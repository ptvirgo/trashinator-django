from django.conf.urls import url
from . import views

app_name = "trashinator"

urlpatterns = [
    url("^$", views.TrashElmView.as_view(), name="trash"),
    url("settings/", views.TrashProfileView.as_view(), name="profile")
]
