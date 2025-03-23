from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/disaster/(?P<report_id>\d+)/$', consumers.DisasterChatConsumer.as_asgi()),
]