from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializers for the user objects"""
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        #to add extra fields we use extra_kwargs
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    """Create user function"""
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None) #here none is the default value for pop function
        user = super().update(instance, validated_data) 

        if password:
            user.set_password(password)
            user.save()

        return user  


"""Token authentication"""
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    """Validate and authenticate the user ,attrs returns all the value as dictionary"""
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials, Please check the credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs