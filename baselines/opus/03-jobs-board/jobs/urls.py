from django.urls import path

from jobs import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="list"),
    path("jobs/<int:pk>/", views.job_detail, name="detail"),
]
