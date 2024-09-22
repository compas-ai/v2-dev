from django.urls import path , include, re_path
from compasaiv2_app.consumers import ChatConsumer
 
# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
   re_path(r"ws/chat/public_room/(?P<chat_community>\w+)/$", ChatConsumer.as_asgi()),
]