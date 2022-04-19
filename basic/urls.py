from . import views
from django.urls import path


urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("get/", views.get),
    path("service_plygin_list/", views.service_plygin_list),
    path("generic_list/", views.generic_list),
    path("slice_list/", views.slice_list),
    path("switch_share/", views.switch_share),
    path("switch_share_gen/", views.switch_share_gen),
]
