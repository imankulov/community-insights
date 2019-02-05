from django.urls import path
from insights.core import views

urlpatterns = [
    path('', views.index, name='core-index'),
]
