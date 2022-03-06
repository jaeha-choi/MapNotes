import json
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.template import loader
from mapnotes.models import User, Note

# Create your views here.


def index(request):  # shows the map interface and notes pinned at locations
    latest_note_list = Note.objects.order_by('-date')[:100]
    latest_note_list = serialize('json', latest_note_list, 
        fields=['id', 'creator', 'body', 'date', 'lat', 'lon', 'upvotes'])
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
        if (form.get('display_name') and form.get('fname') and
                form.get('lname') and form.get('email') and form.get('lat') and form.get('lon')):
            u = None
            try:
                u = User.objects.get(email=request.POST['email'])
            except User.DoesNotExist:  # create a new user entry
                u = User(display_name=request.POST['display_name'],
                         email=request.POST['email'], fname=request.POST['fname'],
                         lname=request.POST['lname'])
            finally:
                u.note_set.create(
                    body=request.POST['note'], date=timezone.now(), 
                    lat=request.POST['lat'], lon=request.POST['lon'])
                next = request.POST.get('next', '/')
                return HttpResponseRedirect(next)
    else:
        return JsonResponse({'error': 'Please fill out all parts of the form'}, status=400)
