# Generated by Django 5.0.1 on 2024-12-10 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_message_receiver_remove_message_sender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='idproof',
            field=models.CharField(max_length=12),
        ),
    ]