from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('insights.core.urls')),
    path('admin/', admin.site.urls),
    path('meetup/', include('insights.meetup.urls')),
]
