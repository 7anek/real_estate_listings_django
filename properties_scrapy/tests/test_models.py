from django.test import TestCase
from django.db import connections
from django.db.utils import OperationalError
from properties_scrapy.models import Property
from properties_scrapy.utils import *


class ModelTestCase(TestCase):
    def test_database_connection_is_working(self):
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError:
            connected = False
        else:
            connected = True
        self.assertEqual(connected, True)

    def test_localization(self):
        lat = 17.5013714
        lon = 78.3878926
        p = Property.objects.create(service_name='a', service_url='a', price=1, area=1, property_type='a',
                                    latitude=lat, longitude=lon)
        self.assertEqual(p.location.coords[1], lat)
        self.assertEqual(p.location.coords[0], lon)
