# community/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/ratings/(?P<film_id>\d+)/$", consumers.RatingConsumer.as_asgi()),
]
