from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API/Payments
    path('payments/', include('payments.urls')),
]
