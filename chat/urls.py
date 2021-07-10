from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', login, name='login'),
    path('api/messages/<int:user_id>/', get_all_messages, name='get-all-messages'),
    path('api/messages/single/<int:message_id>/', get_signle_message, name='get-single-message'),
    path('api/messages/unread/<int:user_id>/', get_all_unread_message, name='get-all-unread-message'),
    path('api/messages/', send_message, name='send-message'),
    path('api/messages/delete/<int:message_id>/<int:user_id>/', message_delete, name='message-delete'),
    path('logout/', LogoutView.as_view(),  name='logout'),
    path('register/', register_view, name='register'),
]
