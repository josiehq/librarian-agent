#!/usr/bin/env python3
"""
Box 3 Vision MCP Wrapper
Provides vision capabilities via deepseek-ocr + CLIP
"""

import asyncio
import base64
import io
import logging
import time
from typing import Dict, List, Optional

import numpy as np
import requests
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel
from transformers import CLIPModel, CLIPProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Box3 Vision MCP", version="1.0.0")

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
NEMOTRON_OCR_MODEL = "nemotron-ocr-v1"

# CLIP model (loaded on startup)
CLIP_MODEL = None
CLIP_PROCESSOR = None


# =============================================================================
# REQUEST MODELS
# =============================================================================

class VisionScreenRequest(BaseModel):
    """Fast CLIP-based screening request"""
    image_urls: List[str]
    categories: List[str]  # e.g., ["leather wallet", "not relevant"]
    threshold: float = 0.7


class VisionOCRRequest(BaseModel):
    """DeepSeek OCR analysis request"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    question: str = "Describe this image in detail."


class VisionAnalyzeRequest(BaseModel):
    """Full vision analysis (CLIP + OCR)"""
    image_url: str
    categories: List[str]
    ocr_question: str = "Extract all visible text and describe the product."


# =============================================================================
# STARTUP: LOAD CLIP MODEL
# =============================================================================

@app.on_event("startup")
async def load_models():
    """Load CLIP model on startup"""
    global CLIP_MODEL, CLIP_PROCESSOR
    
    logger.info("Loading CLIP model...")
    try:
        CLIP_MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        CLIP_PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        CLIP_MODEL.to(device)
        
        logger.info(f"CLIP model loaded on {device}")
    except Exception as e:
        logger.error(f"Failed to load CLIP: {e}")
        raise


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_image_from_url(url: str) -> Image.Image:
    """Load image from URL"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content))


def load_image_from_base64(b64_string: str) -> Image.Image:
    """Load image from base64 string"""
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data))


def clip_classify(image: Image.Image, categories: List[str]) -> Dict[str, float]:
    """Classify image using CLIP"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Prepare inputs
    inputs = CLIP_PROCESSOR(
        text=categories,
        images=image,
        return_tensors="pt",
        padding=True
    ).to(device)
    
    # Get predictions
    with torch.no_grad():
        outputs = CLIP_MODEL(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]
    
    # Return scores
    return {cat: float(prob) for cat, prob in zip(categories, probs)}


def ollama_vision_inference(image_url: str, question: str) -> str:
    """Call Ollama nemotron-ocr-v1 for vision analysis"""
    url = f"{OLLAMA_HOST}/api/generate"
    
    payload = {
        "model": NEMOTRON_OCR_MODEL,
        "prompt": question,
        "images": [image_url],
        "stream": False
    }
    
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    return result.get("response", "")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models": {
            "clip": CLIP_MODEL is not None,
            "nemotron_ocr": True  # Assume Ollama is running
        }
    }


@app.post("/vision/screen")
async def vision_screen(request: VisionScreenRequest):
    """
    Fast CLIP-based image screening
    
    Use case: Filter 100s of supplier images to find relevant products
    Speed: ~50-100 images/sec on GPU, ~5-10 images/sec on CPU
    """
    start_time = time.time()
    results = []
    
    for image_url in request.image_urls:
        try:
            # Load image
            image = load_image_from_url(image_url)
            
            # Classify with CLIP
            scores = clip_classify(image, request.categories)
            
            # Check if passes threshold
            max_category = max(scores, key=scores.get)
            max_score = scores[max_category]
            
            results.append({
                "image_url": image_url,
                "scores": scores,
                "best_match": max_category,
                "confidence": max_score,
                "passed": max_score >= request.threshold
            })
        
        except Exception as e:
            logger.error(f"Error processing {image_url}: {e}")
            results.append({
                "image_url": image_url,
                "error": str(e),
                "passed": False
            })
    
    elapsed = time.time() - start_time
    passed_count = sum(1 for r in results if r.get("passed"))
    
    return {
        "results": results,
        "summary": {
            "total": len(request.image_urls),
            "passed": passed_count,
            "filtered": len(request.image_urls) - passed_count,
            "elapsed_seconds": elapsed,
            "images_per_second": len(request.image_urls) / elapsed
        }
    }


@app.post("/vision/ocr")
async def vision_ocr(request: VisionOCRRequest):
    """
    Nemotron OCR analysis for detailed product information
    
    Use case: Extract text, analyze product features from images
    Speed: ~5-10 seconds per image on GPU
    """
    start_time = time.time()
    
    try:
        # Determine image source
        if request.image_url:
            image_input = request.image_url
        elif request.image_base64:
            # Save base64 to temp URL (or pass directly to Ollama if supported)
            image_input = f"data:image/jpeg;base64,{request.image_base64}"
        else:
            raise HTTPException(status_code=400, detail="Must provide image_url or image_base64")
        
        # Call Nemotron OCR via Ollama
        response = ollama_vision_inference(image_input, request.question)
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "response": response,
            "elapsed_seconds": elapsed,
            "model": NEMOTRON_OCR_MODEL
        }
    
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/analyze")
async def vision_analyze(request: VisionAnalyzeRequest):
    """
    Full vision analysis: CLIP screening + Nemotron OCR
    
    Use case: Complete product analysis pipeline
    Workflow:
    1. CLIP fast check (< 1 sec)
    2. If relevant, Nemotron OCR detailed analysis (5-10 sec)
    """
    start_time = time.time()
    
    try:
        # Step 1: CLIP screening
        image = load_image_from_url(request.image_url)
        clip_scores = clip_classify(image, request.categories)
        
        best_category = max(clip_scores, key=clip_scores.get)
        clip_confidence = clip_scores[best_category]
        
        # Step 2: Nemotron OCR (only if CLIP passes)
        ocr_response = None
        if clip_confidence >= 0.5:  # Lower threshold for full analysis
            ocr_response = ollama_vision_inference(
                request.image_url,
                request.ocr_question
            )
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "clip_screening": {
                "scores": clip_scores,
                "best_match": best_category,
                "confidence": clip_confidence
            },
            "ocr_analysis": ocr_response,
            "elapsed_seconds": elapsed
        }
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/upload")
async def vision_upload(
    file: UploadFile = File(...),
    question: str = "Describe this image."
):
    """
    Upload image directly for OCR analysis
    
    Use case: Testing, direct image uploads without URLs
    """
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Call OCR
        response = ollama_vision_inference(f"data:image/jpeg;base64,{img_b64}", question)
        
        return {
            "success": True,
            "response": response,
            "filename": file.filename
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Box 3 Vision MCP Wrapper on port 8083")
    uvicorn.run(app, host="0.0.0.0", port=8083)
