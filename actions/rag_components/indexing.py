import os
import sys
from pathlib import Path
from typing import List


project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from actions.rag_components.vector_store import DatabaseManager

class DocumentIndexer:
    """
    Indexes documents into Weaviate vector database.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the document indexer.
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _load_document(self, file_path: str) -> List[Document]:
        """
        Load a document from file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return documents
        except Exception as e:
            return []
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using RecursiveCharacterTextSplitter.
    
        """
        try:
            chunked_docs = self.text_splitter.split_documents(documents)
            return chunked_docs
        except Exception as e:
            return []
    
    def _create_tennant_name(self, file_path: str) -> str:
        """
        Create a collection name from file path.
        
        """
        # Get filename without extension
        filename = Path(file_path).stem
        
        # Clean the name for Weaviate (alphanumeric and underscore only)
        collection_name = "".join(c if c.isalnum() or c == "_" else "_" for c in filename)
        
        # Ensure it starts with a letter
        if not collection_name[0].isalpha():
            collection_name = "doc_" + collection_name
            
        return collection_name.lower()
    
    def index_directory(self, path: str):
        """
        Index all documents in a directory with multi-tenancy.
        
        """
        files = list(Path(path).glob("*.txt"))
        
        if not files:
            return Exception("No .txt files found in the directory.")

        try:
            for file_path in files:
                # Load the document
                documents = self._load_document(str(file_path))
                
                if not documents:
                    continue
                
                # Split the document into chunks
                chunked_docs = self._split_documents(documents)
                
                if not chunked_docs:
                    continue
                
                # Create tenant name from file path
                tenant_name = self._create_tennant_name(str(file_path))
                
                # Add documents to the specific tenant
                DatabaseManager.add_documents_to_tenant(tenant_name, chunked_docs)
                
                print(f"Indexed {len(chunked_docs)} chunks from {file_path.name} into tenant '{tenant_name}'")
            
        except Exception as e:
            return Exception(f"Indexing failed: {e}")
            
if __name__ == "__main__":
    # Example usage
    indexer = DocumentIndexer(chunk_size=1000, chunk_overlap=200)
    indexer.index_directory("actions\document_store\policy_docs")
