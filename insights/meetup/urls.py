from django.urls import path
from meetup import views

urlpatterns = [
    path('start/', views.start, name='meetup-start'),
    path('callback/', views.callback, name='meetup-callback'),
]
