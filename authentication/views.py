from django.shortcuts import render
import logging
logger = logging.getLogger(__name__)
from xinfo_ai.utils import *
from .searilizers import *

User = get_user_model()




class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Get the latest custom_id from the User model
        last_user = User.objects.aggregate(Max('custom_id'))
        last_custom_id = last_user['custom_id__max']

        # Generate the new custom_id.....
        if last_custom_id:
            last_number = int(last_custom_id.split('-')[1])
            new_number = last_number + 1
        else:
            new_number = 10000001
        new_custom_id = f"UID-{new_number:08d}"
        request.data._mutable = True
        request.data['custom_id'] = new_custom_id
        request.data._mutable = False

        response = super().create(request, *args, **kwargs)
        if request.GET.get('api') == 'true':
            return JsonResponse({"status": "User Successfully Created", "data": response.data}, status=status.HTTP_201_CREATED)
        return redirect("/")




class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, "authentication/login.html", {"error": "Invalid Credentials"})

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data.get("user") 

            if user:
                login(request, user)
                ic(user)
                refresh = RefreshToken.for_user(user)
                # Store tokens and user info in session
                request.session["access_token"] = str(refresh.access_token)
                request.session["refresh_token"] = str(refresh)
                request.session["user_info"] = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "account_type": user.account_type,
                    'phone_number': user.phone_number,
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                }
                request.session.modified = True
                ic(request.session)
                if request.GET.get('api') == 'true':
                    return JsonResponse(
                        {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "user": request.session["user_info"],
                        },
                        status=status.HTTP_200_OK,
                    )
                return redirect("/user/dashboard/")
            messages.error(request, "Invalid Credentials")
            return redirect("/auth/user-login", {"error": "Invalid Credentials"})

        except Exception as e:
            if request.GET.get('api') == 'true':
                return JsonResponse(
                    {"error": f"Error during login: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            messages.error(request, f"Error during login: {e}")
            return redirect("/auth/user-login", {"error": f"Error during login: {e}", "error": "Invalid Credentials"})



@csrf_exempt
def user_logout(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    from django.http import JsonResponse
    from rest_framework import status
    from icecream import ic

    ic(request.session)
    ic(dict(request.session))
    ic(request.session.get('user_info'))
    ic(request.session.get('access_token'))
    ic(request.session.get('refresh_token'))

    logout(request)
    request.session.flush()
    ic("logout success")

    # Optional: Redirect to Google logout (client-side recommended instead)
    if request.GET.get('google') == 'true':
        ic("google logout")
        return redirect("https://accounts.google.com/Logout")

    if request.GET.get('api') == 'true':
        return JsonResponse(
            {"status": "success", "message": "Logout successful"},
            status=status.HTTP_200_OK
        )
    
    return redirect("/")





# from dj_rest_auth.registration.views import SocialLoginView
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.models import SocialAccount
# from django.contrib.auth import get_user_model
# from rest_framework.response import Response
# from rest_framework import status

# User = get_user_model()

# class CustomGoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         ic(response)
#         user = request.user
#         ic(user)

#         try:
#             social_account = SocialAccount.objects.filter(user=user, provider="google").first()

#             if social_account:
#                 ic(social_account)
#                 extra_data = social_account.extra_data
#                 ic(extra_data)
#                 user.email = user.email or extra_data.get("email")
#                 user.username = user.username or extra_data.get("name") or extra_data.get("given_name")
#                 user.full_name = getattr(user, "full_name", None) or extra_data.get("name")
#                 user.profile_img = getattr(user, "profile_img", None) or extra_data.get("picture")
#                 if hasattr(user, "account_type") and not user.account_type:
#                     user.account_type = "Google"
#                 user.save()
#                 ic(user)

#         except Exception as e:
#             return Response({"detail": f"Google login data processing error: {e}"}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({
#             "refresh": response.data.get("refresh"),
#             "access": response.data.get("access"),
#             "user": {
#                 "id": user.id,
#                 "email": user.email,
#                 "username": user.username,
#                 "full_name": getattr(user, "full_name", None),
#                 "profile_img": getattr(user, "profile_img", None),
#                 "account_type": getattr(user, "account_type", None),
#                 "is_active": user.is_active,
#                 "is_staff": user.is_staff,
#                 "is_superuser": user.is_superuser
#             }
#         }, status=status.HTTP_200_OK)
