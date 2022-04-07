from . import views
from django.urls import path


urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("get/", views.get),
    path("service_plygin_list/", views.service_plygin_list),
    path("switch_share/", views.switch_share)
]
