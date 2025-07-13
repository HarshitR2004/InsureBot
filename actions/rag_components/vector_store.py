from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate
import os
import sys
from typing import Dict, Optional
from weaviate.classes.tenants import Tenant
from weaviate.classes.config import Configure


project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from actions.rag_components.embeddings import Embeddings

class DatabaseManager:
    _client: Optional[weaviate.WeaviateClient] = None
    _vector_stores: Dict[str, WeaviateVectorStore] = {}
    _collection_initialized = False

    COLLECTION_NAME = "InsuranceDocs"

    @classmethod
    def get_client(cls):
        """Get or create the single Weaviate client"""
        if cls._client is None:
            print("Connecting to Weaviate...")
            cls._client = weaviate.connect_to_local()
            print("Connected to Weaviate.")
        return cls._client

    @classmethod
    def ensure_collection_exists(cls):
        """Ensure the InsuranceDocs collection exists with multi-tenancy enabled"""
        if cls._collection_initialized:
            return
            
        client = cls.get_client()
        
        try:
            # Check if collection exists
            if not client.collections.exists(cls.COLLECTION_NAME):
                print(f"Creating collection '{cls.COLLECTION_NAME}' with multi-tenancy enabled...")
                
                # Create collection with multi-tenancy enabled
                client.collections.create(
                    name=cls.COLLECTION_NAME,
                    multi_tenancy_config=Configure.multi_tenancy(enabled=True)
                )
                print(f"Collection '{cls.COLLECTION_NAME}' created successfully.")
                
                # Create a dummy tenant to avoid null type errors
                cls._create_dummy_tenant()
            else:
                print(f"Collection '{cls.COLLECTION_NAME}' already exists.")
                
            cls._collection_initialized = True
            
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
            raise

    @classmethod
    def _create_dummy_tenant(cls):
        """Create a dummy tenant to avoid null type errors"""
        try:
            client = cls.get_client()
            collection = client.collections.get(cls.COLLECTION_NAME)
            
            dummy_tenant_name = "dummy_example_tenant"
            print(f"Creating dummy tenant: {dummy_tenant_name}")
            
            # Check if dummy tenant already exists using correct v4 API
            try:
                existing_tenants = []
                tenant_objects = collection.tenants.get()
                for tenant_obj in tenant_objects:
                    if hasattr(tenant_obj, 'name'):
                        existing_tenants.append(tenant_obj.name)
                    else:
                        # Handle string objects directly
                        existing_tenants.append(str(tenant_obj))
                print(f"Found existing tenants: {existing_tenants}")
            except Exception as e:
                print(f"Could not retrieve existing tenants: {e}")
                existing_tenants = []
            
            if dummy_tenant_name not in existing_tenants:
                collection.tenants.create([Tenant(name=dummy_tenant_name)])
                print(f"Dummy tenant '{dummy_tenant_name}' created successfully.")
            else:
                print(f"Dummy tenant '{dummy_tenant_name}' already exists.")
                
        except Exception as e:
            print(f"Failed to create dummy tenant: {e}")
            raise

    @classmethod
    def get_vector_store(cls, tenant_name: str):
        """Get vector store instance for the specified tenant"""
        # Ensure collection exists first
        cls.ensure_collection_exists()
        
        if tenant_name not in cls._vector_stores:
            client = cls.get_client()
            
            # Ensure the tenant exists
            cls.ensure_tenant_exists(tenant_name)
            
            # Create the vector store for this tenant using from_documents approach
            # We'll store it temporarily and use add_documents later
            cls._vector_stores[tenant_name] = WeaviateVectorStore(
                client=client,
                index_name=cls.COLLECTION_NAME,
                text_key="text",
                embedding=Embeddings.get_embeddings()
            )
            print(f"Initialized vector store for tenant: {tenant_name}")
            
        return cls._vector_stores[tenant_name]

    @classmethod
    def ensure_tenant_exists(cls, tenant_name: str):
        """Create the tenant in Weaviate if it doesn't already exist"""
        try:
            client = cls.get_client()
            collection = client.collections.get(cls.COLLECTION_NAME)
            print(f"Ensuring tenant '{tenant_name}' exists in collection '{cls.COLLECTION_NAME}'...")
            
            # Get existing tenants properly using v4 API
            try:
                existing_tenants = []
                tenant_objects = collection.tenants.get()
                for tenant_obj in tenant_objects:
                    if hasattr(tenant_obj, 'name'):
                        existing_tenants.append(tenant_obj.name)
                    else:
                        # Handle string objects directly
                        existing_tenants.append(str(tenant_obj))
                print(f"Existing tenants: {existing_tenants}")
            except Exception as e:
                print(f"Could not retrieve existing tenants: {e}")
                existing_tenants = []

            if tenant_name not in existing_tenants:
                collection.tenants.create([Tenant(name=tenant_name)])
                print(f"Tenant '{tenant_name}' created.")
            else:
                print(f"Tenant '{tenant_name}' already exists.")
        except Exception as e:
            print(f"Failed to ensure tenant '{tenant_name}': {e}")
            raise

    @classmethod
    def add_documents_to_tenant(cls, tenant_name: str, documents: list):
        """Add documents to a specific tenant"""
        try:
            client = cls.get_client()
            cls.ensure_collection_exists()
            cls.ensure_tenant_exists(tenant_name)
            
            # Use from_documents with tenant parameter
            vector_store = WeaviateVectorStore.from_documents(
                documents=documents,
                embedding=Embeddings.get_embeddings(),
                client=client,
                index_name=cls.COLLECTION_NAME,
                tenant=tenant_name
            )
            
            print(f"Added {len(documents)} documents to tenant '{tenant_name}'")
            
            # Store the vector store for later use
            cls._vector_stores[tenant_name] = vector_store
            
        except Exception as e:
            print(f"Failed to add documents to tenant '{tenant_name}': {e}")
            raise

    @classmethod
    def search_tenant(cls, tenant_name: str, query: str, k: int = 5):
        """Search within a specific tenant using direct Weaviate client"""
        try:
            client = cls.get_client()
            cls.ensure_collection_exists()
            cls.ensure_tenant_exists(tenant_name)
            
            # Get collection and perform search with tenant context
            collection = client.collections.get(cls.COLLECTION_NAME)
            
            # Use tenant-specific collection for search
            tenant_collection = collection.with_tenant(tenant_name)
            
            # Get embeddings for the query
            embeddings = Embeddings.get_embeddings()
            query_vector = embeddings.embed_query(query)
            
            # Perform vector search
            response = tenant_collection.query.near_vector(
                near_vector=query_vector,
                limit=k,
                return_metadata=weaviate.classes.query.MetadataQuery(score=True)
            )
            
            # Convert results to LangChain Document format
            from langchain.schema import Document
            results = []
            for obj in response.objects:
                doc = Document(
                    page_content=obj.properties.get('text', ''),
                    metadata={
                        'id': str(obj.uuid),
                        'tenant': tenant_name,
                        'score': obj.metadata.score if obj.metadata else None,
                        **obj.properties
                    }
                )
                results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"Failed to search tenant '{tenant_name}': {e}")
            return []

    @classmethod
    def list_tenants(cls):
        """List all tenants in the collection"""
        try:
            client = cls.get_client()
            collection = client.collections.get(cls.COLLECTION_NAME)
            
            tenant_names = []
            tenant_objects = collection.tenants.get()
            for tenant_obj in tenant_objects:
                if hasattr(tenant_obj, 'name'):
                    tenant_names.append(tenant_obj.name)
                else:
                    # Handle string objects directly
                    tenant_names.append(str(tenant_obj))
            
            return tenant_names
            
        except Exception as e:
            print(f"Error listing tenants: {e}")
            return []

    @classmethod
    def delete_collection(cls):
        """Delete the entire collection and reset state"""
        try:
            client = cls.get_client()
            if client.collections.exists(cls.COLLECTION_NAME):
                client.collections.delete(cls.COLLECTION_NAME)
                print(f"Deleted collection: {cls.COLLECTION_NAME}")
            
            # Reset state
            cls._vector_stores = {}
            cls._collection_initialized = False
            
        except Exception as e:
            print(f"Error deleting collection: {e}")
            raise

    @classmethod
    def close_client(cls):
        """Close the Weaviate client connection"""
        try:
            if cls._client:
                cls._client.close()
                cls._client = None
                cls._vector_stores = {}
                cls._collection_initialized = False
                print("Weaviate client connection closed")
        except Exception as e:
            print(f"Error closing client: {e}")


if __name__ == "__main__":
    # Example usage with dummy tenant creation
    tenant_name = "example_tenant"
    client = weaviate.connect_to_local()
    
    # Create dummy tenant first
    DatabaseManager.create_dummy_tenant(client)
    
    # Then create the actual tenant
    print(f"Vector store for tenant '{tenant_name}' is ready.")