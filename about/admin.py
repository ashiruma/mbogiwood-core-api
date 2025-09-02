# about/admin.py
from django.contrib import admin
from .models import AboutPageContent, TeamMember

admin.site.register(AboutPageContent)
admin.site.register(TeamMember)