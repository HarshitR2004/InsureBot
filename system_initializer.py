"""
Standalone System Initialization Service
Runs independently of Rasa actions to prepare all components
"""
import asyncio
import time
import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class SystemInitializer:
    def __init__(self):
        self.initialization_status = {
            "embeddings": {"ready": False, "progress": 0, "message": "Not started"},
            "vector_store": {"ready": False, "progress": 0, "message": "Not started"},
            "llm": {"ready": False, "progress": 0, "message": "Not started"},
            "documents": {"ready": False, "progress": 0, "message": "Not started"},
            "overall_ready": False,
            "total_progress": 0,
            "current_step": "Initializing..."
        }
        self.initialization_complete = False
        
    async def initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            self.initialization_status["embeddings"]["message"] = "Loading AI embeddings model..."
            self.initialization_status["current_step"] = "Loading AI embeddings model..."
            
            # Simulate gradual loading
            for progress in range(0, 101, 5):
                self.initialization_status["embeddings"]["progress"] = progress
                await asyncio.sleep(0.1)
            
            # Actually load embeddings
            from actions.rag_components.embeddings import Embeddings
            embeddings = Embeddings.get_embeddings()
            
            if embeddings is not None:
                self.initialization_status["embeddings"]["ready"] = True
                self.initialization_status["embeddings"]["message"] = "✅ Embeddings model loaded"
                return True
            else:
                raise Exception("Failed to load embeddings")
                
        except Exception as e:
            self.initialization_status["embeddings"]["message"] = f"❌ Error: {str(e)}"
            return False
    
    async def initialize_vector_store(self):
        """Initialize vector database connection"""
        try:
            self.initialization_status["vector_store"]["message"] = "Connecting to knowledge base..."
            self.initialization_status["current_step"] = "Connecting to knowledge base..."
            
            # Simulate connection process
            for progress in range(0, 101, 10):
                self.initialization_status["vector_store"]["progress"] = progress
                await asyncio.sleep(0.05)
            
            # Actually connect to vector store
            from actions.rag_components.vector_store import DatabaseManager
            client = DatabaseManager.get_client()
            
            if client is not None:
                self.initialization_status["vector_store"]["ready"] = True
                self.initialization_status["vector_store"]["message"] = "✅ Vector store connected"
                return True
            else:
                raise Exception("Failed to connect to vector store")
                
        except Exception as e:
            self.initialization_status["vector_store"]["message"] = f"❌ Error: {str(e)}"
            return False
    
    async def initialize_llm(self):
        """Initialize LLM connection"""
        try:
            self.initialization_status["llm"]["message"] = "Initializing language model..."
            self.initialization_status["current_step"] = "Initializing language model..."
            
            # Simulate LLM initialization
            for progress in range(0, 101, 8):
                self.initialization_status["llm"]["progress"] = progress
                await asyncio.sleep(0.08)
            
            # Actually test LLM
            from actions.rag_components.llm import LLM
            llm, response = LLM.get_instance()
            
            if response:
                self.initialization_status["llm"]["ready"] = True
                self.initialization_status["llm"]["message"] = f"✅ LLM initialized successfully: {response}"
                return True
            else:
                raise Exception("Failed to initialize LLM")
                
        except Exception as e:
            self.initialization_status["llm"]["message"] = f"❌ Error: {str(e)}"
            return False
    
    async def check_documents(self):
        """Check if documents are indexed"""
        try:
            self.initialization_status["documents"]["message"] = "Checking document index..."
            self.initialization_status["current_step"] = "Checking document index..."
            
            # Simulate document check
            for progress in range(0, 101, 15):
                self.initialization_status["documents"]["progress"] = progress
                await asyncio.sleep(0.03)
            
            # Check if documents are indexed
            from actions.rag_components.vector_store import DatabaseManager
            tenants = DatabaseManager.list_tenants()
            
            if len(tenants) > 0:
                self.initialization_status["documents"]["ready"] = True
                self.initialization_status["documents"]["message"] = f"✅ {len(tenants)} document collections ready"
                return True
            else:
                self.initialization_status["documents"]["message"] = "⚠️ No documents indexed"
                return True  # Not critical for basic operation
                
        except Exception as e:
            self.initialization_status["documents"]["message"] = f"❌ Error: {str(e)}"
            return False
    
    async def run_initialization(self):
        """Run complete system initialization"""
        print("🚀 Starting system initialization...")
        
        # Initialize components in parallel for faster startup
        tasks = [
            self.initialize_embeddings(),
            self.initialize_vector_store(),
            self.initialize_llm(),
            self.check_documents()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate overall progress
        ready_count = sum(1 for status in self.initialization_status.values() 
                         if isinstance(status, dict) and status.get("ready", False))
        
        self.initialization_status["total_progress"] = (ready_count / 4) * 100
        self.initialization_status["overall_ready"] = ready_count >= 3  # Allow 1 failure
        
        if self.initialization_status["overall_ready"]:
            self.initialization_status["current_step"] = "✅ System ready!"
            self.initialization_status["total_progress"] = 100  # Ensure 100% when ready
            print("✅ System initialization complete!")
        else:
            self.initialization_status["current_step"] = "⚠️ System partially ready"
            print("⚠️ System initialization completed with some issues")
        
        self.initialization_complete = True
        return self.initialization_status

# Global initializer instance
system_initializer = SystemInitializer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run initialization
    print("🌟 Starting InsureBot System Initializer...")
    
    # Run initialization in background
    asyncio.create_task(system_initializer.run_initialization())
    
    yield
    
    # Shutdown
    print("🛑 Shutting down System Initializer...")

# FastAPI app for health checks
app = FastAPI(
    title="InsureBot System Initializer",
    description="Standalone system initialization and health monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "System Initializer",
        "timestamp": time.time()
    }

@app.get("/status")
async def get_system_status():
    """Get detailed system initialization status"""
    return {
        "initialization_status": system_initializer.initialization_status,
        "initialization_complete": system_initializer.initialization_complete,
        "timestamp": time.time()
    }

@app.get("/ready")
async def check_system_ready():
    """Check if system is ready for use"""
    if system_initializer.initialization_status["overall_ready"]:
        return {
            "ready": True,
            "message": "System is ready for use",
            "progress": system_initializer.initialization_status["total_progress"]
        }
    else:
        return {
            "ready": False,
            "message": system_initializer.initialization_status["current_step"],
            "progress": system_initializer.initialization_status["total_progress"]
        }

@app.post("/reinitialize")
async def reinitialize_system():
    """Force reinitialize the system"""
    system_initializer.initialization_complete = False
    system_initializer.initialization_status = {
        "embeddings": {"ready": False, "progress": 0, "message": "Restarting..."},
        "vector_store": {"ready": False, "progress": 0, "message": "Restarting..."},
        "llm": {"ready": False, "progress": 0, "message": "Restarting..."},
        "documents": {"ready": False, "progress": 0, "message": "Restarting..."},
        "overall_ready": False,
        "total_progress": 0,
        "current_step": "Reinitializing..."
    }
    
    # Run initialization
    asyncio.create_task(system_initializer.run_initialization())
    
    return {"message": "Reinitialization started"}

if __name__ == "__main__":
    print("🚀 Starting InsureBot System Initializer on port 8000...")
    uvicorn.run(
        "system_initializer:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
