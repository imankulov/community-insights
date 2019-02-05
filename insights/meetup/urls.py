from django.urls import path
from insights.meetup import views

urlpatterns = [
    path('start/', views.start, name='meetup-start'),
    path('callback/', views.callback, name='meetup-callback'),
]
