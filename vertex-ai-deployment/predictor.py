import torch
import base64
import os
import logging
from io import BytesIO
from PIL import Image
from diffusers import FluxPipeline
from huggingface_hub import login

class FluxGameAssetsPredictor:
    def __init__(self):
        """Initialize the FLUX.1-dev model with Game Assets LoRA"""
        logging.info("Loading FLUX.1-dev model...")
        
        # Authenticate with HuggingFace if token is provided
        hf_token = os.environ.get("HUGGINGFACE_HUB_TOKEN")
        if hf_token:
            logging.info("HuggingFace token found, logging in...")
            login(token=hf_token)
        else:
            logging.warning("No HuggingFace token found! Gated models may fail to load.")
        
        # Load base FLUX.1-dev model
        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        
        # Load the Game Assets LoRA
        logging.info("Loading Game Assets LoRA...")
        self.pipe.load_lora_weights("gokaygokay/Flux-2D-Game-Assets-LoRA")
        
        # Memory optimizations
        self.pipe.enable_model_cpu_offload()
        
        # Enable memory efficient attention if available
        try:
            self.pipe.enable_xformers_memory_efficient_attention()
            logging.info("XFormers memory efficient attention enabled")
        except Exception as e:
            logging.warning(f"XFormers not available: {e}")
        
        logging.info("Model loaded successfully!")
    
    def predict(self, instances):
        """Generate game assets from prompts"""
        predictions = []
        
        for instance in instances:
            try:
                # Format prompt with GRPZA trigger word
                base_prompt = instance.get('prompt', '')
                formatted_prompt = f"GRPZA, {base_prompt}, white background, game asset"
                
                # Add pixel art style if requested
                if instance.get('pixel_art', True):
                    formatted_prompt += ", pixel art"
                
                # Generate image
                result = self.pipe(
                    prompt=formatted_prompt,
                    height=instance.get('height', 1024),
                    width=instance.get('width', 1024),
                    num_inference_steps=instance.get('num_steps', 28),
                    guidance_scale=instance.get('guidance_scale', 3.5),
                    max_sequence_length=512,
                    generator=torch.Generator("cpu").manual_seed(
                        instance.get('seed', 42)
                    )
                )
                
                image = result.images[0]
                
                # Convert to base64
                buffer = BytesIO()
                image.save(buffer, format="PNG", optimize=True)
                img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                predictions.append({
                    "image": img_b64,
                    "prompt": formatted_prompt,
                    "status": "success"
                })
                
            except Exception as e:
                predictions.append({
                    "error": str(e),
                    "status": "failed"
                })
                logging.error(f"Prediction failed: {e}")
        
        return {"predictions": predictions}

# Global model instance
predictor = None

def load_model():
    """Load model on startup"""
    global predictor
    if predictor is None:
        predictor = FluxGameAssetsPredictor()
    return predictor