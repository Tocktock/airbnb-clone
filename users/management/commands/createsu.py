from django.core.management.base import BaseCommand
from django_seed import Seed
from users.models import User


class Command(BaseCommand):

    help = "this command create superusers"

    def handle(self, *args, **options):
        try:
            User.objects.get(username="ebadmin")
            self.stdout.write(self.style.SUCCESS(f"SuperUser Exist"))
        except User.DoesNotExist:
            User.objects.create_superuser("ebadmin", "manyang@naver.com", "123")
            self.stdout.write(self.style.SUCCESS(f"SuperUser created"))
