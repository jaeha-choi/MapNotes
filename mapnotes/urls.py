# URL configurations for mapnotes
from django.urls import path

from . import views

# include allows referencing other URLconfs
urlpatterns = [
    path('', views.index, name='index'),
    path('feed', views.feed, name='feed'),
    path('api/data-takeout/all', views.data_takeout_all, name='api/data-takeout/all'),
    path('api/data-takeout/my-notes', views.data_takeout_user, name='api/data-takeout/my-notes'),
    path('user/<int:user_id>/', views.profile, name='profile'),
    path('submit', views.submitNote, name='submit'),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout")
]
