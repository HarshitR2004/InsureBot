import time
import tempfile
import os
import logging
import uvicorn
import mimetypes
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from sarvamai import SarvamAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Audio Transcription API", version="1.0.0")

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

def get_audio_extension(content_type: str, filename: str) -> str:
    """Get appropriate file extension based on content type and filename"""
    # Map content types to extensions
    content_type_map = {
        'audio/wav': '.wav',
        'audio/x-wav': '.wav',
        'audio/wave': '.wav',
        'audio/mpeg': '.mp3',
        'audio/mp3': '.mp3',
        'audio/mpeg3': '.mp3',
        'audio/x-mpeg-3': '.mp3',
        'audio/x-mp3': '.mp3',
        'audio/aac': '.aac',
        'audio/x-aac': '.aac',
        'audio/ogg': '.ogg',
        'audio/opus': '.opus',
        'audio/flac': '.flac',
        'audio/x-flac': '.flac',
        'audio/mp4': '.m4a',
        'audio/x-m4a': '.m4a',
        'audio/webm': '.webm',
        'audio/aiff': '.aiff',
        'audio/x-aiff': '.aiff'
    }
    
    # First try content type
    if content_type in content_type_map:
        return content_type_map[content_type]
    
    # Fallback to filename extension
    if filename:
        _, ext = os.path.splitext(filename.lower())
        if ext in ['.wav', '.mp3', '.aac', '.ogg', '.opus', '.flac', '.m4a', '.webm', '.aiff']:
            return ext
    
    # Default to .wav
    return '.wav'

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    logger.info(f"Received transcription request for file: {file.filename}")
    logger.info(f"Content type: {file.content_type}")
    
    # Check if file is audio
    if not file.content_type.startswith('audio/'):
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Get appropriate file extension
    file_extension = get_audio_extension(file.content_type, file.filename)
    logger.info(f"Using file extension: {file_extension}")
    
    # Create temporary file with correct extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        # Read the uploaded file content
        content = await file.read()
        # Write content to temporary file
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Start transcription timing
        start_time = time.time()
        logger.info(f"Starting transcription for: {temp_file_path}")
        
        # For SarvamAI, we need to open the file in binary mode
        with open(temp_file_path, 'rb') as audio_file:
            response = client.speech_to_text.translate(
                file=audio_file,
                model="saaras:v2.5"
            )
        
        # End timing
        end_time = time.time()
        transcription_time = end_time - start_time
        
        logger.info(f"Transcription completed in {transcription_time:.2f} seconds")
        logger.info(f"Transcription result: {response}")
        
        # Extract the actual transcription text from the response
        transcription_text = ""
        if hasattr(response, 'transcript'):
            transcription_text = response.transcript
        elif isinstance(response, dict) and 'transcript' in response:
            transcription_text = response['transcript']
        else:
            transcription_text = str(response)
        
        return {
            "transcription": transcription_text,
            "duration": round(transcription_time, 2),
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info("Temporary file cleaned up")

@app.get("/")
async def root():
    return {"message": "Audio Transcription API is running", "version": "1.0.0"}




