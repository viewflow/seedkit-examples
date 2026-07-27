from django.conf import settings
from django.http import HttpResponse

if settings.DEBUG:
    from silk.profiling.profiler import silk_profile
else:

    class silk_profile:  # no-op decorator + context manager for prod
        def __init__(self, *_a, **_kw):
            pass

        def __call__(self, fn):
            return fn

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False


@silk_profile(name="jobs.compute_report")
def compute_report():
    return sum(i * i for i in range(100_000))


def profile_demo(request):
    total = compute_report()
    return HttpResponse(f"computed {total}", content_type="text/plain")
