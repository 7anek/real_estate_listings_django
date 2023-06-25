# from django.test import TestCase
from unittest import TestCase

from scrapy.http import TextResponse, HtmlResponse, Response, Request
import json
from datetime import datetime, date, timedelta
from properties_scrapy.models import Property
from properties_scrapy.scrapy_project.items import ScrapyItem

# try:
#     from properties.models import Property
# except ModuleNotFoundError:
#     import os, sys
#     from django.core.wsgi import get_wsgi_application
#
#     sys.path.append(os.path.dirname(os.path.abspath("..")))
#     os.environ["DJANGO_SETTINGS_MODULE"] = "properties_scrapping.settings"
#     application = get_wsgi_application()
#     from properties.models import Property
from properties_scrapy.scrapy_project.spiders.otodom_spider import OtodomSpider
from properties_scrapy.scrapy_project.spiders.domiporta_spider import DomiportaSpider
from properties_scrapy.scrapy_project.spiders.gratka_spider import GratkaSpider
from properties_scrapy.scrapy_project.spiders.morizon_spider import MorizonSpider
from properties_scrapy.scrapy_project.spiders.olx_spider import OlxSpider
from properties_scrapy.scrapy_project.pipelines import PropertiesScrapyPipeline

from asgiref.sync import sync_to_async
from django.core.exceptions import ImproperlyConfigured
import unittest


