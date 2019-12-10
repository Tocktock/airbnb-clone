import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django_seed import Seed
from users import models as user_models
from rooms import models as room_models
from reservations import models as reservations_models

NAME = "reservations"


class Command(BaseCommand):

    help = f"this command create {NAME}"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", default=2, type=int, help=f"How many {NAME} you want to create"
        )

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--times", help="How many times do you want to me to tell you I love you",
    #     )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        guests = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()
        seeder.add_entity(
            reservations_models.Reservation,
            number,
            {
                "guest": lambda x: random.choice(guests),
                "room": lambda x: random.choice(rooms),
                "check_in": lambda x: datetime.now(),
                "check_out": lambda x: datetime.now()
                + timedelta(days=random.randint(3, 25)),
            },
        )

        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{number} {NAME} created!"))
