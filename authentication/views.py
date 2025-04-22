from django.shortcuts import render
import logging
logger = logging.getLogger(__name__)
from xinfo_ai.utils import *
from .searilizers import *

User = get_user_model()


def user_login(request):
    return render(request, "authentication/login.html") 


def user_register(request):
    return render(request, "authentication/signup.html") 



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
    authentication_classes = []  # Disable CSRF check for this view

    @csrf_exempt  # Exempt this view from CSRF verification
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, email=email, password=password)

            if user:
                # Log the user in (this attaches user to request.user)
                login(request, user)
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
                request.session.modified = True  # Ensure session is saved
                if request.GET.get('api') == 'true':
                    return JsonResponse(
                        {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "user": request.session["user_info"],
                        },
                        status=status.HTTP_200_OK,
                    )
                return redirect("/admin-panel/dashboard/")
            messages.error(request, "Invalid Credentials")
            return redirect("/", {"error": "Invalid Credentials"})

        except Exception as e:
            messages.error(request, f"Error during login: {e}")
            return redirect("/")


@csrf_exempt
def user_logout(request):
    ic(request.session)
    ic(dict(request.session))
    ic(request.session.get('user_info'))
    ic(request.session.get('access_token'))
    ic(request.session.get('refresh_token'))
    logout(request)
    request.session.flush()
    ic("logout success")
    if request.GET.get('api') == 'true':
        return JsonResponse({"status": "success", "message": "Logout successful"}, status=status.HTTP_200_OK)
    return redirect("/")



@csrf_exempt
def user_list(request):
    clients = Clients.objects.all()
    clients_data = ClientSerializer(clients, many=True).data
    if request.GET.get('api') == 'true':
        return JsonResponse({"status": "success", "data": clients_data}, status=status.HTTP_200_OK)
    return TemplateResponse(request, "admin_panel/all_users.html", {"clients": clients_data})