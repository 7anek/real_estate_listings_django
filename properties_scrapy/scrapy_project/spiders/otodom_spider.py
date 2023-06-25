from bs4 import BeautifulSoup

from properties_scrapy.utils import *
from scrapy.spiders import Spider
from scrapy import Request
import math
import re
from datetime import datetime
import chompjs
import json
from properties_scrapy.models import Property, ServiceFilterIds
from properties_scrapy.scrapy_project.spiders import otodom
from contextlib import suppress
from properties_scrapy.scrapy_project.items import ScrapyItem


class OtodomSpider(Spider):
    # class PropertiesSpider(Spider):
    name = "otodom"
    service_name = "otodom"
    domain = "www.otodom.pl"
    scheme = "http"
    results_per_page = 24
    first_offer_detail = True
    max_pages_download = 5

    def __init__(self, *args, **kwargs):
        super(OtodomSpider, self).__init__(*args, **kwargs)
        search_form_json = kwargs.get("search_form", False)
        self.scrapyd_job_id = kwargs.get("_job")
        search_form = json.loads(search_form_json) if search_form_json else {}

        search_form = dict_filter_none(search_form)
        # do testowania z konsoli
        # if not search_form:
        #     search_form={'address': 'Elektoralna, Warszawa, Polska', 'province': 'Mazowieckie', 'city': 'Warszawa', 'district': 'Śródmieście','street':'Elektoralna', 'price_min': 300000, 'price_max': 1000000, 'property_type': 'flat', 'offer_type': 'sell'}

        if search_form:
            # add pagination params
            search_form["limit"] = self.results_per_page
            search_form["page"] = 1
            self.use_playwright = "street" in search_form
            self.search_form = search_form
            self.current_url = self.url_from_params()
            self.start_urls = [self.current_url]
        else:
            self.search_form = search_form
            self.query_params = ""
            self.current_url = ""
            self.use_playwright = False
            self.start_urls = []

    def start_requests(self):
        if self.use_playwright:
            for url in self.start_urls:
                selenium = selenium_browser()
                selenium.get(url)
                selenium.implicitly_wait(3)
                selenium.save_screenshot("../test_data/otodom/otodom1.png")
                selenium.find_element("id", "onetrust-accept-btn-handler").click()
                selenium.find_element("id", "location").click()
                selenium.find_element(
                    "css selector",
                    'ul[data-testid="selected-locations"] > li:nth-child(2)',
                ).click()
                selenium.find_element("id", "location-picker-input").send_keys(
                    self.search_form["address"]
                )
                selenium.find_element(
                    "css selector", "ul.css-1tsmnl6 li:first-child"
                ).click()
                selenium.save_screenshot("../test_data/otodom/otodom2.png")
                selenium.find_element("id", "search-form-submit").click()
                selenium.implicitly_wait(3)
                selenium.save_screenshot("../test_data/otodom/otodom3.png")
                print("selenium.current_url", selenium.current_url)
                new_url = selenium.current_url
                selenium.close()
                yield Request(url=new_url)
        else:
            for url in self.start_urls:
                yield Request(url=url)

    def parse(self, response):
        # return True
        print("response.request.url", response.request.url)
        parsed_url_query = url_to_params_dict(response.request.url)
        print("parsed_url_query", parsed_url_query)
        if not "page" in parsed_url_query:
            print("not page in parsed_url")
            return False

        current_page = parsed_url_query["page"]
        if not current_page:
            print("not current_page")
            return False
        print("current_page", current_page)
        # tu chce wyszukać ulice

        num_results = self.get_results_num(response)
        if not num_results:
            return False
        print("num_results", num_results)
        results_per_page = 24
        num_pages = math.ceil(num_results / results_per_page)
        num_pages = (
            self.max_pages_download
            if num_pages > self.max_pages_download
            else num_pages
        )
        print("num_pages", num_pages)

        if "locations" in parsed_url_query:
            self.search_form["locations"] = parsed_url_query["locations"]
        # return True
        if num_pages and int(current_page) == 1:
            for i in range(2, num_pages + 1):
                self.current_url = self.url_from_params(page=i, limit=results_per_page)
                yield response.follow(self.current_url)

        m = re.search(r"ad_impressions\":\[((\d+,)*\d+)\]", response.text)
        offers_ids = list(set((m.group(1).split(","))))
        domain = "http://www.otodom.pl/"
        offers_urls = list(
            map(lambda offer_id: domain + offer_id, set((m.group(1).split(","))))
        )
        for offer_url in offers_urls:
            yield response.follow(offer_url, callback=self.parse_offer)

        # offers_html = soup.find_all('a', {"data-cy": "listing-item-link"})
        # for offer in offers_html:
        #     print('******************', offer['href'], '//////////////////')
        #     yield response.follow("https://www.otodom.pl"+offer['href'], callback=self.parse_get)

    def parse_offer(self, response):
        # if self.first_offer_detail:
        #     with open("/home/janek/python/property_scraper/test_data/otodom-details.html", "w") as file:
        #         file.write(response.text)
        js = response.css("script#__NEXT_DATA__::text").get()
        data = chompjs.parse_js_object(js)
        offer_dict = data["props"]["pageProps"]["ad"]

        if not offer_dict:
            return False

        item = ScrapyItem()
        # item = {}
        # item=localization_fields_from_search_form(item, self.search_form)

        item["scrapyd_job_id"] = self.scrapyd_job_id
        item["service_id"] = self.parse_service_id(offer_dict["id"])
        item["service_name"] = self.service_name
        item["service_url"] = response.request.url

        item["create_date"] = datetime.fromisoformat(offer_dict["createdAt"])
        item["modify_date"] = datetime.fromisoformat(offer_dict["modifiedAt"])

        item["title"] = offer_dict["title"]
        item["price"] = float(offer_dict["target"]["Price"])
        item["description"] = offer_dict["description"]
        item["area"] = float(offer_dict["target"]["Area"])
        item["property_type"] = self.parse_property_type(
            offer_dict["target"]["ProperType"]
        )  # lub z search_forma
        item["offer_type"] = self.search_form["offer_type"]
        item["regular_user"] = self.parse_regular_user(offer_dict)
        item["address"] = self.search_form["address"]
        item["province"] = self.parse_province(offer_dict)
        item["city"] = self.parse_city(offer_dict)
        item["county"] = self.parse_county(offer_dict)
        item["district"] = self.parse_district(offer_dict)
        item["district_neighbourhood"] = self.parse_district_neighbourhood(offer_dict)
        item["street"] = self.parse_street(offer_dict)
        item["floor"] = self.parse_floor(offer_dict)
        item["building_floors_num"] = self.parse_building_floors_num(offer_dict)
        item["rent"] = self.parse_rent(offer_dict)
        item["flat_type"] = self.parse_flat_type(offer_dict)
        item["ownership"] = self.parse_ownership(offer_dict)
        item["heating"] = self.parse_heating(offer_dict)
        item["number_of_rooms"] = self.parse_number_of_rooms(offer_dict)
        item["plot_type"] = self.parse_plot_type(offer_dict)
        # item["house_type"] = self.parse_house_type(offer_dict) if "Building_type" in offer_dict["target"] else None # do zbadania czym się różni od mieszkań
        item["garage_heating"] = self.parse_garage_heating(offer_dict)
        item["garage_lighted"] = self.parse_garage_lighted(offer_dict)
        item["garage_localization"] = self.parse_garage_localization(offer_dict)
        item["forest_vicinity"] = self.parse_forest_vicinity(offer_dict)
        item["lake_vicinity"] = self.parse_lake_vicinity(offer_dict)
        item["electricity"] = self.parse_electricity(offer_dict)
        item["gas"] = self.parse_gas(offer_dict)
        item["sewerage"] = self.parse_sewerage(offer_dict)
        item["water"] = self.parse_water(offer_dict)
        item[
            "fence"
        ] = None  # self.parse_fence(offer_dict)#do sprawdzenia jak to parsować
        item["build_year"] = self.parse_build_year(offer_dict)
        item["market_type"] = self.parse_market_type(offer_dict)
        item["construction_status"] = self.parse_construction_status(offer_dict)
        item["building_material"] = self.parse_building_material(offer_dict)

        # self.first_offer_detail=False

        yield item

    # def parse_property(self, response):
    #     result = otodom_get_parser(response)
    #     item = ScraperItem()
    #     item["price"] = result["price"]
    #     item["location"] = result["title"]
    #     yield item
    # property_loader = ItemLoader(item=ScraperItem(), response=response)
    # property_loader.default_output_processor = TakeFirst()

    # property_loader.add_css(
    #     "price", "span#ContentPlaceHolder1_DetailsFormView_Shillings::text"
    # )
    # property_loader.add_css(
    #     "location", "span#ContentPlaceHolder1_DetailsFormView_LocationLabel::text"
    # )

    # yield property_loader.load_item()
    def url_from_params(self, page=1, limit=24):
        path = otodom.get_url_path(self.search_form)
        query = otodom.url_query(self.search_form, page=page, limit=limit)
        return generate_url(
            scheme=self.scheme, netloc=self.domain, path=path, query=query
        )

    def get_results_num(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        print(
            'soup.find("strong",{"data-cy":"search.listing-panel.label.ads-number"})',
            soup.find("strong", {"data-cy": "search.listing-panel.label.ads-number"}),
        )
        # num_results = int(soup.find("strong",{"data-cy":"search.listing-panel.label.ads-number"}).span.next_sibling.next_sibling.text)
        num_results = int(
            soup.find(
                "strong", {"data-cy": "search.listing-panel.label.ads-number"}
            ).text.split()[-1]
        )
        return num_results

    def parse_service_id(self, service_id):
        if type(service_id) == int:
            return service_id
        else:
            print("uknown service id", service_id, type(service_id))
            return service_id

    def parse_floor(self, offer_dict):
        with suppress(Exception):
            m = re.search(r"floor_(\d+)", offer_dict["target"]["Floor_no"][0])
            if m:
                num = m.group(1)
                if num:
                    return int(num)

    def parse_house_type(self, offer_dict):
        if offer_dict["target"]["ProperType"] != "mieszkanie":
            return None
        try:
            house_type = offer_dict["target"]["Building_type"]
            house_type = house_type[0]
        except KeyError:
            house_type = None
        if house_type == "block":
            return Property.TypesOfFlats.BLOCK_OF_FLATS.value
        elif house_type == "tenement":
            return Property.TypesOfFlats.TENEMENT.value
        elif house_type == "apartment":
            return Property.TypesOfFlats.APARTMENT.value
        return house_type

    def parse_property_type(self, type):
        if type == "mieszkanie":
            return Property.TypesOfProperties.FLAT.value
        elif type == "dzialka":
            return Property.TypesOfProperties.PLOT.value
        else:
            return type

    def parse_flat_type(self, offer_dict):
        with suppress(Exception):
            if offer_dict["target"]["ProperType"] != "mieszkanie":
                return None
            house_type = offer_dict["target"]["Building_type"][0]
            if house_type == "block":
                return Property.TypesOfFlats.BLOCK_OF_FLATS.value
            elif house_type == "tenement":
                return Property.TypesOfFlats.TENEMENT.value
            elif house_type == "apartment":
                return Property.TypesOfFlats.APARTMENT.value
            return house_type

    def parse_plot_type(self, offer_dict):
        with suppress(Exception):
            if offer_dict["target"]["ProperType"] != "dzialka":
                return None

            type = offer_dict["target"]["Type"][0]
            if type == "building":
                return Property.TypesOfPlots.BUILDING.value
            elif type == "agricultural":
                return Property.TypesOfPlots.AGRICULTURAL.value
            elif type == "recreational":
                return Property.TypesOfPlots.RECREATIONAL.value
            elif type == "woodland":
                return Property.TypesOfPlots.FOREST.value
            return type

    def parse_regular_user(self, offer_dict):
        with suppress(Exception):
            if offer_dict["target"]["RegularUser"] == "n":
                return False
            elif offer_dict["target"]["RegularUser"] == "y":
                return True

    def parse_province(self, offer_dict):
        with suppress(Exception):
            if self.search_form["province"]:
                return self.search_form["province"]
            return offer_dict["location"]["address"]["province"]["code"]

    def parse_city(self, offer_dict):
        with suppress(Exception):
            if self.search_form["city"]:
                return self.search_form["city"]
            return offer_dict["location"]["address"]["city"]["code"]

    def parse_county(self, offer_dict):
        with suppress(Exception):
            if self.search_form["county"]:
                return self.search_form["county"]
            return offer_dict["location"]["address"]["county"]["code"]

    def parse_district(self, offer_dict):
        with suppress(Exception):
            if self.search_form["district"]:
                return self.search_form["district"]
            return offer_dict["location"]["address"]["district"]["code"]

    def parse_district_neighbourhood(self, offer_dict):
        with suppress(Exception):
            if self.search_form["district_neighbourhood"]:
                return self.search_form["district_neighbourhood"]
            return offer_dict["location"]["address"]["subdistrict"]["code"]

    def parse_street(self, offer_dict):
        with suppress(Exception):
            if offer_dict["location"]["address"]["street"]["id"]:
                if not ServiceFilterIds.objects.filter(
                        service_name="otodom",
                        field_name="streets",
                        service_id=offer_dict["location"]["address"]["street"]["id"],
                ):
                    ServiceFilterIds.objects.create(
                        service_name="otodom",
                        field_name="streets",
                        service_id=offer_dict["location"]["address"]["street"]["id"],
                    )
            if self.search_form["street"]:
                return self.search_form["street"]
            return offer_dict["location"]["address"]["street"]["code"]

    def parse_street_number(self, offer_dict):
        with suppress(Exception):
            return offer_dict["location"]["address"]["street"]["number"]

    def parse_latitude(self, offer_dict):
        with suppress(Exception):
            return offer_dict["location"]["coordinates"]["latitude"]

    def parse_longitude(self, offer_dict):
        with suppress(Exception):
            return offer_dict["location"]["coordinates"]["longitude"]

    def find_list_value(self, list, label, value):
        f"""
        l=[{'a': 1,'b':2},{'a':3,'b':4}]
        self.find_list_value(l,"a",1)
        >>>{'a': 1,'b':2}
        """
        with suppress(Exception):
            return next((x for x in list if label == value), None)["values"]

    def get_additionalInformation(self, offer_dict, label):
        with suppress(Exception):
            return self.find_list_value(
                offer_dict["additionalInformation"], "label", label
            )["values"]

    def get_characteristics(self, offer_dict, key):
        with suppress(Exception):
            return self.find_list_value(offer_dict["characteristics"], "key", key)[
                "value"
            ]

    def get_vicinity(self, offer_dict):
        with suppress(Exception):
            return self.get_additionalInformation(offer_dict, "vicinity_types")

    def parse_forest_vicinity(self, offer_dict):
        with suppress(Exception):
            return "forest" in self.get_vicinity(offer_dict)

    def parse_open_terrain_vicinity(self, offer_dict):
        with suppress(Exception):
            return "open_terrain" in self.get_vicinity(offer_dict)

    def parse_lake_vicinity(self, offer_dict):
        with suppress(Exception):
            return "lake" in self.get_vicinity(offer_dict)

    def get_media(self, offer_dict):
        with suppress(Exception):
            return self.get_additionalInformation(offer_dict, "media_types")

    def parse_electricity(self, offer_dict):
        with suppress(Exception):
            return "electricity" in self.get_media(offer_dict)

    def parse_gas(self, offer_dict):
        with suppress(Exception):
            return "gas" in self.get_media(offer_dict)

    def parse_sewerage(self, offer_dict):
        with suppress(Exception):
            return "sewerage" in self.get_media(offer_dict)

    def parse_water(self, offer_dict):
        with suppress(Exception):
            return "water" in self.get_media(offer_dict)

    # def parse_fence(self,offer_dict):
    #     with suppress(Exception):
    #         return "::n" in self.get_additionalInformation(offer_dict, "fence")

    def parse_garage_heating(self, offer_dict):
        with suppress(Exception):
            if self.search_form["property_type"] == "garage":
                ret = self.get_characteristics(offer_dict, "heating")
                if ret == "y":
                    return True
                elif ret == "n":
                    return False

    def parse_garage_lighted(self, offer_dict):
        with suppress(Exception):
            if self.search_form["property_type"] == "garage":
                ret = self.get_characteristics(offer_dict, "lighting")
                if ret == "y":
                    return True
                elif ret == "n":
                    return False

    def parse_garage_localization(self, offer_dict):
        with suppress(Exception):
            if self.search_form["property_type"] == "garage":
                type = self.get_characteristics(offer_dict, "localization")
                if type == "in_building":
                    return Property.TypesOfGarageLocalizations.IN_BUILDING.value
                elif type == "separate":
                    return Property.TypesOfGarageLocalizations.SEPARATE.value
                else:
                    return type

    def parse_number_of_rooms(self, offer_dict):
        with suppress(Exception):
            return int(offer_dict["target"]["Rooms_num"][0])

    def parse_building_floors_num(self, offer_dict):
        with suppress(Exception):
            return int(self.get_characteristics(offer_dict, "building_floors_num"))

    def parse_rent(self, offer_dict):
        with suppress(Exception):
            return float(self.get_characteristics(offer_dict, "rent"))

    def parse_ownership(self, offer_dict):
        with suppress(Exception):
            type = self.get_characteristics(offer_dict, "building_ownership")
            if type == "full_ownership":
                return Property.TypesOfOwnership.FULL_OWNERSHIP.value
            else:
                return type

    def parse_heating(self, offer_dict):
        # dodać sprawdzenie typu nieruchomości, korzysta z tego pola garage heating typu boolean

        with suppress(Exception):
            if not self.search_form["property_type"] == "garage":
                type = self.get_characteristics(offer_dict, "heating")
                if type == "urban":
                    return Property.TypesOfHeating.URBAN.value
                elif type == "gas":
                    return Property.TypesOfHeating.GAS.value
                else:
                    return str(type)

    def parse_build_year(self, offer_dict):
        with suppress(Exception):
            return int(self.get_characteristics(offer_dict, "build_year"))

    def parse_market_type(self, offer_dict):
        with suppress(Exception):
            type = self.get_characteristics(offer_dict, "market")
            if type == "primary":
                return Property.TypesOfMarket.PRIMARY.value
            elif type == "secondary":
                return Property.TypesOfMarket.SECONDARY.value
            else:
                return str(type)

    def parse_construction_status(self, offer_dict):
        with suppress(Exception):
            type = self.get_characteristics(offer_dict, "construction_status")
            if type == "ready_to_use":
                return Property.TypesOfConstructionStatus.READY.value
            elif type == "to_completion":
                return Property.TypesOfConstructionStatus.TO_COMPLETION.value
            else:
                return type

    def parse_building_material(self, offer_dict):
        return None
        with suppress(Exception):
            type = self.get_characteristics(offer_dict, "construction_status")
            if type == "ready_to_use":
                return Property.TypesOfConstructionStatus.READY.value
            elif type == "to_completion":
                return Property.TypesOfConstructionStatus.TO_COMPLETION.value
            else:
                return type
