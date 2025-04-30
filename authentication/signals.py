from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def populate_user_data(request, user, **kwargs):
    # For example, assign default values
    user.username = user.email.split('@')[0]
    user.account_type = 'google'
    user.save()
