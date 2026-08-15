import base64
import json
import os
from typing import Dict, Any, Union, Tuple
from django.conf import settings
from google.cloud import bigquery
from google.oauth2 import service_account

# Unified Scopes for Drive & Sheets
DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

# Required scopes for BigQuery
BIGQUERY_SCOPES = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform",
]

# Cache for loaded credentials
_cached_credentials = None

def get_credentials(scopes=None) -> Tuple[service_account.Credentials, Dict[str, Any]]:
    """
    Retrieves Service Account credentials as both a Credentials object 
    and a raw info dictionary from settings or base64.
    """
    # 1. Option A: From Base64 Env Var (In-Memory, safest for Celery)
    if hasattr(settings, "GOOGLE_SA_CREDS_BASE64") and settings.GOOGLE_SA_CREDS_BASE64:
        decoded_json = base64.b64decode(settings.GOOGLE_SA_CREDS_BASE64).decode("utf-8")
        info = json.loads(decoded_json)
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=scopes or DRIVE_SCOPES
        )
        return creds, info

    # 2. Option B: From JSON File using Absolute Path
    # Default to parent directory of BASE_DIR (project root)
    creds_path = getattr(
        settings, 
        "GOOGLE_APPLICATION_CREDENTIALS", 
        os.path.join(os.path.dirname(settings.BASE_DIR), "project-aap-google-big-query.json")
    )
    
    # If path is relative, make it absolute from project root
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(os.path.dirname(settings.BASE_DIR), creds_path)

    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Google credentials file not found at: {creds_path}")

    with open(creds_path, "r") as f:
        info = json.load(f)

    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=scopes or DRIVE_SCOPES
    )
    return creds, info


def get_bigquery_client(location: str = None) -> bigquery.Client:
    """Initializes and returns a BigQuery Client."""
    # Ensure BigQuery specifically gets BigQuery scopes, not Drive Scopes
    credentials, info = get_credentials(scopes=BIGQUERY_SCOPES)
    project_id = info.get("project_id")
    
    if not project_id:
        raise ValueError("Could not extract 'project_id' from Google credentials.")

    return bigquery.Client(
        project=project_id, 
        credentials=credentials, 
        location=location
    )


def get_drive_credentials() -> service_account.Credentials:
    """Returns credentials formatted specifically for Google Drive/Sheets API."""
    credentials, _ = get_credentials(scopes=DRIVE_SCOPES)
    return credentials


def decode_credentials(sa_creds: str = None) -> None:
    """
    Decodes base64-encoded service account credentials and writes to file.
    This is used during Docker initialization.
    """
    if not sa_creds:
        sa_creds = os.getenv("GOOGLE_SA_CREDS_BASE64")
    
    if not sa_creds:
        return
    
    try:
        decoded_json = base64.b64decode(sa_creds).decode("utf-8")
        # Use current directory as fallback if settings not yet loaded
        try:
            # Write to project root (parent of BASE_DIR)
            base_dir = os.path.dirname(settings.BASE_DIR)
        except:
            # Fallback: go up from current file location to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        creds_path = os.path.join(base_dir, "project-aap-google-big-query.json")
        
        with open(creds_path, "w") as f:
            f.write(decoded_json)
    except Exception as e:
        print(f"Warning: Could not decode credentials: {e}")


def load_creds() -> service_account.Credentials:
    """
    Loads and caches Google credentials at startup.
    Returns the credentials object for Drive/Sheets access.
    """
    global _cached_credentials
    
    if _cached_credentials is None:
        try:
            _cached_credentials, _ = get_credentials(scopes=DRIVE_SCOPES)
        except Exception as e:
            print(f"Warning: Could not load credentials at startup: {e}")
            _cached_credentials = None
    
    return _cached_credentials