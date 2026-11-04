import base64
import json
import os
from typing import Dict, Any, Tuple
from django.conf import settings
from google.cloud import bigquery
from google.oauth2 import service_account

# Required scopes for BigQuery
BIGQUERY_SCOPES = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform",
]

def get_credentials(scopes=None) -> Tuple[service_account.Credentials, Dict[str, Any]]:
    """
    Retrieves Service Account credentials as both a Credentials object 
    and a raw info dictionary from settings or base64.
    """
    # Option A: base64 env var
    sa_creds_base64 = os.getenv("GOOGLE_SA_CREDS_BASE64")
    if sa_creds_base64:
        decoded_json = base64.b64decode(sa_creds_base64).decode("utf-8")
        info = json.loads(decoded_json)
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=scopes or BIGQUERY_SCOPES
        )
        return creds, info

    # Option B: JSON key file (default: project root)
    creds_path = getattr(
        settings, 
        "GOOGLE_APPLICATION_CREDENTIALS", 
        os.path.join(os.path.dirname(settings.BASE_DIR), "project-aap-google-big-query.json")
    )
    
    # Relative paths start from the project root
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(os.path.dirname(settings.BASE_DIR), creds_path)

    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Google credentials file not found at: {creds_path}")

    with open(creds_path, "r") as f:
        info = json.load(f)

    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=scopes or BIGQUERY_SCOPES
    )
    return creds, info


def get_bigquery_client(location: str = None) -> bigquery.Client:
    """Initializes and returns a BigQuery Client."""
    credentials, info = get_credentials(scopes=BIGQUERY_SCOPES)
    project_id = info.get("project_id")
    
    if not project_id:
        raise ValueError("Could not extract 'project_id' from Google credentials.")

    return bigquery.Client(
        project=project_id, 
        credentials=credentials, 
        location=location
    )
