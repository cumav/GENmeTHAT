# Generated by Django 2.1.1 on 2018-10-10 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('categories', models.CharField(max_length=500)),
            ],
        ),
    ]
