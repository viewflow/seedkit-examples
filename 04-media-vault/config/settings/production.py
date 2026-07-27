from .base import *

# Always set STATIC_URL in prod — without a fallback, missing
# AWS_S3_CUSTOM_DOMAIN leaves the base `/static/` value pointing at a path
# the prod app does not serve, so every admin asset 404s. Guard with
# `if AWS_STORAGE_BUCKET_NAME:` so ASGI projects that load production.py in
# dev (bucket env may be empty) still boot via the base.py FileSystemStorage
# fallback — without the guard, boto3 raises ParamValidationError on every
# admin asset request.
if AWS_STORAGE_BUCKET_NAME:
    STORAGES = {
        **STORAGES,
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            "OPTIONS": {"location": "static"},
        },
    }

    if AWS_S3_CUSTOM_DOMAIN:
        STATIC_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/static/"
    elif AWS_S3_ENDPOINT_URL:
        # Non-AWS provider without a custom domain: serve from the endpoint host.
        STATIC_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/static/"
    else:
        # AWS without CloudFront — bucket vhost. us-east-1 omits the region.
        _region = "" if AWS_S3_REGION_NAME == "us-east-1" else f".{AWS_S3_REGION_NAME}"
        STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3{_region}.amazonaws.com/static/"
