import datetime

from django.conf import settings
from django.core.serializers import serialize

from mapnotes.models import Note
from util.azure_storage import get_container_client
from util.binfile import BinFile


def data_takeout_backend(map_id: str, creator_id: str = "") -> (bool, str):
    """
    Download all notes in map_id, created by author_id. If author_id is not set, all notes in map_id will be downloaded.

    :param map_id: ID of a map.
    :param creator_id: ID of a user. If not set, all notes in map_id are downloaded
    :return: A boolean which indicates the result and a string containing a download URL or an error message.
            Boolean value is True if the operation was successful, false otherwise.
            String value is a download URL if and only if the first element is True.
    """
    # Grab settings
    storage_url = settings.PROJ_5_STORAGE_URL
    storage_cred_key = settings.PROJ_5_STORAGE_CREDENTIAL_KEY
    container_name = settings.PROJ_5_STORAGE_DATA_TAKEOUT_CONTAINER_NAME
    takeout_dir = settings.PROJ_5_TAKEOUT_DIRECTORY

    try:
        client = get_container_client(storage_url, storage_cred_key, container_name)
        kwargs = {}
        if creator_id:
            kwargs["creator__exact"] = creator_id

        query = Note.objects.filter(map_container_id__exact=map_id, **kwargs)

        if len(query) == 0:
            raise ValueError("no notes with matching map/author found")
        # TODO: implement data takeout for bigger maps (instead of having the user wait on the webpage,
        #  send notifications when done)
        if len(query) >= 10000:
            raise NotImplementedError("map with 10000+ query is not supported yet")

        name = takeout_dir + "/" + str(map_id) + datetime.datetime.now().strftime(".%Y-%m-%d_%H-%M-%S.json")
        with BinFile(max_size=1024) as f:
            serialize("json", queryset=query, stream=f)
            f.seek(0)
            client.upload_blob(name=name, data=f, overwrite=True)

        return True, "/".join((storage_url, container_name, name))
    except Exception as e:
        print(e)
        return False, str(e)
