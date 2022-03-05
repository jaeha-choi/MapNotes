from re import template
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.template import loader
from mapnotes.models import User, Note

# Create your views here.
def index(request): # shows the map interface and notes pinned at locations
    template = loader.get_template('mapnotes/index.html')
    return render(request, 'mapnotes/index.html', {})

def feed(request): # shows the 100 latest notes ordered by publication date
    latest_note_list = Note.objects.order_by('-date')[:100]
    template = loader.get_template('mapnotes/feed.html')
    context = {
        'latest_note_list': latest_note_list,
    }
    return HttpResponse(template.render(context, request))

def profile(request, user_id): # simple page showing user details
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'mapnotes/user.html', {'user': user})