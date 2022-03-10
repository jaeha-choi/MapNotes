# URL configurations for mapnotes
from django.urls import path

from . import views

# include allows referencing other URLconfs
urlpatterns = [
    path('', views.index, name='index'),
    path('feed', views.feed, name='feed'),
    path('user/<int:user_id>/', views.profile, name='profile'),
    path('submit', views.submit, name='submit'),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout")
]