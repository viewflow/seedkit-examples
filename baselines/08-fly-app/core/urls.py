from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("healthz/", views.health_check, name="health-check"),
    path("account/data/export/", views.data_export, name="gdpr-data-export"),
    path("account/data/delete/", views.data_delete, name="gdpr-data-delete"),
]
