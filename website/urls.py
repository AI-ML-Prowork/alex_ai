from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('1', index1, name='index1'),



]