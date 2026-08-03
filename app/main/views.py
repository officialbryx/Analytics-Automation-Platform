from traceback import format_exc
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import logging
from main.forms import RequestForm
from main.tasks import process_form_data
from aap.celery import app
from celery.result import AsyncResult
from main.models import Requests

logger = logging.getLogger(__name__)

# Create your views here.
@login_required(login_url="/")
def form_page(request):
    """View function for the form page."""
    # Check if form is submitted
    if request.method == "POST":
        form = RequestForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            try:
                # Create a new Request object
                with transaction.atomic():
                    request_obj = form.save(commit=False)

                    # Calls the function to process the form data
                    # and sends all form data
                    task = process_form_data.delay(**form.cleaned_data)

                    request_obj.task_id = task.id
                    request_obj.requester_email = request.user.email
                    request_obj.save()

                # Send success message
                messages.success(
                    request,
                    'Form submitted!',
                )
                logger.info(f"Form submitted successfully by {request.user.email}")

                # Redirect to form page
                return redirect("form_page")
            except Exception as error:
                messages.error(request, error)
                logger.error(format_exc())
        else:
            messages.error(
                request,
                'Error: Form did not submit',
            )
            logger.error(
                'Error: Form did not submit',
            )
    else:
        form = RequestForm()

    return render(request, "form.html", {"form": form})

@login_required(login_url="/")
def requests_page(request):
    """View function for the requests page. It renders
    the requests page with the list of requests as a table
    """
    try:
        # [EDIT HERE]
        # Names of the fields of the model to render to the table
        fields_to_render = [
            "status",
            "request_name",
            "information",
            "date",
            "requester_email",
        ]

        # [EDIT HERE]
        # Custom name of the columns to render to the table.
        column_names = {
            "request_name": "Request Name",
            "information": "Information",
            "requester_email": "Requester Email",
        }

        # Check if user is a superuser
        # If so, all Requests are returned
        # Else, only the Requests created by the user are returned
        if request.user.is_superuser:
            requests = Requests.objects.all().order_by("-date")
        else:
            requests = Requests.objects.filter(
                requester_email=request.user.email
            ).order_by("-date")

        # Create context dict for rendering
        context = {
            "requests": requests,
            "fields_to_render": fields_to_render,
            "column_names": {
                field: column_names.get(field, _format_string(field))
                for field in fields_to_render
            },
        }

        return render(request, "requests.html", context)
    except Exception as error:
        messages.error(request, str(error))
        logger.error(format_exc())
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", reverse("main:requests_page"))
        )


def _format_string(value: str) -> str:
    return " ".join(word.capitalize() for word in value.split("_"))


@login_required(login_url="/")
def cancel_celery_task(request, task_id):
    try:
        task = Requests.objects.get(task_id=task_id)

        # Check if task is not running or retrying. If so, return an error message
        if task.status not in ["running", "retrying"]:
            messages.error(request, "Task has already finished or failed")
            logger.info("Task has already finished or failed")
            return HttpResponseRedirect(
                request.META.get("HTTP_REFERER", reverse("main:requests_page"))
            )

        # Cancel celery task
        AsyncResult(id=task_id, app=app).revoke(terminate=True)

        # Update request status and logs
        with transaction.atomic():
            task.status = "cancelled"
            task.logs = (
                f"Task Cancelled [{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]"
            )
            task.save()

        messages.success(request, "Task cancelled successfully")
        logger.info("Task cancelled successfully")
    except Requests.DoesNotExist:
        messages.error(request, "Request not found")
        logger.error(format_exc())
    except Exception as error:
        messages.error(request, str(error))
        logger.error(format_exc())

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("main:requests_page")))


@login_required(login_url="/")
def delete_request(request, task_id):
    try:
        request_obj = Requests.objects.get(task_id=task_id)
        if (
            request_obj.requester_email != request.user.email
            and not request.user.is_superuser
        ):
            messages.error(request, "You do not have permission to delete this")
            logger.error("User does not have permission to delete this")
            return HttpResponseRedirect(
                request.META.get("HTTP_REFERER", reverse("main:requests_page"))
            )

        if request_obj.status in ["retrying", "running"]:
            AsyncResult(id=request_obj.task_id, app=app).revoke(terminate=True)

        with transaction.atomic():
            request_obj.delete()
            messages.success(request, "Deleted successfully!")
            logger.info(f"Deleted '{request_obj.pk}|{request_obj.task_id}' successfully!")

    except Requests.DoesNotExist:
        messages.error(request, "Request not found!")
        logger.error(format_exc())
    except Exception as error:
        messages.error(request, str(error))
        logger.error(format_exc())

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("main:requests_page")))
