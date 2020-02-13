from django.core.management.base import BaseCommand
from rooms.models import RoomType


class Command(BaseCommand):

    help = "this command create room_types"

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--times", help="How many times do you want to me to tell you I love you",
    #     )

    def handle(self, *args, **options):
        room_types = [
            "Private Room",
            "Hotel Room",
            "ApartMent",
            "Guest House",
        ]
        for r in room_types:
            RoomType.objects.create(name=r)
        self.stdout.write(self.style.SUCCESS("Amenities created"))
