import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .models import FilmRating
from films.models import Film


class RatingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.film_id = self.scope["url_route"]["kwargs"]["film_id"]
        self.group_name = f"film_{self.film_id}_ratings"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        rating = int(data.get("rating", 0))
        user = self.scope.get("user")

        if isinstance(user, AnonymousUser) or not (1 <= rating <= 5):
            return  # ignore invalid or anonymous ratings

        await self.save_rating(user, self.film_id, rating)

        # Broadcast updated ratings to all connected clients
        avg, count = await self.get_rating_summary(self.film_id)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "rating_update", "average": avg, "count": count}
        )

    async def rating_update(self, event):
        """Send new rating data to WebSocket clients"""
        await self.send(text_data=json.dumps({
            "average_rating": event["average"],
            "rating_count": event["count"],
        }))

    @database_sync_to_async
    def save_rating(self, user, film_id, rating):
        film = Film.objects.get(id=film_id)
        FilmRating.objects.update_or_create(
            user=user,
            film=film,
            defaults={"rating": rating}
        )

    @database_sync_to_async
    def get_rating_summary(self, film_id):
        film = Film.objects.get(id=film_id)
        ratings = film.community_ratings.all()  # uses related_name from models.py
        if ratings.exists():
            avg = round(sum(r.rating for r in ratings) / ratings.count(), 2)
            return avg, ratings.count()
        return None, 0
