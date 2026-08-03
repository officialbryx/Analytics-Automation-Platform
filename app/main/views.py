from traceback import format_exc
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import logging
from .forms import RequestForm
from .tasks import process_form_data

logger = logging.getLogger(__name__)

# Create your views here.
# @login_required(login_url="/users/login/")
def main_page(request):
    """View function for the main page."""
    # Check if form is submitted
    if request.method == "POST":
        form = RequestForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            try:
                # Create a new Request object
                with transaction.atomic():
                    ticket = form.save(commit=False)

                    # Calls the function to process the form data
                    # and sends all form data
                    task = process_form_data.delay(**form.cleaned_data)

                    ticket.task_id = task.id
                    ticket.requester_email = request.user.email
                    ticket.save()

                # Send success message
                messages.success(
                    request,
                    'Form submitted!',
                )
                logger.info(f"Form submitted successfully by {request.user.email}")

                # Redirect to main page
                return redirect("main_page")
            except Exception as error:
                messages.error(request, error)
                logger.error(format_exc())
        # For invalid forms, display error message
        else:
            messages.error(
                request,
                'Error: Form did not submit',
            )
            logger.error(
                'Error: Form did not submit',
            )
    # If form is not submitted, render the main page instead
    else:
        form = RequestForm()

    return render(request, "main.html", {"form": form})
