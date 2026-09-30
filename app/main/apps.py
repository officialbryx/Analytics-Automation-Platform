import os
from django.apps import AppConfig
from dotenv import load_dotenv
from main.initialization.google import decode_credentials, load_creds

if os.getenv("BUILD_RUN", False) in [0, "0", False]:
    REQUIRED_ENV_VARS = [
        "GOOGLE_APPLICATION_CREDENTIALS", 
        "GOOGLE_DRIVE_PARENT_FOLDER_ID"
    ]
    IS_REQUIRED_ENV_VARS_COMPLETE = all(
        [env_var in os.environ for env_var in REQUIRED_ENV_VARS]
    )
    if not IS_REQUIRED_ENV_VARS_COMPLETE:
        load_dotenv()

    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_DRIVE_PARENT_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_PARENT_FOLDER_ID")
    GOOGLE_SA_CREDS = os.environ.get("GOOGLE_SA_CREDS")
    decode_credentials(sa_creds=GOOGLE_SA_CREDS)

    class MainConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "main"
        google_application_credentials = GOOGLE_APPLICATION_CREDENTIALS
        google_drive_parent_folder_id = GOOGLE_DRIVE_PARENT_FOLDER_ID
        google_creds = load_creds()

else:
    class MainConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "main"
        google_application_credentials = None
        google_drive_parent_folder_id = None
        google_creds = None