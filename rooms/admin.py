from django.contrib import admin
from . import models
from django.utils.html import mark_safe


@admin.register(models.RoomType, models.Facility, models.HouseRule, models.Amenity)
class ItemAdmin(admin.ModelAdmin):

    """ Item Admin Definition """

    list_display = ("name", "used_by")

    def used_by(self, obj):
        return obj.rooms.count()

    pass


class PhotoInline(admin.TabularInline):
    model = models.Photo


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    """ Room Admin Definition """

    inlines = (PhotoInline,)
    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "description", "country", "city", "price", "address",)},
        ),
        ("Times", {"fields": ("check_in", "check_out", "instant_book",)},),
        (
            "More About the Sapce",
            {
                "classes": ("collapse",),
                "fields": ("amenities", "facilities", "house_rules",),
            },
        ),
        ("Spaces", {"fields": ("guests", "beds", "bedrooms", "baths",)},),
        ("Last Details", {"fields": ("host",)},),
    )

    list_display = (
        "name",
        "country",
        "city",
        "price",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "count_amenities",
        "count_photos",
        "total_rating",
    )
    list_filter = (
        "instant_book",
        "host__superhost",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
        "city",
        "country",
    )
    search_fields = ("^city", "^host__username", "^name")

    filter_horizontal = (
        "amenities",
        "facilities",
        "house_rules",
    )
    raw_id_fields = ("host",)

    def count_amenities(self, obj):
        # object는 row
        return obj.amenities.count()

    def count_photos(self, obj):
        # object는 row
        return obj.photos.count()

    count_photos.short_description = "photo count"
    count_amenities.short_description = "Hello Sexy"


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):

    """ Photo Admin Definition """

    list_display = ("__str__", "get_thumnail")

    def get_thumnail(self, obj):
        return mark_safe(f"<img width =100 src ={obj.file.url}>")

    get_thumnail.short_description = "Thumnail"

    pass
