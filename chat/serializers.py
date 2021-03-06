from django.contrib.auth.models import User
from rest_framework import serializers
from chat.models import Message
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'is_staff']

    # def get_isAdmin(self, obj):
    #     return obj.is_staff


class UserSerializerWithToken(UserSerializer):
    token =  serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id','username','email','is_staff' ,'token']
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())
    reciever = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['sender', 'reciever', 'message', 'timestamp']
