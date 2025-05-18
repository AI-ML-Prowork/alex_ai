from django.urls import path
from .views import *


urlpatterns = [
    path("user-register/", UserSignupView.as_view(), name="signup"),
    path("user-login", UserLoginView.as_view(), name="login"),
    path("user-logout/", user_logout, name="user_logout"),

    # Google login
    # path('google-login/', CustomGoogleLogin.as_view(), name='google_login'),

]