import os
from google.cloud import secretmanager


def get_secret_from_gcp(secret_name: str, project_id: str = None) -> str | None:
    """
    Retrieve a secret from GCP Secret Manager.
    
    Args:
        secret_name: Name of the secret in Secret Manager
        project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT env var or saib-ai-playground)
    
    Returns:
        Secret value as string, or None if not found
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        if not project_id:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'saib-ai-playground')
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        return None


def get_hf_token() -> str | None:
    """
    Retrieve HuggingFace token from GCP Secret Manager with fallback to environment variables.
    
    Returns:
        HuggingFace token or None if not found
    """
    # Try GCP Secret Manager first
    token = get_secret_from_gcp("HF_TOKEN")
    if token:
        return token
    
    # Fallback to environment variables
    return os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')