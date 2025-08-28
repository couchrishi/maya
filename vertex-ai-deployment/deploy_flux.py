#!/usr/bin/env python3
"""
Deploy Flux Game Assets model to Vertex AI with secure HF token
"""

import logging
from google.cloud import aiplatform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_flux_model():
    PROJECT_ID = "saib-ai-playground"
    REGION = "us-central1"
    
    # HuggingFace token (you'll need to provide this)
    HF_TOKEN = "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"
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Container URI (make sure build completed first)
    container_uri = "gcr.io/saib-ai-playground/flux-game-assets:latest"
    
    logger.info("Creating Flux Game Assets model...")
    
    # Create model with HF token as environment variable
    model = aiplatform.Model.upload(
        display_name="flux-game-assets",
        artifact_uri=None,
        serving_container_image_uri=container_uri,
        serving_container_predict_route="/predict",
        serving_container_health_route="/health",
        serving_container_ports=[8080],
        serving_container_environment_variables={
            "HUGGINGFACE_HUB_TOKEN": HF_TOKEN
        },
        description="FLUX.1-dev + Game Assets LoRA for 2D game asset generation"
    )
    
    logger.info(f"Model created: {model.resource_name}")
    model_id = model.name.split('/')[-1]
    
    # Create endpoint
    logger.info("Creating endpoint...")
    endpoint = aiplatform.Endpoint.create(
        display_name="flux-game-assets-endpoint",
        description="Endpoint for FLUX Game Assets model"
    )
    
    logger.info(f"Endpoint created: {endpoint.resource_name}")
    endpoint_id = endpoint.name.split('/')[-1]
    
    # Deploy model to endpoint with T4 GPU
    logger.info("Deploying model to endpoint...")
    deployed_model = endpoint.deploy(
        model=model,
        deployed_model_display_name="flux-game-assets-deployment",
        machine_type="n1-standard-4",
        accelerator_type="NVIDIA_TESLA_T4",
        accelerator_count=1,
        min_replica_count=1,  # No auto-scaling to 0 as requested
        max_replica_count=3
    )
    
    print("\n" + "="*60)
    print("FLUX GAME ASSETS DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"Model ID: {model_id}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"Machine Type: n1-standard-4 + T4 GPU")
    print(f"Scaling: 1-3 replicas (no scale to zero)")
    print(f"Health Check: /health")
    print(f"Prediction: /predict")
    print("="*60)
    
    # Test payload example
    print("\nTest with this payload:")
    print("""
{
  "instances": [{
    "prompt": "magical sword with blue flames",
    "pixel_art": true,
    "height": 1024,
    "width": 1024,
    "num_steps": 28,
    "guidance_scale": 3.5,
    "seed": 42
  }]
}
""")
    
    return model, endpoint

if __name__ == "__main__":
    deploy_flux_model()