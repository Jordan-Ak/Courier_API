from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.validators import UniqueValidator

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from accounts.services import validate_password




class UserCreateSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required = True,
                            validators=[UniqueValidator(queryset=get_user_model().objects.all())])
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    phone_no =PhoneNumberField(required = True,
                                validators=[UniqueValidator(queryset=get_user_model().objects.all())])
    password = serializers.CharField(required = True,
                                validators = [validate_password])
    password2 = serializers.CharField(required = True)

    date_created = serializers.DateTimeField(format = "%H:%M, %d-%m-%Y", read_only = True,)


    def validate(self, attrs) -> str:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(_('Passwords do not match'))
        
        return attrs

class UserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'phone_no','is_verified_email', 'on_news')

class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    on_news = serializers.BooleanField()


#class UserDeleteSerializer(serializers.Serializer):
 #   first_name = serializers.CharField()
 #   last_name = serializers.CharField()
  #  on_news = serializers.BooleanField()

class UserAdminListSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'email','first_name','last_name','phone_no','is_verified_email','on_news')

class UserAdminDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = '__all__'

class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField(validators = [validate_password])
    password2 = serializers.CharField()

    def validate(self, attrs) -> str:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(_('Passwords do not match'))
        
        return attrs

class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserPasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(validators = [validate_password])
    new_password2 = serializers.CharField()

    def validate(self, attrs) -> str:
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(_('Passwords do not match'))
        
        return attrs