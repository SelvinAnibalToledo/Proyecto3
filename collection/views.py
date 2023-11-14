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
from django.contrib.postgres import search
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger

class IndexView(ListView):
    model = Artwork
    context_object_name = 'Artwork'
    template_name = 'collection/index.html'
    paginate_by = 12
    #paginator_class = MyPaginator

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     print(qs)
    #     if qs:
    #         qs = qs.order_by(random.sample(qs,12))

    #     Art_genre = self.request.GET.get("artwork_genre")
    #     print(Art_genre)

    #     if Art_genre:
    #         qs = qs.order_by(qs.filter(genre__name=Art_genre))
        
    #     return qs

    # def get_context_data(self):
    #     artworks = self.get_queryset()

    #     genre = Genre.objects.filter(id=OuterRef('genre')).values("name")
    #     count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')
        
    #     genres = count.annotate(name=Subquery(genre)).values('name', 'count')


    #     print(genres)
    #     print(artworks)
    #     context = { "artworks": artworks,
    #                 "artwork_genre": genres,
    #     }

    #     return context
    def get_queryset(self):
        artworks = Artwork.objects.all()

        Art_genre = self.request.GET.get("artwork_genre")

        if Art_genre:
            artworks = artworks.filter(genre__name=Art_genre)

        print('Tamaño del queryset:', artworks.count())
        artworks=artworks.order_by('?')

        return artworks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = Genre.objects.filter(id=OuterRef('genre')).values("name")
        count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')
        
        genres = count.annotate(name=Subquery(genre)).values('name', 'count')

        # Obtener el queryset original asignado por ListView a 'object_list'
        artworks = self.object_list

        # Configurar la paginación
        paginator = Paginator(artworks,12)
        page_number = self.request.GET.get('page')

        # Aplicar paginación
        page_obj = paginator.get_page(page_number)

        context.update({
            'artwork_genre':genres,
            'artworks': page_obj,
            'paginator': paginator,
        })

        return context
        # context = super().get_context_data(**kwargs)

        # # Obtener el queryset original asignado por ListView a 'object_list'
        # artworks = context[self.context_object_name]

        # # Configurar la paginación
        # paginator = Paginator(artworks, 12)
        # page_number = self.request.GET.get('page')

        

        # try:
        #     page_obj = paginator.get_page(page_number)
        # except PageNotAnInteger:
        #     # Si la página no es un número entero, mostrar la primera página
        #     page_obj = paginator.get_page(1)
        # except EmptyPage:
        #     # Si la página está fuera de rango, mostrar la última página
        #     page_obj = paginator.get_page(paginator.num_pages)

        # print(paginator.num_pages)

        # context.update({
        #     'artwork_genre':genres,
        #     'artworks': page_obj,
        #     'paginator': paginator,
        # })

        # return context

    # def get(self, request):
    #     context = self.get_context_data(request=request)
    #     return render(request, 'collection/index.html', context=context)




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


def detail_artwork(request, path):
    #print(path)
    artwork = Artwork.objects.get(path='/en/'+path)
    context = {'artworks': artwork}
    return render(request, 'collection/artwork_detail.html',context=context)

def artist_detail(request,slug):
    artist = Artist.objects.get(slug=slug)
    artworks = Artwork.objects.filter(author=artist)
    print(artworks)
    paginator = Paginator(artworks, 12) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {'artist': artist, 
               "artworks":page_obj}
    
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

def search_artworks(request):
    if request.method == 'GET':
        value = request.GET['search']
        artworks = ft_artworks(value)

        genre = Genre.objects.filter(id=OuterRef('genre')).values("name")
        count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')
        
        genres = count.annotate(name=Subquery(genre)).values('name', 'count')

        paginator = Paginator(artworks, 12) 
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        print(artworks)
        return render(request, 'collection/artwork_search.html',
                      { 'search_value': value, 
                       'artworks': page_obj,
                       'artwork_genre':genres})
    else:
        return render(request, 'collection/index.html',
                      {'artworks': [], 'search_value': None})


def ft_artworks(value):
    vector = (
        search.SearchVector("title", weight="A")
        + search.SearchVector("author__name", weight="B")
        + search.SearchVector("style__name", weight="C")
        + search.SearchVector("genre__name", weight="C")
    )
    query = search.SearchQuery(value, search_type="websearch")

    return (
        Artwork.objects.annotate(
            search=vector,
            rank=search.SearchRank(vector, query),
        )
        .filter(search=query)
        .order_by("-rank")
    )