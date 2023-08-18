from properties_scrapy.utils import *
from scrapy.spiders import Spider
from bs4 import BeautifulSoup
import math
import re
from datetime import datetime, date, timedelta
import chompjs
import json
from properties_scrapy.models import Property
from properties_scrapy.scrapy_project.spiders import morizon
from contextlib import suppress
from properties_scrapy.scrapy_project.items import ScrapyItem


class MorizonSpider(Spider):
    name = "morizon"
    service_name = "morizon"
    domain = "www.morizon.pl"
    scheme = "http"
    results_per_page = 35
    first_offer_detail = True
    max_pages_download = 5

    def __init__(self, *args, **kwargs):
        super(MorizonSpider, self).__init__(*args, **kwargs)
        search_form_json = kwargs.get("search_form", False)
        self.scrapyd_job_id = kwargs.get("_job")
        search_form = json.loads(search_form_json) if search_form_json else {}

        search_form = dict_filter_none(search_form)
        if search_form:
            # add pagination params
            search_form["limit"] = self.results_per_page
            search_form["page"] = 1

            self.search_form = search_form
            self.current_url = self.url_from_params()
            self.start_urls = [self.current_url]
        else:
            self.search_form = search_form
            self.query_params = ""
            self.current_url = ""
            self.start_urls = []

    def parse(self, response):
        parsed_url = url_to_params_dict(response.request.url)

        if not "page" in parsed_url:
            # print("morizon - not page in parsed_url")
            # return False
            parsed_url["page"]=1

        current_page = parsed_url["page"]
        if not current_page:
            print("morizon - not current_page")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        num_results = morizon.get_results_count(soup)
        if not num_results:
            print("morizon - unknown number of results")
            return False

        num_pages = math.ceil(num_results / self.results_per_page)
        num_pages = (
            self.max_pages_download
            if num_pages > self.max_pages_download
            else num_pages
        )

        if num_pages and int(current_page) == 1:
            for i in range(2, num_pages + 1):
                self.current_url = self.url_from_params(page=i)
                yield response.follow(self.current_url)

        js = next(
            filter(
                lambda t: '"@type":"OfferCatalog"' in t.text,
                soup.head.find_all(
                    "script", {"type": "application/ld+json", "data-n-head": "ssr"}
                ),
            )
        ).text
        data = chompjs.parse_js_object(js)
        for offer in data["itemListElement"]:
            yield response.follow(
                data["itemListElement"][offer]["url"], callback=self.parse_offer
            )

    def parse_offer(self, response):
        # if self.first_offer_detail:
        #     with open("/home/janek/python/property_scraper/test_data/morizon-details.html", "w") as file:
        #         file.write(response.text)
        soup = BeautifulSoup(response.text, "html.parser")
        # js=next(filter(lambda t: "PPDataLayer.push({" in t.text, soup.body.find_all("script", resursive=False))).text
        # data = chompjs.parse_js_object(js)
        detailed_information_set = soup.find_all(
            "div", {"class": "detailed-information__row"}
        )
        service_id_str = self.get_detail_information_text(
            detailed_information_set, "Numer ogłoszenia"
        )
        if service_id_str:
            if re.search("gratka|otodom|olx", service_id_str):
                # oferta z innego serwisu
                print("offer from diffrent service")
                return False
        # item = ScraperItem()
        details_row_set = soup.find("div", {"class": "details-row"}).find_all(
            "span", {"class": "details-row__text"}
        )

        attribute_list_set = soup.find_all("span", class_="attribute-list__label")
        item = ScrapyItem()
        item = localization_fields_from_search_form(item, self.search_form)

        item["scrapyd_job_id"] = self.scrapyd_job_id
        item["service_id"] = self.parse_service_id(service_id_str)
        item["service_name"] = self.service_name
        item["service_url"] = response.request.url

        item["create_date"] = self.parse_create_date(detailed_information_set)
        item["modify_date"] = self.parse_modify_date(detailed_information_set)

        item["title"] = self.parse_title(soup)
        item["price"] = self.parse_price(soup)
        item["description"] = self.parse_description(soup)
        item["area"] = self.parse_area(detailed_information_set)
        item["property_type"] = self.search_form["property_type"]
        item["offer_type"] = self.search_form["offer_type"]
        item["regular_user"] = self.parse_regular_user(soup)
        item["address"] = self.parse_address(soup)
        item["province"] = self.parse_province(soup)
        item["city"] = self.parse_city(soup)
        item["county"] = self.parse_county(soup)
        item["district"] = self.parse_district(soup)
        item["district_neighbourhood"] = self.parse_district_neighbourhood(soup)
        item["street"] = self.parse_street(soup)
        item["floor"] = self.parse_floor(detailed_information_set, details_row_set)
        item["building_floors_num"] = self.parse_building_floors_num(
            detailed_information_set
        )
        item["rent"] = None
        item["flat_type"] = self.parse_flat_type(detailed_information_set)
        item["ownership"] = self.parse_ownership(detailed_information_set)
        item["heating"] = self.parse_heating(detailed_information_set)
        item["number_of_rooms"] = self.parse_number_of_rooms(
            detailed_information_set, details_row_set
        )
        item["plot_type"] = self.parse_plot_type(detailed_information_set)
        item["house_type"] = self.parse_house_type(detailed_information_set)
        item["garage_heating"] = self.parse_garage_heating(detailed_information_set)
        item["garage_lighted"] = self.parse_garage_lighted(detailed_information_set)
        item["garage_localization"] = self.parse_garage_localization(
            detailed_information_set
        )
        item["forest_vicinity"] = self.parse_forest_vicinity(detailed_information_set)
        item["lake_vicinity"] = self.parse_lake_vicinity(detailed_information_set)
        item["electricity"] = self.parse_electricity(attribute_list_set)
        item["gas"] = self.parse_gas(attribute_list_set)
        item["sewerage"] = self.parse_sewerage(attribute_list_set)
        item["water"] = self.parse_water(attribute_list_set)
        item["basement"] = self.parse_basement(attribute_list_set)
        item["fence"] = self.parse_fence(attribute_list_set)
        item["build_year"] = self.parse_build_year(detailed_information_set)
        item["market_type"] = self.parse_market_type(detailed_information_set)
        item["construction_status"] = self.parse_construction_status(
            detailed_information_set
        )
        item["building_material"] = self.parse_building_material(
            detailed_information_set
        )

        yield item

    def url_from_params(self, page=1):
        path = morizon.get_url_path(self.search_form)
        query = morizon.get_url_query(self.search_form, page=page)
        return generate_url(
            scheme=self.scheme, netloc=self.domain, path=path, query=query
        )

    def parse_service_id(self, service_id_str):
        with suppress(Exception):
            return service_id_str

    def parse_title(self, soup):
        return None
        # with suppress(Exception):
        #     return soup.find("h3",{"class":"description__title"}).get_text("",strip=True)

    def parse_price(self, soup):
        try:
            return float(
                re.sub(
                    r"[^\d.,]",
                    "",
                    soup.find("span", {"class": "price-row__price"}).text,
                ).replace(",", ".")
            )
        except:
            return 0.0

    def parse_area(self, detailed_information_set):
        try:
            return float(
                re.sub(
                    r"[^\d.,]",
                    "",
                    self.get_detail_information_text(
                        detailed_information_set, "Pow. całkowita"
                    ),
                ).replace(",", ".")
            )
        except:
            return 0.0

    def parse_description(self, soup):
        with suppress(Exception):
            return soup.find("div", {"class": "description"}).get_text(
                "", strip=True
            )  # wczytuje tylko nagłówek

    def parse_address(self, soup):
        with suppress(Exception):
            str = soup.find("h2", class_="location-row__header").get_text(
                "", strip=True
            )
            if str:
                return str
            else:
                return self.search_form["address"]

    def parse_province(self, soup):
        with suppress(Exception):
            return self.search_form["province"]

    def parse_city(self, soup):
        with suppress(Exception):
            return self.search_form["city"]

    def parse_county(self, soup):
        with suppress(Exception):
            return self.search_form["county"]

    def parse_district(self, soup):
        with suppress(Exception):
            return self.search_form["district"]

    def parse_district_neighbourhood(self, soup):
        with suppress(Exception):
            return self.search_form["district_neighbourhood"]

    def parse_street(self, soup):
        with suppress(Exception):
            str = next(
                filter(
                    lambda _: "ul" in _,
                    soup.find("h2", class_="location-row__header")
                    .get_text("", strip=True)
                    .split(","),
                ),
                None,
            )
            if str:
                return str
            else:
                return self.search_form["street"]

    def parse_floor(self, detailed_information_set, details_row_set):
        # if self.search_form["property_type"] != "flat":
        #     return None
        try:
            floor_str = self.get_detail_information_text(
                detailed_information_set, "Piętro"
            ).split("/")[0]
            if floor_str in ["parter", "Parter"]:
                return 0
            else:
                return int(floor_str)
        except:
            # with suppress(Exception):
            f = next(
                filter(
                    lambda t: re.search("[pP]iętro|[pP]arter", t.text), details_row_set
                ),
                None,
            )
            if f:
                s = f.get_text("", strip=True)
                m = re.search("(\d+)/\d", s)
                if m:
                    return int(m.group(1))
                else:
                    m = re.search("[pP]arter", s)
                    if m:
                        return 0

    def parse_building_floors_num(self, detailed_information_set):
        with suppress(Exception):
            return int(
                self.get_detail_information_text(
                    detailed_information_set, "Liczba pięter"
                )
            )

    def parse_number_of_rooms(self, detailed_information_set, details_row_set):
        with suppress(Exception):
            # if self.search_form["property_type"] != "flat":
            #     return None
            f = next(
                filter(lambda t: re.search("[pP]ok", t.text), details_row_set), None
            )
            if f:
                s = f.get_text("", strip=True)
                m = re.search("(\d+)", s)
                if m:
                    return int(m.group(1))

    def parse_flat_type(self, detailed_information_set):
        with suppress(Exception):
            if self.search_form["property_type"] != "flat":
                return None
            type = self.get_detail_information_text(
                detailed_information_set, "Typ budynku"
            )
            if not type:
                return None
            type = type.lower()
            if type == "blok":
                return Property.TypesOfFlats.BLOCK_OF_FLATS.value
            elif type == "kamienica":
                return Property.TypesOfFlats.TENEMENT.value
            elif type == "apartamentowiec":
                return Property.TypesOfFlats.APARTMENT.value
            return type

    def parse_house_type(self, detailed_information_set):
        with suppress(Exception):
            house_type = self.get_detail_information_text(
                detailed_information_set, "Typ domu"
            )
            if not house_type:
                return None
            house_type = house_type.lower()
            if house_type == "wolnostojący" or house_type == "rezydencja":
                return Property.TypesOfHouses.DETACHED_HOUSE.value
            elif house_type == "bliźniak":
                return Property.TypesOfHouses.SEMI_DETACHED_HOUSE.value
            elif house_type == "segment":
                return Property.TypesOfHouses.TERRACED_HOUSE.value
            return house_type

    def parse_plot_type(self, detailed_information_set):
        with suppress(Exception):
            if self.search_form["property_type"] != "plot":
                return None
            type = self.get_detail_information_text(
                detailed_information_set, "Typ działki"
            ).lower()
            if type == "budowlana":
                return Property.TypesOfPlots.BUILDING.value
            elif type == "rolna":
                return Property.TypesOfPlots.AGRICULTURAL.value
            elif type == "rekreacyjna":
                return Property.TypesOfPlots.RECREATIONAL.value
            elif type == "leśna":
                return Property.TypesOfPlots.FOREST.value
            return type

    def get_attribute_list_set_text(self, attribute_list_set, label):
        with suppress(Exception):
            return next(filter(lambda t: label in t.text, attribute_list_set)).text

    def get_detail_information_text(self, detailed_information_set, label):
        with suppress(Exception):
            f = filter(lambda t: label in t.text, detailed_information_set)
            if f:
                return (
                    next(f)
                    .find(
                        "div",
                        {
                            "class": "detailed-information__cell detailed-information__cell--value"
                        },
                    )
                    .div.get_text("", strip=True)
                )

    # def get_details_row_text(self, details_row_set,label):
    #     with suppress(Exception):
    #         f=next(filter(lambda t: re.search('[pP]iętro|[pP]arter]',t.text),details_row_set),None)
    #         if f:
    #             return
    #         return next(filter(lambda t: label in t.text,detailed_information_set),None).find("div",{"class":"detailed-information__cell detailed-information__cell--value"}).div.text

    def parse_regular_user(self, soup):
        try:
            return (
                soup.find("span", class_="contact-person__position").get_text(
                    "", strip=True
                )
                == "osoba prywatna"
            )
        except:
            return False

    def parse_create_date(self, detailed_information_set):
        return self.parse_date(detailed_information_set, "Data dodania")

    def parse_modify_date(self, detailed_information_set):
        return self.parse_date(detailed_information_set, "Aktualizacja")

    def parse_date(self, detailed_information_set, label):
        with suppress(Exception):
            d = self.get_detail_information_text(detailed_information_set, label)
            if d:
                return datetime.strptime(d, "%d.%m.%Y")

    def parse_ownership(self, detailed_information_set):
        with suppress(Exception):
            t = self.get_detail_information_text(
                detailed_information_set, "Forma własności"
            )
            if t == "Własność":
                return Property.TypesOfOwnership.FULL_OWNERSHIP.value
            else:
                return t

    def parse_heating(self, detailed_information_set):
        with suppress(Exception):
            type = self.get_detail_information_text(
                detailed_information_set, "Ogrzewanie"
            )
            if type == "Miejskie":
                return Property.TypesOfHeating.URBAN.value
            elif type == "Gazowe" or type == "CO gazowe":
                return Property.TypesOfHeating.GAS.value
            else:
                return type

    def parse_garage_heating(self, detailed_information_set):
        return None

    def parse_garage_lighted(self, detailed_information_set):
        return None

    def parse_garage_localization(self, detailed_information_set):
        with suppress(Exception):
            t = self.get_detail_information_text(
                detailed_information_set, "Lokalizacja garażu"
            )
            if t == "W budynku":
                return Property.TypesOfGarageLocalizations.IN_BUILDING.value
            elif t == "Samodzielny":
                return Property.TypesOfGarageLocalizations.SEPARATE.value
            else:
                return t

    def parse_forest_vicinity(self, detailed_information_set):
        return None

    def parse_lake_vicinity(self, detailed_information_set):
        return None

    def parse_electricity(self, attribute_list_set):
        with suppress(Exception):
            f = self.get_attribute_list_set_text(attribute_list_set, "Prąd")
            if "BRAK" in f:
                return False
            elif f:
                return True

    def parse_gas(self, attribute_list_set):
        with suppress(Exception):
            f = self.get_attribute_list_set_text(attribute_list_set, "Gaz")
            if "BRAK" in f:
                return False
            elif f:
                return True

    def parse_water(self, attribute_list_set):
        with suppress(Exception):
            f = self.get_attribute_list_set_text(attribute_list_set, "Woda")
            if "BRAK" in f:
                return False
            elif f:
                return True

    def parse_sewerage(self, attribute_list_set):
        with suppress(Exception):
            f = self.get_attribute_list_set_text(attribute_list_set, "Kanalizacja")
            if "BRAK" in f:
                return False
            elif f:
                return True

    def parse_fence(self, attribute_list_set):
        with suppress(Exception):
            f = self.get_attribute_list_set_text(attribute_list_set, "Ogrodzenie")
            if "BRAK" in f:
                return False
            elif f:
                return True

    def parse_basement(self, attribute_list_set):
        with suppress(Exception):
            f = self.get_attribute_list_set_text(attribute_list_set, "Piwnica")
            if "BRAK" in f:
                return False
            elif f:
                return True

    def parse_build_year(self, detailed_information_set):
        with suppress(Exception):
            return int(
                self.get_detail_information_text(detailed_information_set, "Rok budowy")
            )

    def parse_market_type(self, detailed_information_set):
        with suppress(Exception):
            t = self.get_detail_information_text(detailed_information_set, "Rynek")
            if t == "Pierwotny":
                return Property.TypesOfMarket.PRIMARY.value
            elif t == "Wtórny":
                return Property.TypesOfMarket.SECONDARY.value
            else:
                return str(t)

    def parse_construction_status(self, detailed_information_set):
        return None

    def parse_building_material(self, detailed_information_set):
        with suppress(Exception):
            t = self.get_detail_information_text(
                detailed_information_set, "Materiał budowlany"
            )
            if t == "Cegła":
                return Property.TypesOfBuildingMaterials.BRICK.value
            if t == "Wielka płyta":
                return Property.TypesOfBuildingMaterials.GREAT_SLAB.value
            else:
                return t
