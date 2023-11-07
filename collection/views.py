from typing import Any
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views import View
from collection.models import Artwork,Period,Genre
from django.views.generic.list import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.db.models import Count, Subquery, OuterRef

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
        qs = super().get_queryset()
        Art_genre = self.request.GET.get("artwork_genre")
        print(Art_genre)

        if Art_genre:
            qs = qs.filter(genre__name=Art_genre)
        
        print(qs)
        return qs

    def get_context_data(self, request):
        artwork = self.get_queryset
        query = request.GET.get("query")
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

    query = request.GET.get("query")
    if query:
        artwork = artwork.filter(title__icontains=query)

    
    genre = Genre.objects.filter(id=OuterRef('genre')).values("name")
    count = Artwork.objects.values("genre").annotate(count = Count("id")).values('count')
    
    genres = count.annotate(name=Subquery(genre)).values('name', 'count')

    period = Artwork.objects.values("period").annotate(count=Count("id"))

    print(genres)
    #genres =     
    #if count > 0:
    #    random_index = random.randint(0, count - 1)
    #    random_artwork = Artwork.objects.all()#[random_index]
    context = { "artwork": artwork,
                 "artwork_genre": genres,
                 "artwork_period":period
    }
    return render(request, 'collection/index.html', context=context)

