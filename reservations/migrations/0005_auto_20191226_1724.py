# Generated by Django 2.2.5 on 2019-12-26 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_auto_20191226_1704'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookedday',
            options={'verbose_name': 'booked Day', 'verbose_name_plural': 'Booked Days'},
        ),
    ]