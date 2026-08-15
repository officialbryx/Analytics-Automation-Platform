from datetime import datetime
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from google.auth.transport.requests import AuthorizedSession
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def create_sheet(creds, title):
    """
    Creates a Google Sheet with the given title.


    Args:
        creds: The credentials to authenticate the API client.
        title (str): The title of the Google Sheet.


    Returns:
        str: The ID of the created Google Sheet.


    Raises:
        HttpError: If an error occurs during the creation of the Google Sheet.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        spreadsheet = {"properties": {"title": title}}
        spreadsheet = (
            service.spreadsheets()
            .create(body=spreadsheet, fields="spreadsheetId")
            .execute()
        )
        print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
        return spreadsheet.get("spreadsheetId")
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def get_sheet_url(spreadsheet_id):
    """
    Convert spreadsheet_id into spreadsheet link.

    Args:
        spreadsheet_id (str): The ID of the Google Sheet.

    Returns:
        str: The spreadsheet link.
    """
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def update_values(creds, spreadsheet_id, range_name, value_input_option, values):
    """
    Updates the values in a Google Sheet.


    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google Sheet.
        range_name (str): The range of cells to update.
        value_input_option (str): The value input option.
        values (list): The values to update.


    Returns:
        dict: The result of the update operation.


    Raises:
        HttpError: If an error occurs during the update operation.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def move_file_to_folder(creds, file_id, folder_id):
    """
    Moves a file to a specified folder in Google Drive.


    Args:
        creds: The credentials to authenticate the API client.
        file_id (str): The ID of the file to move.
        folder_id (str): The ID of the folder to move the file to.


    Returns:
        list: The IDs of the parents of the moved file.


    Raises:
        HttpError: If an error occurs during the move operation.
    """
    try:
        service = build("drive", "v3", credentials=creds)
        file = service.files().get(fileId=file_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents"))
        file = (
            service.files()
            .update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields="id, parents",
                supportsAllDrives=True,
            )
            .execute()
        )
        return file.get("parents")
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def create_folder(creds, folder_name, parent_folder_id):
    """
    Creates a folder in Google Drive.


    Args:
        creds: The credentials to authenticate the API client.
        folder_name (str): The name of the folder to create.
        parent_folder_id (str): The ID of the parent folder


    Returns:
        str: The ID of the created folder


    Raises:
        HttpError: If an error occurs during the folder creation.
    """
    try:
        service = build("drive", "v3", credentials=creds)
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        }

        folder = (
            service.files()
            .create(body=file_metadata, fields="id", supportsAllDrives=True)
            .execute()
        )
        print(f"Folder ID: {folder.get('id')}")
        return folder.get("id")

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def autofit_columns(creds, spreadsheet_id, sheet_id, start_col=0, end_col=9):
    """
    Auto-fits columns A through I in a Google Sheet.


    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_id (int): The ID of the specific tab.
        start_col (int): Starting column index (0 for A). Default is 0.
        end_col (int): Ending column index (9 for I) Default is 9.

    Returns:
        dict: The result of the batch update operation.

    Raises:
        HttpError: If an error occurs during the operation.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        request_body = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": start_col,
                            "endIndex": end_col,
                        }
                    }
                }
            ]
        }
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute()
        )
        print(f"Auto-fitted columns in sheet {sheet_id}")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def add_column_padding(
    creds, spreadsheet_id, sheet_id, start_col=0, end_col=9, padding=20
):
    """
    Makes the header (first row) bold in a Google Sheet.


    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_id (int): The ID of the specific tab.
        start_col (int): Starting column index (0 for A). Default is 0.
        end_col (int): Ending column index (exclusive, so 9 covers A-I). Default is 9.
        padding (int): The amount of extra space (in pixels) to add to the columns. Default is 20.


    Returns:
        dict: The result of the batch update operation.


    Raises:
        HttpError: If an error occurs during the operation.
    """
    try:
        service = build("sheets", "v4", credentials=creds)

        spreadsheet = (
            service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                fields="sheets.properties,sheets.data.columnMetadata",
            )
            .execute()
        )

        padding_requests = []
        for sheet in spreadsheet.get("sheets", []):
            if sheet["properties"]["sheetId"] == sheet_id:
                sheet_data = sheet.get("data", [])
                if sheet_data:
                    column_metadata = sheet_data[0].get("columnMetadata", [])

                    for col_index in range(
                        start_col, min(end_col, len(column_metadata))
                    ):
                        col_meta = column_metadata[col_index]
                        current_width = col_meta.get("pixelSize", 100)

                        padding_requests.append(
                            {
                                "updateDimensionProperties": {
                                    "range": {
                                        "sheetId": sheet_id,
                                        "dimension": "COLUMNS",
                                        "startIndex": col_index,
                                        "endIndex": col_index + 1,
                                    },
                                    "properties": {
                                        "pixelSize": current_width + padding
                                    },
                                    "fields": "pixelSize",
                                }
                            }
                        )
                break

        if padding_requests:
            result = (
                service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=spreadsheet_id, body={"requests": padding_requests}
                )
                .execute()
            )
            print(f"Added {padding}px padding to columns in sheet {sheet_id}")
            return result
        else:
            print(f"No columns found to add padding in sheet {sheet_id}")
            return None

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def format_header_bold(creds, spreadsheet_id, sheet_id, row_index=0):
    """
    Makes the header (first row) bold in a Google Sheet.


    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_id (int): The ID of the specific tab.
        row_index (int): The row index to format (0 for first row). Default is 0.


    Returns:
        dict: The result of the batch update operation.


    Raises:
        HttpError: If an error occurs during the operation.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        request_body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": True,
                                }
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                }
            ]
        }
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute()
        )
        print(f"Formatted header row as bold in sheet {sheet_id}")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def align_cells_left(creds, spreadsheet_id, sheet_id):
    """
    Aligns all cells to the left in a Google Sheet.


    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_id (int): The ID of the specific tab.


    Returns:
        dict: The result of the batch update operation.


    Raises:
        HttpError: If an error occurs during the operation
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        request_body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                        },
                        "cell": {"userEnteredFormat": {"horizontalAlignment": "LEFT"}},
                        "fields": "userEnteredFormat.horizontalAlignment",
                    }
                }
            ]
        }
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute()
        )
        print(f"Aligned cells to left cells {sheet_id}")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def apply_borders(creds, spreadsheet_id, sheet_id, num_rows, num_cols=9):
    """
    Applies borders to all cells containing data in a Google Sheet.


    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_id (int): The ID of the specific tab.
        num_rows (int): The number of rows with data (including header).
        num_cols (int): The number of columns with data. Default is 9.


    Returns:
        dict: The result of the batch update operation.


    Raises:
        HttpError: If an error occurs during the operation.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        request_body = {
            "requests": [
                {
                    "updateBorders": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": num_rows,
                            "startColumnIndex": 0,
                            "endColumnIndex": num_cols,
                        },
                        "top": {"style": "SOLID", "width": 1},
                        "bottom": {"style": "SOLID", "width": 1},
                        "left": {"style": "SOLID", "width": 1},
                        "right": {"style": "SOLID", "width": 1},
                        "innerHorizontal": {"style": "SOLID", "width": 1},
                        "innerVertical": {"style": "SOLID", "width": 1},
                    }
                }
            ]
        }
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute()
        )
        print(f"Applied borders to {num_rows} rows in sheet {sheet_id}")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


