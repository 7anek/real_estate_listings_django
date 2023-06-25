from django.test import TestCase
from properties_scrapy.utils import *


# Create your tests here.

class UtilsTestCase(TestCase): 

    def test_dict_filter_none(self):
        d={'localization': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000, 'area_min': None, 'area_max': None, 'property_type': 'flat', 'offer_type': 'sell', 'plot_type': '', 'house_type': '', 'flat_type': '', 'year_of_construction_from': None, 'year_of_construction_to': None} 
        self.assertEqual(dict_filter_none(d),{'localization': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000, 'property_type': 'flat', 'offer_type': 'sell'})
    


