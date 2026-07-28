from django.shortcuts import get_object_or_404, render

from jobs.models import Job


def job_list(request):
    jobs = Job.objects.published().select_related("posted_by")
    return render(request, "jobs/job_list.html", {"jobs": jobs})


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.published(), pk=pk)
    return render(request, "jobs/job_detail.html", {"job": job})
