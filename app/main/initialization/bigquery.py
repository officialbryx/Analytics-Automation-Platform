import json
from typing import Optional, Union, Dict, Any
from google.cloud import bigquery
from google.oauth2 import service_account


def load_sources(
    credentials_info: Union[str, Dict[str, Any]],
    location: Optional[str] = None
) -> bigquery.Client:
    """
    Loads the BigQuery client using Google API credentials JSON.
    Automatically extracts the project_id from the credentials.

    Args:
        credentials_info (str | dict): Path to service account JSON file, 
                                       or a JSON string, or credentials dictionary.
        location (str, optional): Default location/region for BigQuery jobs (e.g., 'US').

    Returns:
        bigquery.Client: The BigQuery client instance.
    """
    project_id = None

    if isinstance(credentials_info, str):
        if credentials_info.strip().startswith("{"):
            # Credentials passed as a raw JSON string
            info = json.loads(credentials_info)
            project_id = info.get("project_id")
            credentials = service_account.Credentials.from_service_account_info(info)
        else:
            # Credentials passed as a file path
            with open(credentials_info, "r") as f:
                info = json.load(f)
                project_id = info.get("project_id")
            credentials = service_account.Credentials.from_service_account_file(credentials_info)

    elif isinstance(credentials_info, dict):
        # Credentials passed directly as a Python dictionary
        project_id = credentials_info.get("project_id")
        credentials = service_account.Credentials.from_service_account_info(credentials_info)

    else:
        raise ValueError("Invalid credentials_info provided.")

    if not project_id:
        raise ValueError("Could not extract 'project_id' from the provided credentials JSON.")

    return bigquery.Client(project=project_id, credentials=credentials, location=location)