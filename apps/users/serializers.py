from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .models import CustomUser

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer): #Not being used. Look for users>models>CustomAccountManager>def create_user
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id','email','first_name','last_name', 'password',
                ]

    def create(self, validated_data):
        #custom logic here
        print('users>serializers.py>class UserCreateSerializer>def create: PRE-SUPER')
        instance = super().create(self,validated_data)
        #custom logic here
        print('users>serializers.py>class UserCreateSerializer>def create: POST-SUPER')
        return instance



from rest_framework import serializers
from djoser.conf import settings
from djoser.compat import get_user_email, get_user_email_field_name

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User # <- Redirects the model to the custom user model (see line 6)
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            # 'roles', #<--ADDED,
            # 'tier', #<--ADDED,
            # 'registration_form', #<--ADDED,
        ) 
        read_only_fields = (settings.LOGIN_FIELD,)

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=["is_active"])
        return super().update(instance, validated_data)

# class CustomUserSerializer(ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id','email','first_name','last_name','start_date','is_staff','is_active','roles','corporateGroupPK']
#         read_only_fields = ['id']
