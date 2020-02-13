from math import ceil
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator, EmptyPage
from django.views.generic import ListView, DetailView, View, UpdateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django_countries import countries


from users import mixins as user_mixins
from . import models, forms


class HomeView(ListView):
    """ HomeView Definition """

    model = models.Room
    paginate_by = 12
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

        city = request.GET.get("city")
        if city:
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

                #testing situation about paginator you should make lots of room data.
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


class EditRoomView(user_mixins.LoggedOnlyView, UpdateView):
    model = models.Room
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )
    template_name = "rooms/room_edit.html"

    def get_object(self, queryset=None):
        room = super().get_object()
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


class RoomPhotosView(user_mixins.LoggedOnlyView, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object()
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user

    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo is deleted")

        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(user_mixins.LoggedOnlyView, SuccessMessageMixin, UpdateView):
    model = models.Photo
    template_name = "rooms/photo_edit.html"
    fields = ("caption",)
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated"

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(user_mixins.LoggedOnlyView, FormView):
    model = models.Photo
    template_name = "rooms/photo_create.html"
    fields = (
        "caption",
        "file",
    )
    form_class = forms.CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))


class CreateRoomView(user_mixins.LoggedOnlyView, FormView):

    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form):
        room = form.save(self.request.user)
        room.host = self.request.user
        room.save()
        form.save_m2m()
        messages.success(self.request, "Created Room")
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))

