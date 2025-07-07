"""
LLM RAG Utilities for Insurance Chatbot
Handles document loading, vector storage with ChromaDB, and Ollama LLM integration
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

# ChromaDB and LangChain imports
import chromadb
from chromadb.config import Settings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.schema import Document

# Ollama integration
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, 
                 docs_path: str = "actions/document_store/policy_docs",
                 chroma_path: str = "actions/document_store/chroma_db",
                 ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize RAG system with document path and vector store
        
        Args:
            docs_path: Path to policy documents
            chroma_path: Path to ChromaDB storage
            ollama_base_url: Ollama API base URL
        """
        self.docs_path = Path(docs_path)
        self.chroma_path = Path(chroma_path)
        self.ollama_base_url = ollama_base_url
        
        # Initialize embeddings model (using a lightweight model)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize vector store
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load existing ChromaDB vector store"""
        try:
            # Create ChromaDB client with persistence
            client = chromadb.PersistentClient(path=str(self.chroma_path))
            
            # Check if we have existing documents
            if self._collection_exists(client, "insurance_docs"):
                logger.info("Loading existing ChromaDB collection")
                self.vector_store = Chroma(
                    client=client,
                    collection_name="insurance_docs",
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Creating new ChromaDB collection")
                self._load_and_embed_documents(client)
                
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def _collection_exists(self, client, collection_name: str) -> bool:
        """Check if collection exists in ChromaDB"""
        try:
            collections = client.list_collections()
            return any(col.name == collection_name for col in collections)
        except:
            return False
    
    def _load_and_embed_documents(self, client):
        """Load documents from docs_path and create embeddings"""
        try:
            # Load all text files from the documents directory
            if not self.docs_path.exists():
                logger.warning(f"Documents path {self.docs_path} does not exist")
                return
            
            # Load documents
            loader = DirectoryLoader(
                str(self.docs_path),
                glob="*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            documents = loader.load()
            
            if not documents:
                logger.warning("No documents found to load")
                return
            
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(texts)} chunks")
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                client=client,
                collection_name="insurance_docs"
            )
            
            logger.info(f"Successfully created vector store with {len(texts)} document chunks")
            
        except Exception as e:
            logger.error(f"Error loading and embedding documents: {e}")
            raise
    
    def query_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector store for relevant document chunks
        
        Args:
            query: User query or intent
            top_k: Number of top chunks to retrieve
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            if not self.vector_store:
                logger.warning("Vector store not initialized")
                return []
            
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'unknown'),
                    'score': score
                })
            
            logger.info(f"Retrieved {len(formatted_results)} relevant chunks for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return []
    
    def call_ollama_llm(self, context_chunks: List[str], user_query: str, 
                       model: str = "llama2") -> str:
        """
        Call Ollama LLM with context and user query
        
        Args:
            context_chunks: Relevant document chunks
            user_query: User's question or intent
            model: Ollama model name
            
        Returns:
            Generated response from LLM
        """
        try:
            # Prepare context
            context = "\n\n".join(context_chunks) if context_chunks else ""
            
            # Create enhanced prompt for insurance agent Veena with specific policy knowledge
            prompt = f"""You are Veena, a knowledgeable insurance advisor from ValuEnable Life Insurance. 

Policy Context (CRITICAL - Use these exact numbers):
- Premium: Rs. 1,00,000 yearly
- Sum Assured: Rs. 10,00,000 
- Fund Value: Rs. 5,53,089
- Premiums Paid: Rs. 4,00,000
- Due Date: 25th September 2024
- Effective Returns: 11.47%
- Current Charges: 3.89% (reducing to 1.61%)

Document Context:
{context}

Customer Question: {user_query}

Instructions:
- Use specific policy numbers when relevant
- Maximum 35 simple English words
- Be friendly and professional like Veena
- Focus on benefits and solutions
- Use exact figures from policy context

Response:"""

            # Prepare API request
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Lower for more consistent responses
                    "top_p": 0.9,
                    "max_tokens": 100
                }
            }
            
            # Make API call to Ollama
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                # Ensure response is within word limit
                words = generated_text.split()
                if len(words) > 35:
                    generated_text = ' '.join(words[:35]) + "..."
                
                logger.info(f"Generated response: {generated_text}")
                return generated_text
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "I apologize, I'm having technical difficulties. Your policy has Rs. 10 lakh sum assured with good returns."
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Please ensure Ollama is running.")
            return "I'm having trouble accessing information. Your Rs. 1 lakh premium policy is performing well with 11.47% returns."
        except Exception as e:
            logger.error(f"Error calling Ollama LLM: {e}")
            return "Let me help you. Your policy shows Rs. 5.53 lakh fund value from Rs. 4 lakh premiums paid."
    
    def get_rag_response(self, user_query: str, intent: str = None) -> str:
        """
        Main RAG function: retrieve relevant docs and generate response
        
        Args:
            user_query: User's question
            intent: Detected intent (optional)
            
        Returns:
            Generated response combining retrieval and generation
        """
        try:
            # Enhance query with intent if provided
            enhanced_query = f"{intent} {user_query}" if intent else user_query
            
            # Retrieve relevant document chunks
            relevant_docs = self.query_documents(enhanced_query, top_k=3)
            
            # Extract content from retrieved docs
            context_chunks = [doc['content'] for doc in relevant_docs]
            
            # Generate response using Ollama
            response = self.call_ollama_llm(context_chunks, user_query)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return "I'm sorry, I'm having technical difficulties. Please contact our customer service team."

# Global RAG system instance
rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or create global RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system

def query_rag_system(user_query: str, intent: str = None) -> str:
    """Convenience function to query RAG system"""
    try:
        rag = get_rag_system()
        return rag.get_rag_response(user_query, intent)
    except Exception as e:
        logger.error(f"Error in query_rag_system: {e}")
        return "I apologize for the inconvenience. Please contact our customer service for help."
