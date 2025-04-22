from django.urls import path
from .views import *


urlpatterns = [
    path("user-register/", UserSignupView.as_view(), name="signup"),
    path("user-login/", UserLoginView.as_view(), name="login"),
    path("user-logout/", user_logout, name="user_logout"),


    # Get all users
    path("user/list", user_list, name = "user_list"),


]