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
def process_form_data(self, **kwargs):
    try:
        # Run the process function and obtain the results
        results = process(**kwargs)

        # Set state to finished and logs to success if process succeeds
        _update_ticket_status(
            process_form_data.request.id,
            "finished",
            f"Task Success [{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]",
        )
    except SoftTimeLimitExceeded:
        # Set state to failure and logs timeout
        _update_ticket_status(
            process_form_data.request.id,
            "failure",
            f"Task Timeout [{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] \n\n{traceback.format_exc()}",
        )
    except Exception as exc:
        # Set state to retrying if current retry count is less than max retries
        if self.request.retries < self.max_retries:
            _update_ticket_status(
                process_form_data.request.id, "retrying", traceback.format_exc()
            )
        # Else, set state to failed and logs to exception
        else:
            _update_ticket_status(
                process_form_data.request.id, "failure", traceback.format_exc()
            )
        raise self.retry(exc=exc)


def _update_ticket_status(task_id: str, status: str, logs: str) -> None:
    with transaction.atomic():
        current_request = Requests.objects.get(task_id=task_id)
        current_request.status = status
        current_request.logs = logs
        current_request.save()
