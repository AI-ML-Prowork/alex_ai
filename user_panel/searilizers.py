from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Clients
User = get_user_model()


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'