class ScraperParseTestCase(TestCase):
    def fake_scrapy_response(self, file_path, url):
        return HtmlResponse(
            url=url,
            request=Request(url=url),
            body=open(file_path, "rb").read(),
            # body=open(file_path, "rb", encoding="utf8").read(),
            encoding="utf-8",
        )

    # def setUp(self):
    #     self.otodom_spider = OtodomSpider()

    # def test_otodom_spider_from_file(self):
    #     search_form=json.dumps({'localization': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000, 'area_min': None, 'area_max': None, 'property_type': 'flat', 'offer_type': 'sell', 'plot_type': '', 'house_type': '', 'flat_type': '', 'build_year_from': None, 'build_year_to': None})
    #     job_id='75d6b108cc9811edba0300155d7be260'
    #     params={'search_form':search_form,'_job':job_id}
    #     url="http://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/grodzisk-mazowiecki?distanceRadius=0&priceMin=300000&priceMax=400000&locations=%5Bcities_6-703%5D&viewType=listing&limit=24&page=1"
    #     results = self.spider.parse(fake_response_from_file('otodom-search4.html', url))

    #     print('results',results)
    #     print('list(results)',list(results))
    #     print('Property.objects.all()',Property.objects.all())
    #     print('Ala ma kota')

    def test_parse_otodom_offer(self):
        # return True
        search_form = json.dumps(
            {
                "address": "Jaktorów, Polska",
                "province": "Mazowieckie",
                "city": "Jaktorów",
                "price_min": 30000,
                "price_max": 400000,
                "property_type": "flat",
                "offer_type": "sell",
            }
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = OtodomSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer")
        path = "test_data/otodom/otodom-details.html"
        # url='http://www.otodom.pl/64121978'
        url = "http://www.otodom.pl/pl/oferta/mieszkanie-44-m-jaktorow-ID4ggVJ.html"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        # self.assertEqual(item['title'], 'Mieszkanie 48m²⭐Stan Deweloperski⭐3 pokoje⭐Centrum')
        # self.assertEqual(item['price'], 395000)
        self.assertEqual(item["service_id"], 62983737)
        self.assertEqual(item["service_name"], "otodom")
        self.assertEqual(item["title"], "Mieszkanie, 44 m², Jaktorów")
        self.assertEqual(item["price"], 190000)
        # item["location"] = ", ".join([offer_dict["target"]["City"], offer_dict["target"]["Subregion"],offer_dict["target"]["Province"]])
        self.assertEqual(item["area"], 44)
        # item["floor"] = parse_floor(offer_dict["target"]["Floor_no"]) if "Floor_no" in offer_dict["target"] else None
        self.assertEqual(item["number_of_rooms"], 2)
        self.assertEqual(item["property_type"], "flat")
        # self.assertEqual(item["house_type"],"block")
        # item["create_date"] = datetime.fromisoformat(offer_dict["createdAt"])
        # item["modify_date"] = datetime.fromisoformat(offer_dict["modifiedAt"])
        # self.assertEqual(items[0]['location'], 'Wrocław, Krzyki, ul. Mickiewicza')
        # self.assertEqual(items[0]['description'], 'Kawalerka o powierzchni 50,17 m2 usytuowana na III piętrze w 6 piętrowym budynku na Krzykach')

    # # def test_otodom_spider_from_file(self):
    # #     search_form=json.dumps({'localization': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000, 'area_min': None, 'area_max': None, 'property_type': 'flat', 'offer_type': 'sell', 'plot_type': '', 'house_type': '', 'flat_type': '', 'build_year_from': None, 'build_year_to': None})

    def test_parse_olx_offer(self):
        search_form = json.dumps(
            {
                "address": "Grodzisk Mazowiecki, Polska",
                "province": "Mazowieckie",
                "city": "Grodzisk Mazowiecki",
                "price_min": 300000,
                "price_max": 400000,
                "property_type": "flat",
                "offer_type": "sell",
            }
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = OlxSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer")
        path = "test_data/olx/olx-details.html"
        url = "https://www.olx.pl/d/oferta/atrakcyjne-mieszkania-w-centrum-grodziska-maz-ceny-juz-od-8500-m2-CID3-IDM6vnR.html"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["service_id"], 710818583)
        self.assertEqual(item["service_name"], "olx")
        self.assertEqual(
            item["title"],
            "Atrakcyjne mieszkania w centrum Grodziska Maz. ceny już od 8500/m2",
        )
        self.assertEqual(item["price"], 380000.0)
        # item["location"] = ", ".join([offer_dict["target"]["City"], offer_dict["target"]["Subregion"],offer_dict["target"]["Province"]])
        self.assertEqual(item["area"], 40.0)
        # item["floor"] = parse_floor(offer_dict["target"]["Floor_no"]) if "Floor_no" in offer_dict["target"] else None
        self.assertEqual(item["number_of_rooms"], 2)
        self.assertEqual(item["property_type"], "flat")
        self.assertEqual(item["flat_type"], "block_of_flats")
        # item["create_date"] = datetime.fromisoformat(offer_dict["createdAt"])
        # item["modify_date"] = datetime.fromisoformat(offer_dict["modifiedAt"])
        # self.assertEqual(items[0]['location'], 'Wrocław, Krzyki, ul. Mickiewicza')
        # self.assertEqual(items[0]['description'], 'Kawalerka o powierzchni 50,17 m2 usytuowana na III piętrze w 6 piętrowym budynku na Krzykach')

    def test_parse_offer_domiporta_flat(self):
        search_form = json.dumps(
            {"price_max": 400000, "property_type": "flat", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = DomiportaSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer")
        path = "test_data/domiporta/domiporta-details.html"
        # url='http://www.otodom.pl/64121978'
        url = "http://www.domiporta.pl/nieruchomosci/sprzedam-mieszkanie-dwupokojowe-chrzanow-maly-chrzanow-maly-41m2/154218398"
        request = Request(url=url)
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]

        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "154218398")
        self.assertEqual(item["service_name"], "domiporta")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], None)
        self.assertEqual(item["modify_date"], None)

        self.assertEqual(item["title"], "Mieszkanie dwupokojowe na sprzedaż")
        self.assertEqual(item["price"], 390_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 41.0)
        self.assertEqual(item["property_type"], Property.TypesOfProperties.FLAT.value)
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        # self.assertEqual(item["address"], 'Michałowice małopolskie')
        self.assertEqual(item["province"], "mazowieckie")
        self.assertEqual(item["city"], "Chrzanow Maly")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], 2)
        self.assertEqual(item["building_floors_num"], 3)
        self.assertEqual(item["rent"], 500)
        self.assertEqual(item["basement"], None)
        self.assertEqual(item["flat_type"], Property.TypesOfFlats.BLOCK_OF_FLATS.value)
        self.assertEqual(
            item["ownership"], Property.TypesOfOwnership.FULL_OWNERSHIP.value
        )
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], 2)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], None)
        self.assertEqual(item["build_year"], 2016)
        self.assertEqual(item["market_type"], Property.TypesOfMarket.SECONDARY.value)
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(
            item["building_material"], Property.TypesOfBuildingMaterials.BRICK.value
        )

    def test_parse_offer_domiporta_plot(self):
        search_form = json.dumps(
            {"price_max": 400000, "property_type": "plot", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = DomiportaSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer_domiporta_plot")
        path = "test_data/domiporta/domiporta-details-plot.html"
        # url='http://www.otodom.pl/64121978'
        url = "https://www.domiporta.pl/nieruchomosci/sprzedam-dzialke-kolczewo-2101m2/148747351"
        request = Request(url=url)
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]

        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "148747351")
        self.assertEqual(item["service_name"], "domiporta")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], None)
        self.assertEqual(item["modify_date"], None)

        self.assertEqual(item["title"], "Działka rekreacyjna na sprzedaż")
        self.assertEqual(item["price"], 360_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 2_101.0)
        self.assertEqual(item["property_type"], Property.TypesOfProperties.PLOT.value)
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        self.assertEqual(item["address"], "Kołczewo")
        self.assertEqual(item["province"], "Zachodniopomorskie")
        self.assertEqual(item["city"], "Kolczewo")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["basement"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(
            item["ownership"], Property.TypesOfOwnership.FULL_OWNERSHIP.value
        )
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], None)
        self.assertEqual(item["plot_type"], Property.TypesOfPlots.RECREATIONAL.value)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], True)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], True)
        self.assertEqual(item["build_year"], None)
        self.assertEqual(item["market_type"], Property.TypesOfMarket.SECONDARY.value)
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], None)

    def test_parse_offer_domiporta_garage(self):
        search_form = json.dumps(
            {"price_max": 400000, "property_type": "garage", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = DomiportaSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer_domiporta_garage")
        path = "test_data/domiporta/domiporta-details-garage.html"
        # url='http://www.otodom.pl/64121978'
        url = "https://www.domiporta.pl/nieruchomosci/sprzedam-garaz-katowice-al-wojciecha-korfantego-31m2/154432519"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]

        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "154432519")
        self.assertEqual(item["service_name"], "domiporta")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], None)
        self.assertEqual(item["modify_date"], None)

        self.assertEqual(item["title"], "Garaż na sprzedaż")
        self.assertEqual(item["price"], 89_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 31.0)
        self.assertEqual(item["property_type"], Property.TypesOfProperties.GARAGE.value)
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        self.assertEqual(item["address"], "Katowice,al. Wojciecha Korfantego")
        self.assertEqual(item["province"], "Slaskie")
        self.assertEqual(item["city"], "Katowice")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["basement"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], None)
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], None)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], None)
        self.assertEqual(item["build_year"], 1972)
        self.assertEqual(item["market_type"], Property.TypesOfMarket.SECONDARY.value)
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], None)

    def test_parse_gratka_flat_offer(self):
        search_form = json.dumps(
            {
                "price_min": 300000,
                "price_max": 400000,
                "property_type": "flat",
                "offer_type": "sell",
            }
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = GratkaSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer")
        path = "test_data/gratka/gratka-details.html"
        url = "https://gratka.pl/nieruchomosci/mieszkanie-grodzisk-mazowiecki-ul-grunwaldzka/ob/30116547"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "30116547")
        self.assertEqual(item["service_name"], "gratka")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], date.today() + timedelta(days=-31))
        self.assertEqual(item["modify_date"], date.today())

        self.assertEqual(
            item["title"], "Mieszkanie Grodzisk Mazowiecki, ul. Grunwaldzka"
        )
        self.assertEqual(item["price"], 348_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 47.0)
        self.assertEqual(item["property_type"], "flat")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        # self.assertEqual(item["address"], 'ul. Grunwaldzka Grodzisk Mazowiecki, mazowieckie')
        self.assertEqual(item["province"], "mazowieckie")
        self.assertEqual(item["city"], "grodzisk-mazowiecki")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], "Grunwaldzka")
        self.assertEqual(item["floor"], 4)
        self.assertEqual(item["building_floors_num"], 4)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["basement"], True)
        self.assertEqual(item["flat_type"], Property.TypesOfFlats.BLOCK_OF_FLATS.value)
        self.assertEqual(item["ownership"], "cooperative_ownership")
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], 3)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], None)
        self.assertEqual(item["build_year"], 1980)
        self.assertEqual(item["market_type"], Property.TypesOfMarket.SECONDARY.value)
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(
            item["building_material"], Property.TypesOfBuildingMaterials.BRICK.value
        )

    def test_parse_gratka_plot_offer2(self):
        search_form = json.dumps(
            {"price_max": 400000, "property_type": "plot", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = GratkaSpider(search_form=search_form, _job=job_id)
        print("test_parse_gratka_offer_plot2")
        path = "test_data/gratka/gratka-details-plot2.html"
        url = "https://gratka.pl/nieruchomosci/dzialka-budowlana-ksawerow-z-budynkiem-mieszkalnym/oi/30041237"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "30041237")
        self.assertEqual(item["service_name"], "gratka")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], date.today() + timedelta(days=-31))
        self.assertEqual(item["modify_date"], date.today() + timedelta(days=-4))

        self.assertEqual(
            item["title"], "Działka budowlana Ksawerów z budynkiem mieszkalnym"
        )
        self.assertEqual(item["price"], 350_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 855.0)
        self.assertEqual(item["property_type"], "plot")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], True)
        # self.assertEqual(item["address"], 'ul. Macieja Rataja 2, Ksawerów, łódzkie')#niewczytało się
        self.assertEqual(item["province"], "lodzkie")
        self.assertEqual(item["city"], "ksawerow")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], "Macieja Rataja")
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["basement"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], None)
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], None)
        self.assertEqual(item["plot_type"], Property.TypesOfPlots.BUILDING.value)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], True)
        self.assertEqual(item["gas"], True)
        self.assertEqual(item["sewerage"], True)
        self.assertEqual(item["water"], True)
        self.assertEqual(item["fence"], True)
        self.assertEqual(item["build_year"], None)
        # self.assertEqual(item["market_type"], None)
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], None)

    def test_parse_gratka_garage_offer(self):
        search_form = json.dumps(
            {"price_max": 400000, "property_type": "garage", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = GratkaSpider(search_form=search_form, _job=job_id)
        print("test_parse_gratka_offer_garage")
        path = "test_data/gratka/gratka-details-garage.html"
        url = "https://gratka.pl/nieruchomosci/sprzedam-miejsce-w-hali-garazowej-gdansk-ul-jeleniogorska-od-zaraz/oi/30026531"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "30026531")
        self.assertEqual(item["service_name"], "gratka")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], date.today() + timedelta(days=-31))
        self.assertEqual(item["modify_date"], date.today() + timedelta(days=-5))

        # self.assertEqual(item["title"], 'SPRZEDAM miejsce w hali garażowej Gdańsk, ul Jeleniogórska od zaraz')
        self.assertEqual(item["price"], 33_500.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 14.60)
        self.assertEqual(item["property_type"], "garage")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], True)
        # self.assertEqual(item["address"], 'ul. Jeleniogórska Gdańsk, pomorskie')
        self.assertEqual(item["province"], "pomorskie")
        self.assertEqual(item["city"], "gdansk")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["basement"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], Property.TypesOfOwnership.FULL_OWNERSHIP)
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], None)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], True)
        self.assertEqual(
            item["garage_localization"], Property.TypesOfGarageLocalizations.SEPARATE
        )
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], None)
        self.assertEqual(item["build_year"], None)
        self.assertEqual(item["market_type"], None)
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], None)

    def test_parse_gratka_house_offer(self):
        search_form = json.dumps({"property_type": "house", "offer_type": "sell"})
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = GratkaSpider(search_form=search_form, _job=job_id)
        print("test_parse_gratka_offer_house")
        path = "test_data/gratka/gratka-details-house.html"
        url = "https://gratka.pl/nieruchomosci/sprzedam-dom-przy-michalowicach-duzy-taras-rekuperacja-klima-fotowoltaika/oi/27855401"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "27855401")
        self.assertEqual(item["service_name"], "gratka")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"], date.today() + timedelta(days=-183))
        self.assertEqual(item["modify_date"], date.today() + timedelta(days=-14))

        self.assertEqual(
            item["title"],
            "Sprzedam DOM przy Michałowicach / DUŻY TARAS /rekuperacja / klima / fotowoltaika",
        )
        self.assertEqual(item["price"], 1_750_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 140.0)
        self.assertEqual(item["property_type"], "house")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], True)
        # self.assertEqual(item["address"], 'Michałowice małopolskie')
        self.assertEqual(item["province"], "malopolskie")
        self.assertEqual(item["city"], "michalowice")
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], 2)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["basement"], False)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], Property.TypesOfOwnership.FULL_OWNERSHIP)
        self.assertEqual(item["heating"], None)  # jak parsować?
        self.assertEqual(item["number_of_rooms"], 6)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(
            item["house_type"], Property.TypesOfHouses.DETACHED_HOUSE.value
        )
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], True)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], True)
        self.assertEqual(item["build_year"], 2016)
        self.assertEqual(item["market_type"], Property.TypesOfMarket.SECONDARY.value)
        self.assertEqual(
            item["construction_status"], Property.TypesOfConstructionStatus.READY.value
        )
        self.assertEqual(
            item["building_material"], Property.TypesOfBuildingMaterials.BRICK.value
        )

    def test_parse_morizon_flat_offer(self):
        search_form = json.dumps(
            {
                "address": "Grodzisk Mazowiecki, Polska",
                "province": "Mazowieckie",
                "city": "Grodzisk Mazowiecki",
                "price_min": 300000,
                "price_max": 400000,
                "property_type": "flat",
                "offer_type": "sell",
            }
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = MorizonSpider(search_form=search_form, _job=job_id)
        print("test_parse_offer")
        path = "test_data/morizon/morizon-details.html"
        url = "https://www.morizon.pl/oferta/sprzedaz-mieszkanie-grodziski-grodzisk-mazowiecki-grunwaldzka-38m2-mzn2041893797"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        # items = list(results)
        self.assertEqual(
            list(results), []
        )  # oferta z innej strony, trzeba pobrać nowy przykład

    def test_parse_morizon_plot_offer(self):
        search_form = json.dumps(
            {"price_max": 400000, "property_type": "plot", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = MorizonSpider(search_form=search_form, _job=job_id)
        print("test_parse_morizon_plot_offer")
        path = "test_data/morizon/morizon-details-plot.html"
        url = "https://www.morizon.pl/oferta/sprzedaz-dzialka-mragowski-piecki-1760m2-mzn2041893356"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "morizon-164/12353/OGS")
        self.assertEqual(item["service_name"], "morizon")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"].year, 2023)
        self.assertEqual(item["create_date"].month, 4)
        self.assertEqual(item["create_date"].day, 20)
        self.assertEqual(item["modify_date"].year, 2023)
        self.assertEqual(item["modify_date"].month, 4)
        self.assertEqual(item["modify_date"].day, 24)

        self.assertEqual(item["title"], None)
        self.assertEqual(item["price"], 3_100_000.0)
        self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 7_000.0)
        self.assertEqual(item["property_type"], "plot")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        self.assertEqual(item["address"], "Piaseczyński,Lesznowola")
        self.assertEqual(item["province"], None)
        self.assertEqual(item["city"], None)
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], None)
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], None)
        self.assertEqual(item["plot_type"], "building")
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], False)
        self.assertEqual(item["build_year"], None)
        self.assertEqual(item["market_type"], "secondary")
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], None)

    def test_parse_morizon_house_offer(self):
        search_form = json.dumps(
            {"price_max": 10_000_000, "property_type": "house", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = MorizonSpider(search_form=search_form, _job=job_id)
        print("test_parse_morizon_plot_offer")
        path = "test_data/morizon/morizon-details-house.html"
        url = "https://www.morizon.pl/oferta/sprzedaz-dom-krakow-zwierzyniec-wodociagowa-440m2-mzn2039204511"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "morizon-557816")
        self.assertEqual(item["service_name"], "morizon")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"].year, 2021)
        self.assertEqual(item["create_date"].month, 8)
        self.assertEqual(item["create_date"].day, 24)
        self.assertEqual(item["modify_date"].year, 2022)
        self.assertEqual(item["modify_date"].month, 8)
        self.assertEqual(item["modify_date"].day, 19)

        self.assertEqual(item["title"], None)
        self.assertEqual(item["price"], 7_490_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 440.0)
        self.assertEqual(item["property_type"], "house")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        self.assertEqual(
            item["address"], "Kraków,Zwierzyniec,Salwator,Wodociagowa"
        )
        self.assertEqual(item["province"], None)
        self.assertEqual(item["city"], None)
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], None)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], "full_ownership")
        self.assertEqual(item["heating"], "gas")
        self.assertEqual(item["number_of_rooms"], 6)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], "detached_house")
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], True)
        self.assertEqual(item["gas"], True)
        self.assertEqual(item["sewerage"], True)
        self.assertEqual(item["water"], True)
        self.assertEqual(item["fence"], True)
        self.assertEqual(item["build_year"], None)
        self.assertEqual(item["market_type"], "secondary")
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], "brick")

    def test_parse_morizon_garage_offer(self):
        search_form = json.dumps(
            {"price_max": 10_000_000, "property_type": "garage", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = MorizonSpider(search_form=search_form, _job=job_id)
        print("test_parse_morizon_garage_offer")
        path = "test_data/morizon/morizon-details-garage.html"
        url = "https://www.morizon.pl/oferta/sprzedaz-garaz-wejherowski-rumia-wyzynna-83m2-mzn2041927555"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "morizon-157")
        self.assertEqual(item["service_name"], "morizon")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"].year, 2023)
        self.assertEqual(item["create_date"].month, 4)
        self.assertEqual(item["create_date"].day, 13)
        self.assertEqual(item["modify_date"].year, 2023)
        self.assertEqual(item["modify_date"].month, 5)
        self.assertEqual(item["modify_date"].day, 8)

        self.assertEqual(item["title"], None)
        self.assertEqual(item["price"], 160_000.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 83.4)
        self.assertEqual(item["property_type"], "garage")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        self.assertEqual(item["address"], "Wejherowski (pow.),Rumia,Wyżynna")
        self.assertEqual(item["province"], None)
        self.assertEqual(item["city"], None)
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], 0)
        self.assertEqual(item["building_floors_num"], None)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["flat_type"], None)
        self.assertEqual(item["ownership"], "full_ownership")
        self.assertEqual(item["heating"], None)
        self.assertEqual(item["number_of_rooms"], None)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], "in_building")
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], True)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], None)
        self.assertEqual(item["build_year"], 2004)
        self.assertEqual(item["market_type"], "secondary")
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], None)

    def test_parse_morizon_flat_offer(self):
        search_form = json.dumps(
            {"price_max": 10_000_000, "property_type": "flat", "offer_type": "sell"}
        )
        job_id = "75d6b108cc9811edba0300155d7be260"
        spider = MorizonSpider(search_form=search_form, _job=job_id)
        print("test_parse_morizon_flat_offer")
        path = "test_data/morizon/morizon-details-flat.html"
        url = "https://www.morizon.pl/oferta/sprzedaz-mieszkanie-warszawa-bialoleka-palukow-68m2-mzn2041856530"
        response = self.fake_scrapy_response(path, url)
        results = spider.parse_offer(response)
        # print('results',list(results))
        items = list(results)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["scrapyd_job_id"], "75d6b108cc9811edba0300155d7be260")
        self.assertEqual(item["service_id"], "morizon-1")
        self.assertEqual(item["service_name"], "morizon")
        self.assertEqual(item["service_url"], url)

        self.assertEqual(item["create_date"].year, 2023)
        self.assertEqual(item["create_date"].month, 3)
        self.assertEqual(item["create_date"].day, 28)
        self.assertEqual(item["modify_date"].year, 2023)
        self.assertEqual(item["modify_date"].month, 5)
        self.assertEqual(item["modify_date"].day, 4)

        self.assertEqual(item["title"], None)
        self.assertEqual(item["price"], 700_230.0)
        # self.assertEqual(item["description"], None)
        self.assertEqual(item["area"], 68.6)
        self.assertEqual(item["property_type"], "flat")
        self.assertEqual(item["offer_type"], "sell")
        self.assertEqual(item["regular_user"], False)
        self.assertEqual(
            item["address"], "Warszawa,Białołęka,Tarchomin,Pałuków"
        )
        self.assertEqual(item["province"], None)
        self.assertEqual(item["city"], None)
        self.assertEqual(item["county"], None)
        self.assertEqual(item["district"], None)
        self.assertEqual(item["district_neighbourhood"], None)
        self.assertEqual(item["street"], None)
        self.assertEqual(item["floor"], 2)
        self.assertEqual(item["building_floors_num"], 7)
        self.assertEqual(item["rent"], None)
        self.assertEqual(item["flat_type"], "apartment")
        self.assertEqual(item["ownership"], "full_ownership")
        self.assertEqual(item["heating"], "urban")
        self.assertEqual(item["number_of_rooms"], 3)
        self.assertEqual(item["plot_type"], None)
        self.assertEqual(item["house_type"], None)
        self.assertEqual(item["garage_heating"], None)
        self.assertEqual(item["garage_lighted"], None)
        self.assertEqual(item["garage_localization"], None)
        self.assertEqual(item["forest_vicinity"], None)
        self.assertEqual(item["lake_vicinity"], None)
        self.assertEqual(item["electricity"], None)
        self.assertEqual(item["gas"], None)
        self.assertEqual(item["sewerage"], None)
        self.assertEqual(item["water"], None)
        self.assertEqual(item["fence"], None)
        self.assertEqual(item["build_year"], 2022)
        self.assertEqual(item["market_type"], "primary")
        self.assertEqual(item["construction_status"], None)
        self.assertEqual(item["building_material"], "great_slab")



