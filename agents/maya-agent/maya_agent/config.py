import os
from .utils import get_hf_token

# GCP Configuration
GCP_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'saib-ai-playground')
GCP_REGION = os.getenv('GCP_REGION', 'us-central1')

# Model Configuration
MODEL_NAME = "gemini-2.5-pro"  # For Game Creator (high quality code generation)
FAST_MODEL_NAME = "gemini-2.5-flash"  # For Orchestrator, Publisher, Asset Generator (speed)
SUPER_FAST_MODEL_NAME = "gemini-2.5-flash-lite"  # Ultra-fast model for all agents

# HuggingFace Configuration
HF_TOKEN = get_hf_token()
HF_MODEL_NAME = "gokaygokay/Flux-2D-Game-Assets-LoRA"

# Asset Generation Settings
ASSET_WIDTH = 512
ASSET_HEIGHT = 512
GRPZA_TRIGGER = "GRPZA"