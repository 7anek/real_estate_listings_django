from django.test import TestCase
from properties_scrapy.utils import *
from properties_scrapy.scrapy_project.spiders import gratka, otodom, olx, nieruchomosci_online, domiporta, morizon


class HelperTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.search_params = {'address': 'Grodzisk Mazowiecki, Polska', 'province': 'Mazowieckie',
                             'city': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000,
                             'property_type': 'flat', 'offer_type': 'sell'}
        cls.search_params_2 = {'address': 'Muranów, Warszawa, Polska', 'province': 'Mazowieckie',
                               'city': 'Warszawa', 'district': 'Śródmieście', 'district_neighbourhood': 'Muranów',
                               'price_min': 300000, 'price_max': 400000, 'property_type': 'flat', 'offer_type': 'sell'}
        cls.search_params_3 = {'address': 'Mokotów, Warszawa, Polska', 'province': 'Mazowieckie',
                               'city': 'Warszawa', 'district': 'Mokotów', 'price_min': 300000, 'price_max': 400000,
                               'property_type': 'flat', 'offer_type': 'sell'}
        cls.search_params_4 = {'address': 'Mazowieckie, Polska', 'province': 'Mazowieckie',
                               'price_min': 300000, 'price_max': 400000, 'property_type': 'flat', 'offer_type': 'sell'}
        cls.search_params_5 = {'address': 'Elektoralna, Warszawa, Polska', 'province': 'Mazowieckie',
                               'city': 'Warszawa', 'district': 'Śródmieście', 'street': 'Elektoralna',
                               'price_min': 300000, 'price_max': 400000, 'property_type': 'flat', 'offer_type': 'sell'}
        cls.search_params_6 = {'price_min': 300000, 'price_max': 400000, 'property_type': 'flat', 'offer_type': 'sell'}
        cls.search_params_7 = {'address': 'Grodzisk Mazowiecki, Polska', 'province': 'Mazowieckie',
                               'city': 'Grodzisk Mazowiecki', 'price_max': 4000, 'property_type': 'flat',
                               'offer_type': 'rent'}

    # otodom
    def test_otodom_url_path(self):
        self.assertEqual(otodom.get_url_path(self.search_params), 'pl/oferty/sprzedaz/mieszkanie/grodzisk-mazowiecki')
        self.assertEqual(otodom.get_url_path(self.search_params_2), 'pl/oferty/sprzedaz/mieszkanie/warszawa/muranow')
        self.assertEqual(otodom.get_url_path(self.search_params_3), 'pl/oferty/sprzedaz/mieszkanie/warszawa/mokotow')
        self.assertEqual(otodom.get_url_path(self.search_params_4), 'pl/oferty/sprzedaz/mieszkanie/mazowieckie')
        self.assertEqual(otodom.get_url_path(self.search_params_5),
                         'pl/oferty/sprzedaz/mieszkanie/warszawa/srodmiescie')
        self.assertEqual(otodom.get_url_path(self.search_params_6), 'pl/oferty/sprzedaz/mieszkanie/cala-polska')

    def test_otodom_request_params(self):
        self.assertEqual(otodom.url_query(self.search_params),
                         {'distanceRadius': 0, 'market': 'ALL', 'viewType': 'listing', 'lang': 'pl',
                          'searchingCriteria': 'sprzedaz', 'priceMin': 300000, 'priceMax': 400000, 'limit': 24,
                          'page': 1})
        # self.assertEqual(otodom.url_query(self.search_params_5),{'distanceRadius': 0, 'market': 'ALL', 'viewType': 'listing', 'lang': 'pl', 'searchingCriteria': 'sprzedaz', 'priceMin': 300000, 'priceMax': 400000, 'limit': 24, 'page': 1, 'locations': '[streets-11167]'})

    # olx
    def test_olx_url_path(self):
        self.assertEqual(olx.get_url_path(self.search_params),
                         '/d/nieruchomosci/mieszkania/sprzedaz/grodzisk-mazowiecki')
        self.assertEqual(olx.get_url_path(self.search_params_3), '/d/nieruchomosci/mieszkania/sprzedaz/warszawa')
        self.assertEqual(olx.get_url_path(self.search_params_6), '/d/nieruchomosci/mieszkania/sprzedaz')

    def test_olx_request_params(self):
        self.assertEqual(olx.get_request_params(self.search_params),
                         {'page': 1, 'search[filter_float_price:from]': 300000,
                          'search[filter_float_price:to]': 400000})

    # nieruchomosci_online
    def test_nieruchomosci_online_url_path(self):
        self.assertEqual(nieruchomosci_online.get_url_path(self.search_params), '/szukaj.html')

    def test_nieruchomosci_online_request_params(self):
        self.assertEqual(nieruchomosci_online.get_request_params(self.search_params),
                         {',mieszkanie,sprzedaz,,Grodzisk Mazowiecki,,,,300000-400000,,,,,,,,,,,,,,,,,,,,,,': '',
                          'page': 1})
        self.assertEqual(nieruchomosci_online.get_request_params(self.search_params_2),
                         {',mieszkanie,sprzedaz,,Warszawa,Muranów,,,300000-400000,,,,,,,,,,,,,,,,,,,,,,': '',
                          'page': 1})
        self.assertEqual(nieruchomosci_online.get_request_params(self.search_params_3),
                         {',mieszkanie,sprzedaz,,Warszawa,Mokotów,,,300000-400000,,,,,,,,,,,,,,,,,,,,,,': '',
                          'page': 1})
        self.assertEqual(nieruchomosci_online.get_request_params(self.search_params_6),
                         {',mieszkanie,sprzedaz,,,,,,300000-400000,,,,,,,,,,,,,,,,,,,,,,': '', 'page': 1})

    def test_nieruchomosci_online_url(self):
        self.assertEqual(generate_url(
            scheme='https',
            netloc='www.nieruchomosci-online.pl',
            path="/szukaj.html",
            url='',
            query={',mieszkanie,sprzedaz,,Grodzisk Mazowiecki,,,,300000-400000,,,,,,,,,,,,,,,,,,,,,,': '', 'page': 1},
            fragment=''
        ),
            'https://www.nieruchomosci-online.pl/szukaj.html?%2Cmieszkanie%2Csprzedaz%2C%2CGrodzisk+Mazowiecki%2C%2C%2C%2C300000-400000%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C=&page=1')

    # gratka
    def test_gratka_url_path(self):
        self.assertEqual(gratka.get_url_path(self.search_params), '/nieruchomosci/mieszkania/grodzisk-mazowiecki')
        self.assertEqual(gratka.get_url_path(self.search_params_2), '/nieruchomosci/mieszkania/warszawa/srodmiescie')
        self.assertEqual(gratka.get_url_path(self.search_params_3), '/nieruchomosci/mieszkania/warszawa/mokotow')
        self.assertEqual(gratka.get_url_path(self.search_params_4), '/nieruchomosci/mieszkania/mazowieckie')
        self.assertEqual(gratka.get_url_path(self.search_params_5), '/nieruchomosci/mieszkania/warszawa/ul-elektoralna')
        self.assertEqual(gratka.get_url_path(self.search_params_6), '/nieruchomosci/mieszkania')
        self.assertEqual(gratka.get_url_path(self.search_params_7),
                         '/nieruchomosci/mieszkania/grodzisk-mazowiecki/wynajem')

    def test_gratka_request_params(self):
        self.assertEqual(gratka.get_url_query(self.search_params),
                         {'cena-calkowita:min': 300000, 'cena-calkowita:max': 400000, 'page': 1})

    def test_gratka_url(self):
        self.assertEqual(generate_url(
            scheme='http',
            netloc='gratka.pl',
            path=gratka.get_url_path(self.search_params),
            url='',
            query=gratka.get_url_query(self.search_params),
            fragment=''
        ),
            'http://gratka.pl/nieruchomosci/mieszkania/grodzisk-mazowiecki?page=1&cena-calkowita%3Amin=300000&cena-calkowita%3Amax=400000')

    # morizon
    def test_morizon_url_path(self):
        self.assertEqual(morizon.get_url_path(self.search_params), '/mieszkania/grodzisk-mazowiecki/')
        self.assertEqual(morizon.get_url_path(self.search_params_2), '/mieszkania/warszawa/muranow/')
        self.assertEqual(morizon.get_url_path(self.search_params_3), '/mieszkania/warszawa/mokotow/')
        self.assertEqual(morizon.get_url_path(self.search_params_4), '/mieszkania/mazowieckie/')
        self.assertEqual(morizon.get_url_path(self.search_params_5), '/mieszkania/warszawa/srodmiescie/elektoralna/')
        self.assertEqual(morizon.get_url_path(self.search_params_6), '/mieszkania/')
        self.assertEqual(morizon.get_url_path(self.search_params_7), '/do-wynajecia/mieszkania/grodzisk-mazowiecki/')

    def test_morizon_request_params(self):
        self.assertEqual(morizon.get_url_query(self.search_params),
                         {'ps[price_from]': 300000, 'ps[price_to]': 400000, 'page': 1})

    def test_morizon_url(self):
        self.assertEqual(generate_url(
            scheme='http',
            netloc='www.morizon.pl',
            path=morizon.get_url_path(self.search_params),
            url='',
            query=morizon.get_url_query(self.search_params),
            fragment=''
        ),
            'http://www.morizon.pl/mieszkania/grodzisk-mazowiecki/?page=1&ps%5Bprice_from%5D=300000&ps%5Bprice_to%5D=400000')

    # domiporta
    def test_domiporta_url_path(self):
        self.assertEqual(domiporta.get_url_path(self.search_params),
                         '/mieszkanie/sprzedam/mazowieckie/grodzisk-mazowiecki')
        self.assertEqual(domiporta.get_url_path(self.search_params_2),
                         '/mieszkanie/sprzedam/mazowieckie/warszawa/muranow')
        self.assertEqual(domiporta.get_url_path(self.search_params_3),
                         '/mieszkanie/sprzedam/mazowieckie/warszawa/mokotow')
        self.assertEqual(domiporta.get_url_path(self.search_params_4), '/mieszkanie/sprzedam/mazowieckie')
        self.assertEqual(domiporta.get_url_path(self.search_params_5),
                         '/mieszkanie/sprzedam/mazowieckie/warszawa/elektoralna')
        self.assertEqual(domiporta.get_url_path(self.search_params_6), '/mieszkanie/sprzedam')
        self.assertEqual(domiporta.get_url_path(self.search_params_7),
                         '/mieszkanie/wynajme/mazowieckie/grodzisk-mazowiecki')

    def test_domiporta_request_params(self):
        self.assertEqual(domiporta.get_url_query(self.search_params),
                         {'Price.From': 300000, 'Price.To': 400000, 'PageNumber': 1})

    def test_domiporta_url(self):
        self.assertEqual(generate_url(
            scheme='http',
            netloc='www.domiporta.pl',
            path=domiporta.get_url_path(self.search_params),
            url='',
            query=domiporta.get_url_query(self.search_params),
            fragment=''
        ),
            'http://www.domiporta.pl/mieszkanie/sprzedam/mazowieckie/grodzisk-mazowiecki?PageNumber=1&Price.From=300000&Price.To=400000')
