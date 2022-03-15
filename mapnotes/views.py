from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from allauth.socialaccount.models import SocialAccount
from django.core.handlers.wsgi import WSGIRequest
from django.core.serializers import serialize
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.utils import timezone

from mapnotes.models import User, Note, Map
from util.data_takeout import data_takeout_backend


def index(request):  # shows the map interface and notes pinned at locations
    # notes = (User.objects.raw("SELECT * FROM mapnotes_note " +
    #     "INNER JOIN mapnotes_user ON (mapnotes_note.creator_id = mapnotes_user._id);"))
    if request.user.is_authenticated: 
        try: # make an account for the logged in user if not already
            data = SocialAccount.objects.get(user=request.user).extra_data
            uid = data.get('id')
            name = data.get('name')
            u = User(_id=uid, name=name)
            u.save()
        except Exception as e: # this will catch if user already exists
            print(e)

    notes = Note.objects.order_by('-date')[:100]
    notes = serialize('json', notes)
    return render(request, 'mapnotes/index.html', {'latest_note_list': notes})


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
            if request.user.is_authenticated: 
                data = SocialAccount.objects.get(user=request.user).extra_data
                uid = data.get('id')
                u = User.objects.get(_id__exact=uid)
            else:
                raise Exception('User must be signed in to post notes')
        except User.DoesNotExist as e:  # create a new user entry
            print(e)
        finally:
            try:
                global_map = _get_global_map()
            except Exception as _:
                raise Exception('Could not load the public map.')

            global_map.note_set.create(body=request.POST['note'], date=timezone.now(), creator_id=u._id,
                                       lat=request.POST['lat'], lon=request.POST['lon'])
            next_ = request.POST.get('next', '/')
            return HttpResponseRedirect(next_)

    else:
        return JsonResponse({'error': 'Please fill out all parts of the form'}, status=400)


def data_takeout_all(request: WSGIRequest):
    try:
        global_map = _get_global_map()
        res, msg = data_takeout_backend(str(global_map._id))
    except Exception as e:
        return JsonResponse({"success": 'false', "msg": str(e)})
    return JsonResponse({"success": res, "msg": msg})


def data_takeout_user(request: WSGIRequest):
    try:
        global_map = _get_global_map()
        if request.user.is_authenticated: 
            data = SocialAccount.objects.get(user=request.user).extra_data
            uid = data.get('id')
            u = User.objects.get(_id__exact=uid)
            res, msg = data_takeout_backend(str(global_map._id), uid)
        else:
            return JsonResponse({"success": 'false', "msg": "Please login before downloading notes."})
    except Exception as e:
        return JsonResponse({"success": 'false', "msg": str(e)})

    return JsonResponse({"success": res, "msg": msg})

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


def _get_global_map() -> Map:
    """
    A helper method to find global map created by superuser.

    :return: Map object
    :raises User.DoesNotExist: Superuser not found
    :raises Map.DoesNotExist: Map not found
    :raises Map.MultipleObjectsReturned: Too many map created by the superuser
    """
    try:
        su = User.objects.get(_id__exact=settings.DJANGO_SUPERUSER_ID)
        return Map.objects.get(creator_id__exact=su._id)
    except User.DoesNotExist as e:
        # Superuser account must exist
        print(e)
        raise
    except Map.DoesNotExist as e:
        # There should be one global map, created by superuser
        print(e)
        raise
    except Map.MultipleObjectsReturned as e:
        # There should be only one global map, created by superuser
        print(e)
        raise
    except Exception as e:
        print(e)
        raise
