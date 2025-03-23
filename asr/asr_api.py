import os
import sys
print(sys.executable)
print(sys.version)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from dotenv import load_dotenv
import logging
import tempfile

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler("asr_api.log")])

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Load model and processor at startup
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/wav2vec2-large-960h")  # Default model if no .env provided
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME).to(device)

# Pydantic model for response
class ASRResponse(BaseModel):
    transcription: str
    duration: str

@app.get("/ping")
async def ping():
    """Simple endpoint to check the service is running."""
    return {"status": "ok"}

@app.post("/asr", response_model=ASRResponse)
async def transcribe(file: UploadFile = File(...)):
    """API endpoint for transcribing audio files."""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided.")
    
    try:
        # Save uploaded file to a temporary location
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_filepath = tmp.name

        # Load the audio (assuming it is a 16kHz sampled MP3)
        waveform, sample_rate = torchaudio.load(tmp_filepath)
        if sample_rate != 16000:
            # Resample to 16kHz if needed
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)
            sample_rate = 16000

        # Calculate duration in seconds
        duration = round(waveform.shape[1] / sample_rate, 1)

        # Convert waveform to mono if needed
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Prepare input for model
        input_values = processor(waveform.squeeze().numpy(), sampling_rate=sample_rate, return_tensors="pt").input_values.to(device)
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0].strip()

        # Clean up: remove the temporary file
        os.remove(tmp_filepath)

        logger.info(f"Transcription completed for {file.filename}. Duration: {duration}s")

        return ASRResponse(transcription=transcription, duration=str(duration))

    except Exception as e:
        # Ensure file is deleted even if error occurs
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
