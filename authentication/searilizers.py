from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

User = get_user_model()



class UserSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "password", "password2", "account_type"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)





class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username",  "phone_number", "account_type"]  # Exclude password and other creation-only fields
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def update(self, instance, validated_data):
        """Custom update method to update user details."""
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.account_type = validated_data.get("account_type", instance.account_type)
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = User.objects.filter(email=email).first()

            if user:
                if not user.check_password(password) or not user.is_active:
                    msg = "Check your credentials"
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = "User does not exist please register yourself"
                raise serializers.ValidationError(msg, code="authorization")

        else:
            msg = "Must include 'email' and 'password'"
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
    
    


# CustomUser Manager



    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'