from django.urls import path
from . import views
from .views import ArtListView

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/profile/", views.index, name="index"),
    path("accounts/register/", views.register, name="register"),
    path("selvin",views.home, name="artwork_list")
]
