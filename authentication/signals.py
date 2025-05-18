from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from user_panel.models import Clients
from user_panel.searilizers import ClientSerializer
from icecream import ic


def generate_next_client_id():
    last_client = Clients.objects.order_by('id').last()
    if not last_client or not last_client.custom_id:
        return 'UID100001'
    last_id = last_client.custom_id.replace('UID', '')
    return f'UID{int(last_id) + 1:06d}'



@receiver(user_logged_in)
def handle_google_login(sender, request, user, **kwargs):
    try:
        social_account = SocialAccount.objects.filter(user=user, provider='google').first()
        ic('1',social_account.extra_data)
        if not social_account:
            return

        # # Check if Clients profile already exists
        # if hasattr(user, 'clients'):
        #     return 

        extra_data = social_account.extra_data
        ic(extra_data)
        email = extra_data.get('email')
        full_name = extra_data.get('name')
        picture = extra_data.get('picture')


        if not user.email:
            user.email = email
        if not user.full_name:
            user.full_name = full_name
        if not user.profile_img:
            user.profile_img = picture
        if not user.account_type:
            user.account_type = "Clients"
        user.save()

        clients_data = {
            "user": user.id,
            "custom_id": generate_next_client_id(),
            "email": email,
            "full_name": full_name,
            "profile_img": picture,            
        }

        clients_serializer = ClientSerializer(data=clients_data)
        if clients_serializer.is_valid():
            clients_serializer.save()
            print("Google login: Clients profile created successfully.")
        else:
            print("Google login: Clients profile validation error:", clients_serializer.errors)
    except Exception as e:
        print(f"[Google Auth] Error in post-login handler: {str(e)}")
