from django.urls import path
from . import views
from .views import GenresListView
from .views import IndexView

urlpatterns = [
    path("", IndexView.as_view()),
    path("en/<path:path>/", views.detail_artwork, name="Artwork detail"),
    path("artist/<slug:slug>/", views.artist_detail, name="artist_detail"),
    path("accounts/profile/", IndexView.as_view(), name="index"),
    path("accounts/register/", views.register, name="register"),
    path("collections/", views.collections, name="collections"),
    path("collection_list/", views.collection_list, name="collection_list"),
    path("collection/add", views.collection_add, name="collection_add"),
    path("collection/modify/<int:id>/", views.collection_modify, name="collection_modify")
]
