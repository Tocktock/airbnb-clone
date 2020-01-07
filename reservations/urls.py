from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    path(
        "create/<int:room>/<int:year>-<int:month>-<int:day>",
        views.create,
        name="create",
    ),
    path("delete-reservations/<int:pk>", views.delete, name="delete-res",),
    path("<int:pk>/", views.ReservationDetailView.as_view(), name="detail",),
    path("<int:pk>/<str:verb>/", views.edit_reservation, name="edit",),
    path("my-reservations/", views.MyReservationView.as_view(), name="my-reservations"),
]

