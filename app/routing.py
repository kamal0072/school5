from django.urls import path
from . import consumers

websocket_urlpatterns=[
    # path("web_s/sync_con/<str:groupsname>/",consumers.MySyncConsumer.as_asgi()),
    path("web_s/async_con/",consumers.MyAsyncConsumer.as_asgi()),
]