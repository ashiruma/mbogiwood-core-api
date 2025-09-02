# jobs/urls.py
from django.urls import path
from .views import JobListView

app_name = 'jobs'

urlpatterns = [
    # This now correctly creates the URL /api/jobs/
    path('', JobListView.as_view(), name='job-list'),
]