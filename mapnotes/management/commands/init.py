import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from mapnotes.models import User, Map


class Command(BaseCommand):
    # can_import_settings = True
    help = "Initializes MapNotes app"

    def handle(self, *args, **options):
        try:
            u = User.objects.get(email=settings.DJANGO_SUPERUSER_EMAIL)
        except User.DoesNotExist:
            print("Creating superuser for mapnotes")
            u = User(name=settings.DJANGO_SUPERUSER_USERNAME, email=settings.DJANGO_SUPERUSER_EMAIL)
            u.save()

        try:
            Map.objects.get(creator_id__exact=u._id)
        except Map.DoesNotExist:
            print("Creating default map")
            u.map_set.create(name='Public Map created by admin', description='This map is visible to the world')
        except Map.MultipleObjectsReturned:
            print("Error: multiple maps found. Current implementation requires exactly one map to be created.")
            sys.exit(1)
        print("Successfully initialized mapnotes")
