#!/usr/bin/env python3
"""
FastAPI server for OmniVoice TTS.

Provides REST API endpoints for voice conversion with:
- Text input
- Reference audio for voice cloning
- Language selection
- Returns converted audio

Usage:
    python -m omnivoice.api --model k2-fsa/OmniVoice --port 8000 --share
"""

import argparse
import base64
import io
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

import torch
import torchaudio
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from omnivoice import OmniVoice, OmniVoiceGenerationConfig


def get_best_device():
    """Auto-detect the best available device: CUDA > MPS > CPU."""
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class VoiceConversionRequest(BaseModel):
    """Request model for voice conversion."""
    text: str
    language: Optional[str] = None
    num_step: int = 32
    guidance_scale: float = 2.0
    denoise: bool = True
    speed: float = 1.0
    duration: Optional[float] = None


class VoiceConversionResponse(BaseModel):
    """Response model for voice conversion."""
    audio_base64: str
    sample_rate: int
    message: str


app = FastAPI(
    title="OmniVoice API",
    description="API for text-to-speech voice conversion using OmniVoice model",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Optional[OmniVoice] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "OmniVoice API is running",
        "docs": "/docs",
        "endpoints": {
            "voice_conversion": "/api/v1/voice-conversion",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.post("/api/v1/voice-conversion", response_model=VoiceConversionResponse)
async def voice_conversion(
    text: str = Form(..., description="Text to synthesize"),
    language: Optional[str] = Form(None, description="Language (e.g., 'English', 'Portuguese', 'Auto')"),
    ref_audio: Optional[UploadFile] = File(None, description="Reference audio file for voice cloning (optional, uses voice.wav if not provided)"),
    ref_text: Optional[str] = Form(None, description="Transcript of reference audio (optional)"),
    num_step: int = Form(32, description="Number of inference steps (4-64)"),
    guidance_scale: float = Form(2.0, description="Guidance scale (0.0-4.0)"),
    denoise: bool = Form(True, description="Apply denoising"),
    speed: float = Form(1.0, description="Speed factor (0.5-1.5)"),
    duration: Optional[float] = Form(None, description="Fixed duration in seconds"),
):
    """
    Convert text to speech with voice cloning.
    
    **Parameters:**
    - **text**: The text to synthesize (required)
    - **language**: Target language (optional, auto-detected if not provided)
    - **ref_audio**: Reference audio file for voice cloning (optional, uses voice.wav if not provided)
    - **ref_text**: Transcript of reference audio (optional, auto-transcribed if not provided)
    - **num_step**: Number of inference steps, higher = better quality (default: 32)
    - **guidance_scale**: CFG scale (default: 2.0)
    - **denoise**: Enable denoising (default: true)
    - **speed**: Speech speed multiplier (default: 1.0)
    - **duration**: Fixed output duration in seconds (optional)
    
    **Returns:**
    - **audio_base64**: Base64-encoded WAV audio
    - **sample_rate**: Audio sample rate
    - **message**: Status message
    
    **Note:** If ref_audio is not provided, the default voice.wav file will be used.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        gen_config = OmniVoiceGenerationConfig(
            num_step=int(num_step),
            guidance_scale=float(guidance_scale),
            denoise=bool(denoise),
            preprocess_prompt=True,
            postprocess_output=True,
        )
        
        lang = language if (language and language.lower() != "auto") else None
        
        kwargs = {
            "text": text.strip(),
            "language": lang,
            "generation_config": gen_config,
        }
        
        if speed != 1.0:
            kwargs["speed"] = float(speed)
        if duration is not None and duration > 0:
            kwargs["duration"] = float(duration)
        
        default_voice_path = Path(__file__).parent.parent / "voice.wav"
        
        if ref_audio is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(ref_audio.filename).suffix) as tmp_file:
                content = await ref_audio.read()
                tmp_file.write(content)
                tmp_audio_path = tmp_file.name
            
            try:
                kwargs["voice_clone_prompt"] = model.create_voice_clone_prompt(
                    ref_audio=tmp_audio_path,
                    ref_text=ref_text if ref_text else None,
                )
            finally:
                Path(tmp_audio_path).unlink(missing_ok=True)
        elif default_voice_path.exists():
            kwargs["voice_clone_prompt"] = model.create_voice_clone_prompt(
                ref_audio=str(default_voice_path),
                ref_text=ref_text if ref_text else None,
            )
        else:
            logging.warning(f"Default voice file not found at {default_voice_path}, generating without voice cloning")
        
        audio = model.generate(**kwargs)
        
        waveform = audio[0].squeeze(0)
        
        buffer = io.BytesIO()
        torchaudio.save(
            buffer,
            waveform.unsqueeze(0),
            model.sampling_rate,
            format="wav"
        )
        buffer.seek(0)
        
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return VoiceConversionResponse(
            audio_base64=audio_base64,
            sample_rate=model.sampling_rate,
            message="Audio generated successfully"
        )
        
    except Exception as e:
        logging.error(f"Error during voice conversion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {type(e).__name__}: {str(e)}")


def load_env_config():
    """Load configuration from .env file."""
    load_dotenv()
    
    config = {
        "model": os.getenv("MODEL_PATH", "k2-fsa/OmniVoice"),
        "device": os.getenv("DEVICE", None) or None,
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8001")),
        "share": os.getenv("SHARE", "false").lower() in ("true", "1", "yes"),
    }
    return config


def build_parser() -> argparse.ArgumentParser:
    env_config = load_env_config()
    
    parser = argparse.ArgumentParser(
        prog="omnivoice-api",
        description="Launch FastAPI server for OmniVoice.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default=env_config["model"],
        help=f"Model checkpoint path or HuggingFace repo id. (default from .env: {env_config['model']})",
    )
    parser.add_argument(
        "--device",
        default=env_config["device"],
        help="Device to use. Auto-detected if not specified."
    )
    parser.add_argument(
        "--host",
        default=env_config["host"],
        help=f"Server host (default from .env: {env_config['host']})."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=env_config["port"],
        help=f"Server port (default from .env: {env_config['port']})."
    )
    parser.add_argument(
        "--share",
        action="store_true",
        default=env_config["share"],
        help="Create public link using ngrok."
    )
    return parser


def main(argv=None) -> int:
    global model
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )
    
    parser = build_parser()
    args = parser.parse_args(argv)
    
    device = args.device or get_best_device()
    
    checkpoint = args.model
    if not checkpoint:
        parser.print_help()
        return 0
    
    logging.info(f"Loading model from {checkpoint}, device={device} ...")
    model = OmniVoice.from_pretrained(
        checkpoint,
        device_map=device,
        dtype=torch.float16,
        load_asr=True,
    )
    logging.info("Model loaded successfully.")
    
    if args.share:
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(args.port)
            logging.info(f"Public URL: {public_url}")
            logging.info(f"API Docs: {public_url}/docs")
        except ImportError:
            logging.warning("pyngrok not installed. Install with: pip install pyngrok")
            logging.info("Running without public URL.")
        except Exception as e:
            logging.warning(f"Could not create public URL: {e}")
            logging.info("Running without public URL.")
    
    logging.info(f"Starting server at http://{args.host}:{args.port}")
    logging.info(f"API Documentation: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
