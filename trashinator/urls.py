from django.conf.urls import url
from . import views

app_name = "trashinator"

urlpatterns = [
    url("settings/", views.TrashProfileView.as_view(), name="profile")
]
