# about/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AboutPageContent, TeamMember
from .serializers import AboutPageSerializer

class AboutPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        content = AboutPageContent.objects.first()
        team_members = TeamMember.objects.all()
        
        # The serializer data now includes the new stat fields
        serializer_data = {
            'mission_statement': content.mission_statement if content else '',
            'vision_statement': content.vision_statement if content else '',
            'our_story': content.our_story if content else '',
            'our_values': content.our_values if content else '',
            'team_members': team_members,
            'films_featured': content.films_featured if content else 0,
            'professionals_connected': content.professionals_connected if content else '0',
            'countries_reached': content.countries_reached if content else 0,
            'hours_watched': content.hours_watched if content else '0',
        }
        serializer = AboutPageSerializer(instance=serializer_data)
        return Response(serializer.data)