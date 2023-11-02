from typing import Any
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from collection.models import Artwork
from django.views.generic.list import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
import random

class ArtListView(ListView):
    model = Artwork
    def get_context_data(self, **kws):
        context = super().get_context_data(**kws)
        context["genre_type"] = (
            Artwork.objects
            .values("genre")
            #.annotate(count = Count("id"))
        )
        return context
        #return render(request, 'collection/index.html', {'artwork': random_artwork})


def register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            username = f.cleaned_data.get('username')
            raw_password = f.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect('/')

    else:
        f = UserCreationForm()

    return render(request, 'registration/registration_form.html', {'form': f})

def home(request):
    qs = Artwork.objects.all()
    query = request.GET.get("query")
    if query:
        qs = qs.filter(title__icontains=query)
        #qs = Artwork.objects.annotate(search=SearchVector("title")).filter(search=SearchQuery(query))
        #qs = Artwork.objects.annotate(
        #    headline=SearchHeadline(
        #        "title",
        #        SearchQuery(query),
        #        start_sel="<b><u><i>",
        #        stop_sel="</i></u></b>",
        #    )
        #)
    return render(request, "collection/artwork_list.html", {"queryset": qs})

def index(request):   
    count = Artwork.objects.count()
    random_artwork = None
    if count > 0:
        random_index = random.randint(0, count - 1)
        random_artwork = Artwork.objects.all()[random_index]

    return render(request, 'collection/index.html', {'artwork': random_artwork})

