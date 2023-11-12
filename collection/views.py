from typing import Any
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views import View
from collection.models import Artwork,Period,Genre, Artist, Collection
from django.views.generic.list import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.db.models import Count, Subquery, OuterRef
import random
from .forms import CollectionForm

class GenresListView(ListView):
    model=Artwork
    
    def get_context_data(self, **kws):
        context = super().get_context_data(**kws)

        genres = Genre.objects.filter(id=OuterRef('genre')).values("name")
        count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')

        context["genre_type"] = ( 
            count.annotate(name=Subquery(genres)).values('name', 'count')
        )

        print(context["genre_type"])
        
        return context


class IndexView(ListView):
    model = Artwork

    def get_queryset(self):
        qs2 = super().get_queryset()
        qs = list(qs2)
        
        if qs:
            qs = random.sample(qs, 10)
        Art_genre = self.request.GET.get("artwork_genre")
        print(Art_genre)

        if Art_genre:
            qs = list(qs2.filter(genre__name=Art_genre))
        
        return qs[:10]

    def get_context_data(self, request):
        artwork = self.get_queryset

        query = request.GET.get("search")
        if query:
            artwork = Artwork.objects.filter(title__icontains=query)

        
        genre = Genre.objects.filter(id=OuterRef('genre')).values("name")
        count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')
        
        genres = count.annotate(name=Subquery(genre)).values('name', 'count')

        period = Artwork.objects.values("period").annotate(count=Count("id"))

        print(genres)
        
        context = { "artwork": artwork,
                    "artwork_genre": genres,
                    "artwork_period":period
        }

        return context
    
    def get(self, request):
        context = self.get_context_data(request=request)
        return render(request, 'collection/index.html', context=context)




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
    return render(request, "collection/artwork_list.html", {"queryset": qs})

def index(request):   
    artwork = Artwork.objects.all()

    query = request.GET.get("query")
    if query:
        artwork = artwork.filter(title__icontains=query)

    
    genre = Genre.objects.filter(id=OuterRef('genre')).values("name")
    count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')
    
    genres = count.annotate(name=Subquery(genre)).values('name', 'count')

    period = Artwork.objects.values("period").annotate(count=Count("id"))
    print(artwork)
    print(genres)
    print(period)
    context = { "artwork": artwork,
                 "artwork_genre": genres,
                 "artwork_period":period
    }
    return render(request, 'collection/index.html', context=context)

def detail_artwork(request, path):
    #print(path)
    artwork = Artwork.objects.get(path='/en/'+path)
    context = {'artwork': artwork}
    #print(artwork)
    #print(path)
    return render(request, 'collection/artwork_detail.html',context=context)

def artist_detail(request,slug):
    artist = Artist.objects.get(slug=slug)
    context = {'artist': artist}
    return render(request, "collection/artist_detail.html", context=context)

def collections(request):
    print(request.user)
    if request.user.is_authenticated:
        collections = Collection.objects.filter(owner=request.user)
        for collection in collections:
            print(f"Collection Name: {collection.name}")

            # Itera sobre los artworks en la colección
            for artwork in collection.artworks.all():
                print(f"Artwork Title: {artwork.title}")
    else:
        collections = ''      
    return render(request, 'collection/collections.html',
                  {'collections': collections})


def collection_list(request):
    if request.user.is_authenticated:
        collections = Collection.objects.filter(owner=request.user)
    else:
        collections = ''   
    return render(request, 'collection/collection_list.html',
                  {'collections': collections})



def collection_add(request):
    form= None

    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            collection = Collection(
                    name=name,
                    description=description,
                    owner=request.user)
            collection.save()
            return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})
        
    context ={
        "form":form
    }

    return render(request,
                  'collection/collection_form.html',
                  context)


def collection_modify(request, id):
    collection = Collection.objects.get(id=id)
    form = CollectionForm(request.POST or None, instance=collection)

    if request.method == "POST":
        if form.is_valid():
                collection = form.save()
                return HttpResponse(status=204,
                                    headers={'HX-Trigger': 'listChanged'})
            

    context ={
        "form":form,
        "collection":collection
    }

    return render(request, "collection/collection_form.html", context)


def collection_delete(request, id):
    collection = Collection.objects.get(id=id)
    try:
        collection.delete()
    except:
        pass
    return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})

def modal_collection(request, id):
    if request.user.is_authenticated:
        collections = Collection.objects.filter(owner=request.user)
        idArtwork = id
        context ={
            "collections":collections,
            "idArtworks":idArtwork
        }
    else:
        collections = ''
        context = {
            "collections":collections
        }  
    
    return render(request, "collection/collection_artworks.html", context)

def add_artwork_collection(request, idCollection, idArtwork):
    collection = Collection.objects.get(id=idCollection)
    artwork = Artwork.objects.get(id=idArtwork)

    collection.artworks.add(artwork)

    return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})