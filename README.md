# InsureBot

InsureBot is an AI-powered insurance assistant that enables voice-based interactions, document search, and intelligent responses for insurance-related queries. The system features a Python backend (FastAPI, Rasa, custom services) and a modern React frontend.

## Requirements

* Python 3.10 or higher
* Docker
* SarvamAI API key (for TTS and STT)
* Gemini API key (for LLM)

## Features

* Voice chat assistant with real-time speech-to-text (STT) and text-to-speech (TTS)
* Rasa-based NLP and chat orchestration
* Retrieval-Augmented Generation (RAG) for knowledge base-grounded responses
* End-to-end audio pipeline for seamless voice interaction

## Demo Video

Watch the demo video [here](https://www.example.com/demo-placeholder).

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/HarshitR2004/InsureBot.git
cd InsureBot
```

### 2. Set Up Environment Variables

Create `.env` files in the respective directories:

```
# TTS and STT/.env
YOUR_SARVAM_API_KEY=sk_your_actual_key_here

# Project root .env
GEMINI_API_KEY=your_gemini_key_here
```

### 3. Docker Deployment (Required)

> **Note:** Docker is the only supported method to run InsureBot. All services must be started using Docker containers.

#### Run Weaviate (Vector Database)

```bash
docker run -d --name weaviate -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=100 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH="./data" \
  semitechnologies/weaviate:latest
```

#### Run TTS Service

```bash
cd TTS
docker build -t insurebot-tts .
docker run -d -p 5050:5050 --env-file .env --name tts-service insurebot-tts
```

#### Run ASR Service

```bash
cd ASR
docker build -t insurebot-asr .
docker run -d -p 3001:3001 --name asr-service insurebot-asr
```

Sure! Here's the updated section with the `pip install -r requirements.txt` step added before running the `start.bat` script:

---

#### Start All Services

Install Python dependencies first:

```bash
pip install -r requirements.txt
```

Then use the `start.bat` script from the project root to start all backend services:

```bash
start.bat
```

## Usage

* Ensure all backend services and the frontend are running.
* Open the frontend in your browser.
* Use the voice chat interface to interact with InsureBot.

---








