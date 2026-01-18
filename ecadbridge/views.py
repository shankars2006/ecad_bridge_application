from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.urls import reverse
from urllib.parse import urlencode
import requests
from jose import jwt
from django.conf import settings

# 404 handler
def custom_page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

