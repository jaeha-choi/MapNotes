import datetime

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.serializers import serialize
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.utils import timezone

from mapnotes.models import User, Note
from util.azure_storage import get_container_client
from util.binfile import BinFile


# Create your views here.

def index(request):  # shows the map interface and notes pinned at locations
    # latest_note_list = Note.objects.order_by('-date')[:100]
    latest_note_list = Note.objects.all()
    latest_note_list = serialize('json', latest_note_list,
                                 fields=['id', 'creator', 'body', 'date', 'lat', 'lon', 'upvotes'])
    # print(latest_note_list)
    return render(request, 'mapnotes/index.html', {'latest_note_list': latest_note_list})


def feed(request):  # shows the 100 latest notes ordered by publication date
    try:
        latest_note_list = Note.objects.order_by('-date')[:100]
        template = loader.get_template('mapnotes/feed.html')
        context = {
            'latest_note_list': latest_note_list,
        }
    except Note.DoesNotExist:
        raise Http404("Notes do not exist")
    return HttpResponse(template.render(context, request))


def profile(request, user_id):  # simple page showing user details
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'mapnotes/user.html', {'user': user})


def submit(request):  # response to user POSTing a note
    if request.method == "POST":
        form = request.POST
        print(form)
        u = None
        try:
            u = User.objects.get(email=request.POST['email'])
        except User.DoesNotExist:  # create a new user entry
            u = User(email=request.POST['email'])
            u.save()
        finally:
            m = u.map_set.create(name='Some random map Here', description='Some Map Here')
            m.note_set.create(body=request.POST['note'], date=timezone.now(),
                              lat=request.POST['lat'], lon=request.POST['lon'])
            next_ = request.POST.get('next', '/')
            return HttpResponseRedirect(next_)
    else:
        return JsonResponse({'error': 'Please fill out all parts of the form'}, status=400)


def login_request(request):  # process the login request
    form = AuthenticationForm()
    return render(request=request,
                  template_name="account/login.html",
                  context={"form": form})


def logout_request(request):  # process the logout request
    form = AuthenticationForm()
    return render(request=request,
                  template_name="account/logout.html",
                  context={"form": form})


def _data_takeout(map_id: str, creator_id: str = "") -> (bool, str):
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
    container_name = settings.PROJ_5_STORAGE_CONTAINER_NAME
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

        name = takeout_dir + "/" + map_id + datetime.datetime.now().strftime(".%Y-%m-%d_%H-%M-%S.json")
        with BinFile(max_size=1024) as f:
            serialize("json", queryset=query, stream=f)
            f.seek(0)
            client.upload_blob(name=name, data=f, overwrite=True)
    except Exception as e:
        return False, str(e)

    return True, "/".join((storage_url, container_name, name))
