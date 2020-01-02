# Generated by Django 2.2.5 on 2019-12-30 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_auto_20191227_1052'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='reservation',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancled', 'Cancled')], default='pending', max_length=12),
        ),
    ]
