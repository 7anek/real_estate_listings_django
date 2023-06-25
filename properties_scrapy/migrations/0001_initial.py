# Generated by Django 4.2.2 on 2023-06-25 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MissingValues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(default=None, max_length=255)),
                ('field_name', models.CharField(default=None, max_length=255)),
                ('value', models.CharField(default=None, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceFilterIds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(default=None, max_length=255)),
                ('field_name', models.CharField(default=None, max_length=255)),
                ('service_id', models.CharField(default=None, max_length=255)),
            ],
        ),
    ]
