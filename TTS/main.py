import time
import tempfile
import os
import logging
import uvicorn
import mimetypes
import base64
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sarvamai import SarvamAI
from dotenv import load_dotenv
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Speech to Text API", version="1.0.0")

# Pydantic models
class TTSRequest(BaseModel):
    text: str
    lang: str

class TTSResponse(BaseModel):
    message: str
    language: str
    text_length: int

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SarvamAI client
try:
    client = SarvamAI(
        api_subscription_key=os.getenv("YOUR_SARVAM_API_KEY"),
    )
    logger.info("SarvamAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SarvamAI client: {e}")
    raise

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint to check if the API is running"""
    return {"message": "Welcome to the Speech to Text API"}



@app.post("/speak/", response_model=TTSResponse)
async def play_audio(request: TTSRequest):
    """Convert text to speech and return audio file"""
    
    language = {
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN",
    "Tamil": "ta-IN",
    "Urdu": "ur-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Odia": "or-IN",
    "Malayalam": "ml-IN",
    "Punjabi": "pa-IN",
    }

    # Validate language
    if request.lang not in language:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {request.lang}")

    try:
        response = client.text_to_speech.convert(
            text=request.text,
            target_language_code=language[request.lang],
        )
                
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(response.audios[0])
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "X-Language": request.lang,
                "X-Text-Length": str(len(request.text))
            }
        )
        
    except Exception as e:
        logger.error(f"Error during text-to-speech conversion: {e}")
        raise HTTPException(status_code=500, detail="Text-to-speech conversion failed")
    

