from django.urls import path
from .views import *


urlpatterns = [
    path("register/", register_user, name= "register_user"),
    # path("user/profile/", my_profile, name = "my_profile"),
    # path("user/profile/update/<int:pk>/", my_profile_update, name = "my_profile_update"),

    path("alex-ai/", alex_ai, name= "alex_ai"),

]