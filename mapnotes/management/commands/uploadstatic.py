from django.conf import settings
from django.core.management.base import BaseCommand

from util.azure_storage import get_container_client
from util.azure_upload import AzureUpload, get_secret


class Command(BaseCommand):
    help = "Uploads staticfiles to Azure"

    def add_arguments(self, parser):
        parser.add_argument("--insecure", action="store_true")

    def handle(self, *args, **options):
        url = settings.PROJ_5_STORAGE_URL
        container = settings.PROJ_5_STORAGE_CONTAINER_NAME
        data_takeout_container = settings.PROJ_5_STORAGE_DATA_TAKEOUT_CONTAINER_NAME
        cred = settings.PROJ_5_STORAGE_CREDENTIAL_KEY

        key = get_secret()

        if data_takeout_container == container:
            # Making sure the container allows blob access
            get_container_client(url, cred, container)

        au = AzureUpload(url, container, cred, key)
        au.backup(local_path="./staticfiles", remote_path="staticfiles/", overwrite=False, insecure=options["insecure"])
