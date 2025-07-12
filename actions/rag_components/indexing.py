import os
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.schema import Document
from vector_store import DatabaseManager
from embeddings import Embeddings

class DocumentIndexer:
    """
    Indexes documents into Weaviate vector database using LangChain.
    All documents are stored in a single collection with metadata differentiation.
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
    
    def load_document(self, file_path: str) -> List[Document]:
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
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using RecursiveCharacterTextSplitter.
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of chunked Document objects
        """
        try:
            chunked_docs = self.text_splitter.split_documents(documents)
            return chunked_docs
        except Exception as e:
            return []
    
    def create_collection_name(self, file_path: str) -> str:
        """
        Create a collection name from file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Clean collection name for Weaviate
        """
        # Get filename without extension
        filename = Path(file_path).stem
        
        # Clean the name for Weaviate (alphanumeric and underscore only)
        collection_name = "".join(c if c.isalnum() or c == "_" else "_" for c in filename)
        
        # Ensure it starts with a letter
        if not collection_name[0].isalpha():
            collection_name = "doc_" + collection_name
            
        return collection_name.lower()
    
    def index_document(self, file_path: str) -> bool:
        """
        Index a single document into Weaviate single collection.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load document
            documents = self.load_document(file_path)
            if not documents:
                return False
            
            # Split into chunks
            chunked_docs = self.split_documents(documents)
            if not chunked_docs:
                return False
            
            # Create document identifier
            document_name = self.create_collection_name(file_path)
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunked_docs):
                chunk.metadata.update({
                    'source_file': os.path.basename(file_path),
                    'file_path': file_path,
                    'document_name': document_name,
                    'chunk_index': i,
                    'total_chunks': len(chunked_docs)
                })
            
            # Get the single vector store instance
            vector_store = DatabaseManager.get_collection()
            
            # Add documents to vector store
            texts = [doc.page_content for doc in chunked_docs]
            metadatas = [doc.metadata for doc in chunked_docs]
            
            vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            
            return True
            
        except Exception as e:
            return False
    
    def index_directory(self, directory_path: str, file_extensions: List[str] = None) -> Dict[str, bool]:
        """
        Index all documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            file_extensions: List of file extensions to process (default: ['.txt'])
            
        Returns:
            Dictionary mapping file paths to success status
        """
        if file_extensions is None:
            file_extensions = ['.txt']
        
        directory = Path(directory_path)
        if not directory.exists():
            return {}
        
        results = {}
        
        # Find all files with specified extensions
        for ext in file_extensions:
            for file_path in directory.glob(f"**/*{ext}"):
                if file_path.is_file():
                    success = self.index_document(str(file_path))
                    results[str(file_path)] = success
        
        return results
    
    def search_collection(self, query: str, document_name: str = None, k: int = 5) -> List[Document]:
        """
        Search for similar documents in the single collection.
        
        Args:
            query: Search query
            document_name: Optional document name to filter by
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            vector_store = DatabaseManager.get_collection()
            
            if document_name:
                # Search with metadata filter for specific document
                results = vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter={'document_name': document_name}
                )
            else:
                # Search across all documents
                results = vector_store.similarity_search(query, k=k)
            
            return results
            
        except Exception as e:
            return []

def main():
    """
    Main function to demonstrate document indexing.
    """
    # Initialize indexer
    indexer = DocumentIndexer(
        chunk_size=800,
        chunk_overlap=100
    )
    
    # Define document directory
    docs_directory = "../document_store/policy_docs"
    
    # Index all text files in the directory
    results = indexer.index_directory(
        directory_path=docs_directory,
        file_extensions=['.txt']
    )
    
    # Print results
    print("\nINDEXING RESULTS")
    print("="*50)
    
    for file_path, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        filename = os.path.basename(file_path)
        print(f"{status}: {filename}")
    
    # Example search
    if results:
        print("\nEXAMPLE SEARCH")
        print("="*50)
        
        # Search across all documents in single collection
        search_results = indexer.search_collection(
            query="What are the policy benefits?",
            k=3
        )
        
        print(f"Search results from insurance documents collection:")
        for i, doc in enumerate(search_results, 1):
            print(f"\n{i}. Source: {doc.metadata.get('source_file', 'Unknown')}")
            print(f"   Content: {doc.page_content[:200]}...")

if __name__ == "__main__":
    main()