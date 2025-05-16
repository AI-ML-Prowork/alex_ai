from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from icecream import ic
from django.db.models import Max
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.template.response import TemplateResponse
from django.db import transaction,IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json,os,logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import send_mail
from .openai_utils import *
from .storage import *

User = get_user_model()

from authentication.models import CustomUser
from user_panel.models import Clients
from authentication.searilizers import UserSerializer


from authentication.searilizers import UserSignupSerializer
from user_panel.searilizers import ClientSerializer
