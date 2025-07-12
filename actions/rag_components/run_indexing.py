

import sys
import os
from pathlib import Path

# Add the rag_components directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from indexing import DocumentIndexer

def main():
    """
    Run the document indexing process for insurance policy documents.
    """
    print("Starting InsureBot Document Indexing Process")
    print("=" * 60)
    
    # Initialize the document indexer
    indexer = DocumentIndexer(
        chunk_size=1000,      
        chunk_overlap=200     
    )
    
    base_dir = Path(__file__).parent.parent
    policy_docs_dir = base_dir / "document_store" / "policy_docs"
    
    print(f"Looking for documents in: {policy_docs_dir}")
    
    # Check if directory exists
    if not policy_docs_dir.exists():
        print(f"Error: Directory not found: {policy_docs_dir}")
        print("Please ensure the policy documents directory exists.")
        return
    
    # List files to be processed
    txt_files = list(policy_docs_dir.glob("*.txt"))
    if not txt_files:
        print("No .txt files found in the policy documents directory.")
        return
    
    print(f"Found {len(txt_files)} document(s) to process:")
    for file_path in txt_files:
        print(f"   - {file_path.name}")
    print()
    
    # Start indexing process
    print("Starting indexing process...")
    results = indexer.index_directory(
        directory_path=str(policy_docs_dir),
        file_extensions=['.txt']
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("INDEXING RESULTS")
    print("=" * 60)
    
    successful_files = []
    failed_files = []
    
    for file_path, success in results.items():
        filename = Path(file_path).name
        if success:
            print(f"SUCCESS: {filename}")
            successful_files.append(file_path)
        else:
            print(f"FAILED:  {filename}")
            failed_files.append(file_path)
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"   Total files processed: {len(results)}")
    print(f"   Successful: {len(successful_files)}")
    print(f"   Failed: {len(failed_files)}")
    
    # Show single collection used
    if successful_files:
        print(f"\nSINGLE COLLECTION:")
        print(f"   - All documents indexed into: insurance_documents")
    
    # Test search if any files were successfully indexed
    if successful_files:
        print("\n" + "=" * 60)
        print("TESTING SEARCH FUNCTIONALITY")
        print("=" * 60)
        
        test_queries = [
            "What are my policy benefits?",
            "How do I make a claim?",
            "What is covered under this policy?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            search_results = indexer.search_collection(
                query=query,
                k=2
            )
            
            if search_results:
                for i, doc in enumerate(search_results, 1):
                    source = doc.metadata.get('source_file', 'Unknown')
                    content_preview = doc.page_content[:150].replace('\n', ' ')
                    print(f"  {i}. [{source}] {content_preview}...")
            else:
                print("  No results found.")
    
    print("\n" + "=" * 60)
    print("Indexing process completed!")
    print("=" * 60)
    
    if successful_files:
        print("Your documents are now indexed and ready for RAG queries.")
        print("You can now use the vector database for your insurance chatbot.")
    else:
        print("No documents were successfully indexed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nIndexing process interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your Weaviate server and try again.")