@retry(
    reraise=True,
    retry=retry_if_exception_type(HttpError),
    wait=wait_exponential(),
    stop=stop_after_attempt(5),
)
def populate_tabs(creds, spreadsheet_id, df, tab_with_df):
    """
    Populate the google sheet with multiple tabs (per mobile no).
    Uses the default sheet for the full dataset, then creates additional tabs for split data.




    Args:
        creds: The credentials to authenticate the API client.
        spreadsheet_id (str): The ID of the Google sheet to populate.
        df (pandas.DataFrame): The dataframe to populate in the default sheet.
        tab_with_df(dict): Dictionary with tab names as keys and pandas DataFrames as values.

    Raises:
        HttpError: If an error occurs during the operation.
    """
    try:
        sheets_service = build("sheets", "v4", credentials=creds)

        spreadsheet = (
            sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        default_sheet_id = spreadsheet["sheets"][0]["properties"]["sheetId"]

        rename_request = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": default_sheet_id,
                            "title": "Transaction History",
                        },
                        "fields": "title",
                    }
                }
            ]
        }
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=rename_request
        ).execute()
        logger.info("Renamed default sheet to 'Transaction History'")

        range_name = "Transaction History!A1"
        update_values(
            creds,
            spreadsheet_id,
            range_name,
            "USER_ENTERED",
            [df.columns.tolist()] + df.values.tolist(),
        )
        logger.info(f"Updated default sheet with {len(df)} rows")

        format_header_bold(creds, spreadsheet_id, default_sheet_id)
        align_cells_left(creds, spreadsheet_id, default_sheet_id)
        autofit_columns(creds, spreadsheet_id, default_sheet_id)
        add_column_padding(creds, spreadsheet_id, default_sheet_id)
        apply_borders(creds, spreadsheet_id, default_sheet_id, len(df) + 1)

        for tab_name, tab_df in tab_with_df.items():
            request_body = {
                "requests": [{"addSheet": {"properties": {"title": str(tab_name)}}}]
            }
            response = (
                sheets_service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
                .execute()
            )
            new_sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
            logger.info(f"Created tab: {tab_name}")

            range_name = f"{tab_name}!A1"
            update_values(
                creds,
                spreadsheet_id,
                range_name,
                "USER_ENTERED",
                [tab_df.columns.tolist()] + tab_df.values.tolist(),
            )
            logger.info(f"Updated tab {tab_name} with {len(tab_df)} rows")

            format_header_bold(creds, spreadsheet_id, new_sheet_id)
            align_cells_left(creds, spreadsheet_id, new_sheet_id)
            autofit_columns(creds, spreadsheet_id, new_sheet_id)
            add_column_padding(creds, spreadsheet_id, new_sheet_id)
            apply_borders(creds, spreadsheet_id, new_sheet_id, len(tab_df) + 1)

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error
