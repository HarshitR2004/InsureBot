# Insurance Chatbot with RAG Integration

An intelligent insurance policy chatbot named "Veena" built with Rasa framework and enhanced with Retrieval-Augmented Generation (RAG) using ChromaDB and Ollama for accurate, document-grounded responses.

## Prerequisites

- **Python 3.10** (Required - Rasa is available in Python 3.10)
- Ollama installed and running locally
- Git (for cloning)

## Quick Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv rasa_env

# Activate environment
# Windows:
rasa_env\Scripts\activate
# macOS/Linux:
source rasa_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Ollama Setup
```bash
# Install Ollama from https://ollama.ai/download
# Pull a lightweight model
ollama pull llama2
# or
ollama pull mistral

# Verify Ollama is running
ollama list
```

### 3. Train the Model
```bash
rasa train
```

## Running the Bot

### Start Action Server (Terminal 1)
```bash
rasa run actions
```

### Start Rasa Shell (Terminal 2)
```bash
rasa shell
```

## System Architecture

### Core Components
- **Rasa Framework**: Intent classification and dialogue management
- **Custom Actions**: RAG-powered response generation
- **ChromaDB**: Vector database for policy document storage
- **Ollama**: Local LLM for response generation
- **LangChain**: Document processing and embeddings

### Data Flow
1. User input → Rasa NLU (intent classification)
2. Intent → Custom Action (RAG system)
3. RAG system → Document retrieval (ChromaDB)
4. Retrieved context → LLM generation (Ollama)
5. Generated response → User

## Project Structure

```
InsureBot/
├── actions/
│   ├── actions.py              # Custom RAG-powered actions
│   ├── llm_rag_utils.py       # RAG system implementation
│   └── document_store/
│       ├── policy_docs/        # Insurance policy documents
│       └── chroma_db/          # Vector database storage
├── data/
│   ├── nlu.yml                # Training data for intents
│   ├── rules.yml              # Conversation rules
│   └── stories.yml            # Conversation flows
├── domain.yml                 # Bot configuration
├── config.yml                 # ML pipeline configuration
├── endpoints.yml              # Action server configuration
└── requirements.txt           # Python dependencies
```

## Key Features

### RAG Integration
- **Document-grounded responses** using actual policy information
- **Vector similarity search** for relevant context retrieval
- **Local LLM processing** with Ollama (no cloud dependencies)
- **35-word response limit** for concise, actionable advice

### Policy-Specific Knowledge
- Exact policy numbers and performance metrics
- Fund allocation and returns data
- Scenario-based customer objection handling
- Growth projections and comparisons

### Conversation Capabilities
- Intent classification for insurance queries
- Context-aware dialogue management
- Fallback handling for unknown inputs
- Multi-turn conversation support

## Test the System

### Test RAG Components
```bash
python test_rag.py
```


## Configuration

### Modify Response Length
Edit `llm_rag_utils.py`:
```python
if len(words) > 35:  # Change word limit
    generated_text = ' '.join(words[:35]) + "..."
```

### Change Ollama Model
Edit `llm_rag_utils.py`:
```python
def call_ollama_llm(self, context_chunks, user_query, model="mistral"):
```

### Add New Documents
1. Drop `.txt` files in `actions/document_store/policy_docs/`
2. Delete `actions/document_store/chroma_db/`
3. Restart action server to rebuild vector store

## Performance Notes

- **Response Time**: 2-3 seconds with local Ollama
- **Memory Usage**: ~2GB for llama2 model  
- **Storage**: ChromaDB ~10MB for policy documents
- **Accuracy**: High precision with document-grounded responses

## Troubleshooting

### Ollama Connection Issues
```bash
# Ensure Ollama is running
ollama serve

# Check available models
ollama list
```

### ChromaDB Errors
```bash
# Reinstall ChromaDB
pip install --upgrade chromadb

# Reset vector store
rm -rf actions/document_store/chroma_db/
```

### Python Version Issues
- Ensure Python 3.10 is installed
- Rasa requires Python 3.10 specifically
- Check version: `python --version`

## Environment Variables

No external API keys required - all processing happens locally with Ollama and ChromaDB.
