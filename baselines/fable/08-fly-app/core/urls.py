from django.urls import path

from core import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("healthz", views.healthz, name="healthz"),
    path("readyz", views.readyz, name="readyz"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("privacy/export/", views.export_user_data, name="privacy-export"),
    path("privacy/delete/", views.delete_account, name="privacy-delete"),
]
