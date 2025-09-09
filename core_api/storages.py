from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    """
    Stores static files (CSS, JS, images used in frontend/admin).
    Served via AWS S3 at: https://<bucket>.s3.amazonaws.com/static/...
    """
    location = "static"
    default_acl = "public-read"
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN


class MediaStorage(S3Boto3Storage):
    """
    Stores media files (uploaded films, posters, trailers).
    Served via AWS S3 at: https://<bucket>.s3.amazonaws.com/media/...
    """
    location = "media"
    file_overwrite = False
    default_acl = "public-read"
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
