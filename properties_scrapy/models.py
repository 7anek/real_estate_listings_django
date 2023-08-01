# from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


# Create your models here.
class Property(models.Model):

    # class Meta:
    #     app_label = "properties"

    class TypesOfOffer(models.TextChoices):
        SELL = 'sell', 'Sprzedaż'
        RENT = 'rent', 'Wynajem'

    class TypesOfProperties(models.TextChoices):
        FLAT = 'flat', 'Mieszkanie'
        PLOT = 'plot', 'Działka'
        HOUSE = 'house', 'Dom'
        GARAGE = 'garage', 'Garaż'

    # flat choices

    class TypesOfFlats(models.TextChoices):
        TENEMENT = 'tenement', 'Kamienica'
        BLOCK_OF_FLATS = 'block_of_flats', 'Blok'
        APARTMENT = 'apartment', 'Apartamentowiec'

    class TypesOfBuildingMaterials(models.TextChoices):
        BRICK = 'brick', 'Cegła'
        GREAT_SLAB = 'great_slab', 'Wielka płyta'

    class TypesOfOwnership(models.TextChoices):
        FULL_OWNERSHIP = 'full_ownership', 'Pełna własność'
        COOPERATIVE_OWNERSHIP = 'cooperative_ownership', 'Spółdzielcze własnościowe'
        COOPERATIVE_TENANT = 'cooperative_tenant', 'Spółdzielcze lokatorskie'
        GOVERNMENT_HOUSING = 'government_housing', 'Komunalne'

    class TypesOfHeating(models.TextChoices):
        URBAN = 'urban', 'Miejskie'
        GAS = 'gas', 'Gazowe'

    class TypesOfMarket(models.TextChoices):
        PRIMARY = 'primary', 'Pierwotny'
        SECONDARY = 'secondary', 'Wtórny'

    class TypesOfConstructionStatus(models.TextChoices):
        TO_COMPLETION = 'to_completion', 'Do wykończenia'
        READY = 'ready', 'Do zamieszkania'

    # plot choices

    class TypesOfPlots(models.TextChoices):
        AGRICULTURAL = 'agricultural', 'Rolna',
        BUILDING = 'building', 'Budowlana',
        RECREATIONAL = 'recreational', 'Rekreacyjna',
        FOREST = 'forest', 'Leśna',

    # house choices

    class TypesOfHouses(models.TextChoices):
        DETACHED_HOUSE = 'detached_house', 'Wolnostojący',
        SEMI_DETACHED_HOUSE = 'semi_detached_house', 'Bliźniak',
        TERRACED_HOUSE = 'terraced_house', 'Szeregowiec',

    # garage choices

    class TypesOfGarageLocalizations(models.TextChoices):
        IN_BUILDING = 'in_building', 'w budynku'
        SEPARATE = "separate", 'samodzielny'

    service_id = models.CharField(max_length=255, null=True)
    service_name = models.CharField(max_length=255, null=False, default=None)
    service_url = models.CharField(max_length=255, null=False, default=None)
    scrapyd_job_id = models.UUIDField(primary_key=False, default=None, editable=True, null=True)
    create_date = models.DateTimeField(default=timezone.now, null=True)
    modify_date = models.DateTimeField(default=timezone.now, null=True)
    # main common fields
    title = models.CharField(max_length=255, null=True)
    price = models.FloatField(default=None, null=False)
    description = models.TextField(null=True)
    area = models.FloatField(default=None, null=False)
    property_type = models.CharField(max_length=100, choices=TypesOfProperties.choices, default=TypesOfProperties.FLAT,
                                     null=False)
    offer_type = models.CharField(max_length=100, choices=TypesOfOffer.choices, default=TypesOfOffer.SELL, null=False)
    regular_user = models.BooleanField(default=None,
                                       null=True)  # czy zamieszczone przez agenta czy przez osobę prywatną
    # localization fields
    address = models.CharField(max_length=255, null=True)
    province = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    county = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255, null=True)
    district_neighbourhood = models.CharField(max_length=255, null=True)  # poddzielnica np Muranów
    street = models.CharField(max_length=255, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    radius = models.IntegerField(null=True)
    location = models.PointField(blank=True, null=True)
    # flat fields
    floor = models.SmallIntegerField(default=None, null=True)
    building_floors_num = models.SmallIntegerField(default=None, null=True)
    rent = models.FloatField(default=None, null=True)  # czynsz
    flat_type = models.CharField(max_length=100, choices=TypesOfFlats.choices, default=None, null=True)
    ownership = models.CharField(max_length=100, choices=TypesOfOwnership.choices, default=None, null=True)
    heating = models.CharField(max_length=100, choices=TypesOfHeating.choices, default=None, null=True)
    number_of_rooms = models.PositiveSmallIntegerField(default=None, null=True)
    # plot fields
    plot_type = models.CharField(max_length=100, choices=TypesOfPlots.choices, default=None, null=True)
    # house fields
    house_type = models.CharField(max_length=100, choices=TypesOfHouses.choices, default=None, null=True)
    plot_area = models.FloatField(default=None, null=True)
    basement = models.BooleanField(default=None, null=True)
    # garage fields
    garage_heating = models.BooleanField(default=None, null=True)
    garage_lighted = models.BooleanField(default=None, null=True)
    garage_localization = models.CharField(max_length=100, choices=TypesOfGarageLocalizations.choices, default=None,
                                           null=True)
    # house and plot fields
    forest_vicinity = models.BooleanField(default=None, null=True)  # vicinity - rodzaj sąsiedztwa, sąsiedztwo lasu
    open_terrain_vicinity = models.BooleanField(default=None, null=True)  # sąsiedztwo otwartego terenu
    lake_vicinity = models.BooleanField(default=None, null=True)  # sąsiedztwo jeziora
    electricity = models.BooleanField(default=None, null=True)
    gas = models.BooleanField(default=None, null=True)
    sewerage = models.BooleanField(default=None, null=True)  # kanalizacja
    water = models.BooleanField(default=None, null=True)
    fence = models.BooleanField(default=None, null=True)
    # house and flat fields
    build_year = models.PositiveSmallIntegerField(default=None, null=True)
    market_type = models.CharField(max_length=100, choices=TypesOfMarket.choices, default=None, null=True)
    construction_status = models.CharField(max_length=100, choices=TypesOfConstructionStatus.choices, default=None,
                                           null=True)
    building_material = models.CharField(max_length=100, choices=TypesOfBuildingMaterials.choices, default=None,
                                         null=True)

    def save(self, *args, **kwargs):
        if self.longitude and self.latitude:
            self.location = Point(self.longitude, self.latitude)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_name} - {self.service_id} - {self.price} - {self.area} - {self.title}"


class ServiceFilterIds(models.Model):
    service_name = models.CharField(max_length=255, null=False, default=None)
    field_name = models.CharField(max_length=255, null=False, default=None)
    service_id = models.CharField(max_length=255, null=False, default=None)


class MissingValues(models.Model):
    service_name = models.CharField(max_length=255, null=False, default=None)
    field_name = models.CharField(max_length=255, null=False, default=None)
    value = models.CharField(max_length=255, null=False, default=None)
