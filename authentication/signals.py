from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def populate_user_data(request, user, **kwargs):
    if not user.username:
        user.username = user.email.split('@')[0]
    if not user.account_type:
        user.account_type = 'google'
    user.save()