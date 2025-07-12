from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate
from embeddings import Embeddings


class DatabaseManager:
    _instance = None  # Single vector store instance
    
    # Fixed Weaviate connection settings
    WEAVIATE_HOST = 'localhost'
    WEAVIATE_PORT = 8080
    COLLECTION_NAME = 'insurance_documents'  # Single collection for all documents
    
    @classmethod
    def get_collection(cls):
        if cls._instance is None:
            print("Connecting to Weaviate...")
            client = weaviate.connect_to_local(host=cls.WEAVIATE_HOST, port=cls.WEAVIATE_PORT)
            try:
                client.is_ready()
                print("Connected to Weaviate.")
            except Exception as e:
                print(f"Could not connect to Weaviate: {e}")
                raise
            embeddings = Embeddings.get_embeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
            cls._instance = WeaviateVectorStore(
                embedding=embeddings,
                client=client,
                index_name=cls.COLLECTION_NAME,
                text_key="page_content"
            )
            print("Weaviate vector store ready.")
        return cls._instance
    
if __name__ == "__main__":
    try:
        vector_store = DatabaseManager.get_collection()
        print("Vector store instance created successfully.")
    except Exception as e:
        print(f"Error creating vector store instance: {e}")
