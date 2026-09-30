import logging
from datetime import datetime
from main.apps import MainConfig
from main.models import Requests
from main.utils.drive import (
    create_sheet,
    get_sheet_url,
    move_file_to_folder,
    create_folder,
    update_values,
)
from main.utils.queries import QUERY

from main.initialization.google import get_bigquery_client

logger = logging.getLogger(__name__)

google_drive_parent_folder_id = MainConfig.google_drive_parent_folder_id


_bq_client = None

def get_bq_client():
    global _bq_client
    if _bq_client is None:
        _bq_client = get_bigquery_client()
    return _bq_client

drive_credentials = MainConfig.google_creds 


def query_bigquery(tickers, statement_type, period_type, start_year, end_year, display_unit):
    tickers_str = "['" + "','".join(tickers) + "']"
    formatted_query = QUERY.format(
        start_year,
        end_year,
        tickers_str,
        f"'{statement_type}'",
        f"'{period_type}'",
        display_unit
    )
    
    # Use the actual bq_client here
    bq_client = get_bq_client()
    query_job = bq_client.query(formatted_query)
    results = query_job.result()
    
    # Convert results to list of dictionaries
    processed_data = []
    for row in results:
        row_dict = dict(row.items())
        processed_data.append(row_dict)
    
    logger.info(f"Retrieved {len(processed_data)} rows from BigQuery")
    return processed_data


def process(
    task_id,
    report_name,
    tickers,
    statement_type,
    period_type,
    start_year,
    end_year,
    display_unit
):
    current_request = Requests.objects.get(task_id=task_id)

    logger.info(f"Loading data report for {report_name}")
    current_request.save()

    # Query BigQuery
    results = query_bigquery(
        tickers=tickers,
        statement_type=statement_type,
        period_type=period_type,
        start_year=start_year,
        end_year=end_year,
        display_unit=display_unit
    )
    logger.info(f"Successfully loaded {len(results)} rows.")

    # Create a timestamp folder name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{report_name}_{timestamp}"
    
    # Create folder in Google Drive
    logger.info(f"Creating folder: {folder_name}")
    parent_folder_id = google_drive_parent_folder_id
    
    # Pass drive_credentials (or built service object) depending on what your utils expect
    folder_id = create_folder(drive_credentials, folder_name, parent_folder_id)
    
    # Create Google Sheet
    sheet_title = f"{report_name}"
    spreadsheet_id = create_sheet(drive_credentials, sheet_title)
    logger.info(f"Google sheet created: {sheet_title}")
    
    # Format and populate the sheet
    logger.info(f"Populating sheet with {len(results)} rows")
    if results:
        # Get headers from first row
        headers = list(results[0].keys())
        # Convert results to list of lists
        data_rows = [[str(row[header]) if row[header] is not None else "" for header in headers] for row in results]
        # Combine headers and data
        all_data = [headers] + data_rows
        
        # Update the sheet
        update_values(
            creds=drive_credentials,
            spreadsheet_id=spreadsheet_id,
            range_name="Sheet1!A1",
            value_input_option="USER_ENTERED",
            values=all_data
        )
    else:
        logger.warning("No results returned from BigQuery")
        # At least add headers
        update_values(
            creds=drive_credentials,
            spreadsheet_id=spreadsheet_id,
            range_name="Sheet1!A1",
            value_input_option="USER_ENTERED",
            values=[["No data returned from query"]]
        )
    
    # Move sheet to folder
    move_file_to_folder(drive_credentials, spreadsheet_id, folder_id)
    logger.info(f"Moved Google Sheet file: {folder_id}")
    
    # Get the sheet URL
    sheet_url = get_sheet_url(spreadsheet_id)
    logger.info(f"Google Sheet URL Link updated: {sheet_url}")
    
    links = {
        "sheet_url": sheet_url,
        "folder_id": folder_id,
    }

    return links