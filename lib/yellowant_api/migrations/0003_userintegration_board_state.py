# Generated by Django 2.0.6 on 2018-06-18 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yellowant_api', '0002_yellowantredirectstate'),
    ]

    operations = [
        migrations.AddField(
            model_name='userintegration',
            name='board_state',
            field=models.CharField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', max_length=2048),
        ),
    ]
