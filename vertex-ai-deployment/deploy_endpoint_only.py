#!/usr/bin/env python3
"""
Deploy existing Flux model to existing endpoint
"""

import logging
from google.cloud import aiplatform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_to_existing_endpoint():
    PROJECT_ID = "saib-ai-playground"
    REGION = "us-central1"
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Use existing model and endpoint IDs
    model_id = "2718919632164487168"  # Latest flux-game-assets model
    endpoint_id = "4899814139997716480"  # Existing endpoint
    
    logger.info(f"Getting existing model: {model_id}")
    model = aiplatform.Model(model_name=f"projects/{PROJECT_ID}/locations/{REGION}/models/{model_id}")
    
    logger.info(f"Getting existing endpoint: {endpoint_id}")
    endpoint = aiplatform.Endpoint(endpoint_name=f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{endpoint_id}")
    
    # Deploy model to endpoint with T4 GPU
    logger.info("Deploying model to endpoint...")
    try:
        deployed_model = endpoint.deploy(
            model=model,
            deployed_model_display_name="flux-game-assets-deployment",
            machine_type="n1-standard-4",
            accelerator_type="NVIDIA_TESLA_T4",
            accelerator_count=1,
            min_replica_count=1,
            max_replica_count=3
        )
        
        print("\n" + "="*60)
        print("FLUX GAME ASSETS DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"Model ID: {model_id}")
        print(f"Endpoint ID: {endpoint_id}")
        print(f"Machine Type: n1-standard-4 + T4 GPU")
        print(f"Scaling: 1-3 replicas")
        print("="*60)
        
        return deployed_model
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise

if __name__ == "__main__":
    deploy_to_existing_endpoint()