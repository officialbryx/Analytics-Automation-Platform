from django.shortcuts import render
from django.core.exceptions import PermissionDenied

# Create your views here.
def login_page(request):
    return render(request, "login.html", {})

def login_error(request):
    raise PermissionDenied()
