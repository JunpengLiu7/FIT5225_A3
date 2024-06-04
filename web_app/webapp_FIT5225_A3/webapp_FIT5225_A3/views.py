from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Record, Communication_Record, Group_Record, Sender, Group_Communication_Record
from .forms import AddRecordForm, AddGroupForm, AddSenderForm, ChatMessageForm, ChatGroupMessageForm
from django import template
import json,random, string, time, requests, re, phonenumbers, copy
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from email_validator import validate_email, EmailNotValidError
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from .pageination import Pagination
from django.http.request import QueryDict


def cognito_login_view(request):
    if request.method == 'POST':
        id_token = request.POST.get('id_token')  # Get the ID token from the frontend
        user = authenticate(request, id_token=id_token)
        if user:
            login(request, user)
            # Redirect or respond accordingly upon successful authentication
            return HttpResponse('Authenticated')
        else:
            # Handle authentication failure
            return HttpResponse('Authentication failed')
    else:
        # Handle GET request if needed
        return HttpResponseNotAllowed(['POST'])
    
   
def home(request):
    
    # load data records
    # records = Record.objects.all()
    group_records = Group_Record.objects.all()
    sender_records = Sender.objects.all()
    
    
    
    # check login
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In")
            return redirect('home')
        else:
            messages.success(request, "Error Login...")
            return redirect('home')
    else:          
        return render(request, 'home.html', {'records': records, 'group_records': group_records, 'sender_records': sender_records})
    
