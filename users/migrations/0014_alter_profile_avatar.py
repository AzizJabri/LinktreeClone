# Generated by Django 4.0.6 on 2023-02-11 00:51

from django.db import migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=users.models.LongerImageField(default='default_ibxmy4.jpg', max_length=2048, upload_to=users.models.Profile.change_avatar_name),
        ),
    ]
