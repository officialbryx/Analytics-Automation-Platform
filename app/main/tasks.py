import traceback
from django.db import transaction
from django.utils import timezone
from celery import shared_task
from celery.contrib.abortable import AbortableTask
from celery.exceptions import SoftTimeLimitExceeded
from main.models import Requests
from main.process import process

SOFT_TIME_LIMIT = 86400  # 24 hours
HARD_TIME_LIMIT = SOFT_TIME_LIMIT + 1800  # Add 30 minutes to the soft time limit

@shared_task(
    bind=True,
    retry_backoff=True,
    max_retries=5,
    base=AbortableTask,
    soft_time_limit=SOFT_TIME_LIMIT,
    time_limit=HARD_TIME_LIMIT,
)
def process_form_data(
    self,
    report_name,
    tickers,
    statement_type,
    period_type,
    start_year,
    end_year,
    display_unit,
    **kwargs
):
    task_id = self.request.id

    try:
        with transaction.atomic():
            current_request = Requests.objects.get(task_id=task_id)
            current_request.logs = (
                "Task received by Celery Worker and started processing"
            )
            current_request.save()

        results = process(
            task_id,
            report_name,
            tickers,
            statement_type,
            period_type,
            start_year,
            end_year,
            display_unit
        )
        
        # Extract the sheet URL returned by process.py
        sheet_url = results.get("sheet_url")
        
        # Set state to finished and log success
        # Removed 'rows_count' as process.py does not return it in the links dictionary
        _update_ticket_status(
            task_id,
            "finished",
            f"Task Success [{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]\nReport generated successfully.",
            sheet_url=sheet_url,
        )
    except SoftTimeLimitExceeded:
        # Set state to failure and log timeout
        _update_ticket_status(
            task_id,
            "failure",
            f"Task Timeout [{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] \n\n{traceback.format_exc()}",
        )
    except Exception as exc:
        # Set state to retrying if current retry count is less than max retries
        if self.request.retries < self.max_retries:
            _update_ticket_status(
                task_id, "retrying", traceback.format_exc()
            )
        # Else, set state to failed and log the exception
        else:
            _update_ticket_status(
                task_id, "failure", traceback.format_exc()
            )
        # Re-raise the exception to trigger Celery's retry mechanism
        raise self.retry(exc=exc)


def _update_ticket_status(task_id: str, status: str, logs: str, sheet_url: str = None) -> None:
    with transaction.atomic():
        current_request = Requests.objects.get(task_id=task_id)
        current_request.status = status
        current_request.logs = logs
        if sheet_url:
            current_request.sheet_url = sheet_url
        current_request.save()
