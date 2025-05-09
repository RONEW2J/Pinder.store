from django.urls import path
from . import views

app_name = 'actions'

urlpatterns = [
    path('swipe/', views.SwipeActionView.as_view(), name='swipe-action'),
]