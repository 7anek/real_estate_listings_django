# Generated by Django 4.2.2 on 2023-08-11 12:19

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.utils.timezone


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
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(max_length=255, null=True)),
                ('service_name', models.CharField(default=None, max_length=255)),
                ('service_url', models.CharField(default=None, max_length=255)),
                ('scrapyd_job_id', models.UUIDField(default=None, null=True)),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('modify_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('price', models.FloatField(default=None)),
                ('description', models.TextField(null=True)),
                ('area', models.FloatField(default=None)),
                ('property_type', models.CharField(choices=[('flat', 'Mieszkanie'), ('plot', 'Działka'), ('house', 'Dom'), ('garage', 'Garaż')], default='flat', max_length=100)),
                ('offer_type', models.CharField(choices=[('sell', 'Sprzedaż'), ('rent', 'Wynajem')], default='sell', max_length=100)),
                ('regular_user', models.BooleanField(default=None, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('province', models.CharField(max_length=255, null=True)),
                ('city', models.CharField(max_length=255, null=True)),
                ('county', models.CharField(max_length=255, null=True)),
                ('district', models.CharField(max_length=255, null=True)),
                ('district_neighbourhood', models.CharField(max_length=255, null=True)),
                ('street', models.CharField(max_length=255, null=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('radius', models.IntegerField(null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('floor', models.SmallIntegerField(default=None, null=True)),
                ('building_floors_num', models.SmallIntegerField(default=None, null=True)),
                ('rent', models.FloatField(default=None, null=True)),
                ('flat_type', models.CharField(choices=[('tenement', 'Kamienica'), ('block_of_flats', 'Blok'), ('apartment', 'Apartamentowiec')], default=None, max_length=100, null=True)),
                ('ownership', models.CharField(choices=[('full_ownership', 'Pełna własność'), ('cooperative_ownership', 'Spółdzielcze własnościowe'), ('cooperative_tenant', 'Spółdzielcze lokatorskie'), ('government_housing', 'Komunalne')], default=None, max_length=100, null=True)),
                ('heating', models.CharField(choices=[('urban', 'Miejskie'), ('gas', 'Gazowe')], default=None, max_length=100, null=True)),
                ('number_of_rooms', models.PositiveSmallIntegerField(default=None, null=True)),
                ('plot_type', models.CharField(choices=[('agricultural', 'Rolna'), ('building', 'Budowlana'), ('recreational', 'Rekreacyjna'), ('forest', 'Leśna')], default=None, max_length=100, null=True)),
                ('house_type', models.CharField(choices=[('detached_house', 'Wolnostojący'), ('semi_detached_house', 'Bliźniak'), ('terraced_house', 'Szeregowiec')], default=None, max_length=100, null=True)),
                ('plot_area', models.FloatField(default=None, null=True)),
                ('basement', models.BooleanField(default=None, null=True)),
                ('garage_heating', models.BooleanField(default=None, null=True)),
                ('garage_lighted', models.BooleanField(default=None, null=True)),
                ('garage_localization', models.CharField(choices=[('in_building', 'w budynku'), ('separate', 'samodzielny')], default=None, max_length=100, null=True)),
                ('forest_vicinity', models.BooleanField(default=None, null=True)),
                ('open_terrain_vicinity', models.BooleanField(default=None, null=True)),
                ('lake_vicinity', models.BooleanField(default=None, null=True)),
                ('electricity', models.BooleanField(default=None, null=True)),
                ('gas', models.BooleanField(default=None, null=True)),
                ('sewerage', models.BooleanField(default=None, null=True)),
                ('water', models.BooleanField(default=None, null=True)),
                ('fence', models.BooleanField(default=None, null=True)),
                ('build_year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('market_type', models.CharField(choices=[('primary', 'Pierwotny'), ('secondary', 'Wtórny')], default=None, max_length=100, null=True)),
                ('construction_status', models.CharField(choices=[('to_completion', 'Do wykończenia'), ('ready', 'Do zamieszkania')], default=None, max_length=100, null=True)),
                ('building_material', models.CharField(choices=[('brick', 'Cegła'), ('great_slab', 'Wielka płyta')], default=None, max_length=100, null=True)),
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
