import re
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from chat.serializers import MessageSerializer, UserSerializerWithToken
from .models import Message
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



@api_view(['POST'])
def register_view(request):

    data = request.data

    try:
        user = User.objects.create(
            username = data['username'],
            email = data['email'],
            password = make_password(data['password'])
        )
        serializer = UserSerializerWithToken(user, many=False)

        return Response(serializer.data)

    except:
        message = {"User with this email already exists"}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_messages(request, user_id):

    if user_id == request.user.id:
        if user_id is None:
            return Response('user_id is not specified')

        messages = (Message.objects.filter(reciever_id=user_id) | Message.objects.filter(sender_id=user_id))
        serializer = MessageSerializer(messages, many=True, context={'request': request})

        for message in messages:
            message.is_read = True
            message.save()

        return Response(serializer.data)

    else:
        return Response({"You are not allowed to access"})





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signle_message(request, message_id):
    
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({"message_id is not valid"})

    serializer = MessageSerializer(message, many=False, context={'request': request})

    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_unread_message(request, user_id):
    if user_id == request.user.id:
        messages = Message.objects.filter(reciever_id=user_id, is_read = False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})

        for message in messages:
           message.is_read = True
           message.save()

        return Response(serializer.data)

    else:
        return Response({"You are not allowed to access"})
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):  

    serializer = MessageSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def message_delete(request, message_id):
    try:
        message = Message.objects.get(id=message_id)

    except Message.DoesNotExist:
        return Response({"message_id was not found"})

    if request.user.id in [message.reciever_id, message.sender_id]:
 
        message.delete()
        return Response({'message had deleted'})

    else:
        return Response({"You are not allowed to delete this message"})




