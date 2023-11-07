from django.urls import path
from . import views
from .views import GenresListView
from .views import IndexView

urlpatterns = [
    path("", IndexView.as_view()),
    path("accounts/profile/", IndexView.as_view(), name="index"),
    path("accounts/register/", views.register, name="register"),
    path("selvin",views.home, name="artwork_list"),
    path("cano",GenresListView.as_view())
]
