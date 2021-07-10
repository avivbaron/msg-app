from django.contrib.auth import authenticate, login
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Message
from .forms import SignUpForm
import json

@csrf_exempt
def do_login(request):
    if request.user.is_authenticated:
        return HttpResponse('{"user is connected"}')
    if request.method == "POST":
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponse('{"error": "User does not exist"}')
        return HttpResponse('{"user is connected"}')

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('{"registered"}')
    return HttpResponse('{"not registered"}')



@csrf_exempt
def get_all_messages(request, user_id=None):
    """
    List all required messages.
    """
    if request.method == 'GET':
        messages = (Message.objects.filter(receiver_id=user_id) | Message.objects.filter(sender_id=user_id))
        response_json = {}
        for message in messages:
            message.is_read = True
            message.save()
            response_json[message.id] = {
                'receiver_id': message.receiver_id,
                'sender_id': message.sender_id,
                'message_content': message.message,
            }
        return HttpResponse(json.dumps(response_json), content_type="application/json")


@csrf_exempt
def get_signle_message(request, message_id):
    if request.method == 'GET':
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return HttpResponse({"message_id is not valid"})

        response_json = {
            'receiver_id': message.receiver_id,
            'receiver': message.receiver.username,
            'sender_id': message.sender_id,
            'sender': message.sender.username,
            'message_content': message.message,
        }
        return HttpResponse(json.dumps(response_json), content_type='application/json')
    return HttpResponse({"message error"})


@csrf_exempt
def get_all_unread_message(request, user_id):
    if request.method == 'GET':
        messages = Message.objects.filter(receiver_id=user_id, is_read = False)
        response_json = {}
        for message in messages:
           message.is_read = True
           message.save()
           response_json[message.id] = {
               'receiver_id': message.receiver_id,
               'sender_id': message.sender_id,
               'message_content': message.message,
           }
        return HttpResponse(json.dumps(response_json), content_type="application/json")
    

@csrf_exempt
def send_message(request):    
    if request.method == 'POST':
        data = JSONParser().parse(request)
        receiver = User.objects.filter(username=data['receiver']).first()
        sender = User.objects.filter(username=data['sender']).first()
        msg = Message(receiver=receiver, sender=sender, message=data['message'])
        msg.save()
        return HttpResponse({'message sent'} )


@csrf_exempt
def message_delete(request, message_id, user_id):
     if request.method == 'DELETE':
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return HttpResponse({"message_id was not found"})

        if user_id in [message.receiver_id, message.sender_id]:
            message.delete()
            return HttpResponse({"message has deleted"})
        return HttpResponse({"message has not been deleted due to user_id mismatch"})




