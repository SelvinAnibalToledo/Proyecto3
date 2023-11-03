from typing import Any
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from collection.models import Artwork,Period,Genre
from django.views.generic.list import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
import random
from django.db.models import Count

class ArtListView(ListView):
    model = Artwork
    def get_context_data(self, **kws):
        context = super().get_context_data(**kws)
        id = Artwork.objects.values("genre")
        #context["genre_type"] = (
        #    Genre.objects.filter(id__in=id)
        #)
        context["genre_type"] = ( 
            #Genre.objects.filter(id__in=id).values("name"),
            Artwork.objects
            .values("genre")
            .annotate(count = Count("id"))
            
        )
        print(id)
        print(context["genre_type"])
        
        return (context)
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
    artwork = Artwork.objects.all()
    random_artwork = None
    query = request.GET.get("query")
    if query:
        artwork = artwork.filter(title__icontains=query)
    genre = Artwork.objects.values("genre").annotate(count=Count("id"))
    period = Artwork.objects.values("period").annotate(count=Count("id"))
    #genres =     
    #if count > 0:
    #    random_index = random.randint(0, count - 1)
    #    random_artwork = Artwork.objects.all()#[random_index]
    contexts = { "artwork": artwork,
                 "artwork_genre": genre,
                 "artwork_period":period
    }
    return render(request, 'collection/index.html', {"artwork": artwork})

