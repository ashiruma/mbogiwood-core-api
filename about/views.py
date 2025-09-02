# about/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AboutPageContent, TeamMember
from .serializers import AboutPageSerializer

class AboutPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Assuming you only have one instance of the about page content
        content = AboutPageContent.objects.first()
        team_members = TeamMember.objects.all()
        
        serializer = AboutPageSerializer({
            'mission_statement': content.mission_statement if content else '',
            'our_story': content.our_story if content else '',
            'team_members': team_members
        })
        return Response(serializer.data)