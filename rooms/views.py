from math import ceil
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator, EmptyPage
from django.views.generic import ListView, DetailView, View
from django_countries import countries
from . import models, forms


class HomeView(ListView):
    """ HomeView Definition """

    model = models.Room
    paginate_by = 10
    ordering = "created"
    paginate_orphans = 5
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context


class RoomDetail(DetailView):
    """ RoomDetail Definition """

    model = models.Room


class SearchView(View):

    """ SearchView Definition """

    def get(self, request):

        country = request.GET.get("country")
        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                bedrooms = form.cleaned_data.get("bedrooms")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facility")
                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms
                if beds is not None:
                    filter_args["beds__gte"] = beds
                if baths is not None:
                    filter_args["baths__gte"] = baths
                if instant_book is True:
                    filter_args["instant_book"] = True
                if superhost is True:
                    filter_args["host__superhost"] = True

                rooms = models.Room.objects.filter(**filter_args).order_by("-created")
                for amenity in amenities:
                    rooms = rooms.filter(amenities__pk=amenity.pk)

                for facility in facilities:
                    rooms = rooms.filter(facilities__pk=facility.pk)

                page_size = 2
                paginator = Paginator(rooms, page_size)
                page = int(request.GET.get("page", 1))

                page_count = int(ceil(rooms.count() / page_size))
                print(page, page_count)
                rooms = paginator.get_page(page)
                return render(
                    request,
                    "rooms/search.html",
                    {
                        "form": form,
                        "rooms": rooms,
                        "page": page,
                        "page_count": page_count,
                    },
                )

        else:
            form = forms.SearchForm()
        return render(request, "rooms/search.html", {"form": form})

