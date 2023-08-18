from properties_scrapy.utils import *
from scrapy.spiders import Spider
from scrapy import Request
import math
import re
from datetime import date, timedelta
import chompjs
import json
# from otodom import *
from properties_scrapy.models import Property
from properties_scrapy.scrapy_project.spiders import gratka
from contextlib import suppress
from properties_scrapy.scrapy_project.items import ScrapyItem


class GratkaSpider(Spider):
    name = "gratka"
    service_name = "gratka"
    domain = "gratka.pl"
    scheme = "http"
    results_per_page = 32
    first_offer_detail = True
    max_pages_download = 5

    def __init__(self, *args, **kwargs):
        super(GratkaSpider, self).__init__(*args, **kwargs)
        search_form_json = kwargs.get("search_form", False)
        self.scrapyd_job_id = kwargs.get("_job")
        search_form = json.loads(search_form_json) if search_form_json else {}

        search_form = dict_filter_none(search_form)
        print('\\\\\\\\\\\\\\\\ search form', search_form)
        if search_form:
            # add pagination params
            search_form["limit"] = self.results_per_page
            search_form["page"] = 1
            self.use_playwright = "district_neighbourhood" in search_form
            self.search_form = search_form
            self.current_url = self.url_from_params()
            print('\\\\\\\\\\\\\\\\ current_url', self.current_url)
            self.start_urls = [self.current_url]
        else:
            self.search_form = search_form
            self.query_params = ""
            self.current_url = ""
            self.start_urls = []

    def start_requests(self):
        if self.use_playwright:
            for url in self.start_urls:
                selenium = selenium_browser()
                selenium.get(url)
                selenium.implicitly_wait(3)
                # selenium.save_screenshot("../test_data/gratka/gratka1.png")
                selenium.find_element(
                    "css selector", "button.cmp-intro_acceptAll"
                ).click()
                selenium.find_element(
                    "css selector", "i.locationSuggester__eraser"
                ).click()
                selenium.find_element(
                    "css selector", 'input[name="lokalizacja_region"]'
                ).send_keys(self.search_form["address"])
                selenium.find_element(
                    "css selector", "ul.category__results li:first-child"
                ).click()
                selenium.find_element("css selector", "body").click()
                # selenium.implicitly_wait(5)
                # selenium.save_screenshot("../test_data/gratka/gratka2.png")
                selenium.find_element(
                    "css selector", 'button[data-cy="submitSearch"]'
                ).click()
                # selenium.save_screenshot("../test_data/gratka/gratka3.png")
                print("selenium.current_url", selenium.current_url)
                new_url = selenium.current_url + "&page=1"
                selenium.close()
                yield Request(url=new_url)
        else:
            for url in self.start_urls:
                yield Request(url=url)

    def parse(self, response):
        parsed_url_query = url_to_params_dict(response.request.url)

        if not "page" in parsed_url_query:
            print("gratka - not page in parsed_url")
            return False

        current_page = parsed_url_query["page"]
        if not current_page:
            print("gratka - not current_page")
            return False

        url_path = get_url_path(response.request.url)
        district_neighbourhood_cand = url_path.split("/")[-1]
        if re.search(r"[a-z]+\-\d+", district_neighbourhood_cand):
            self.search_form[
                "district_neighbourhood_from_url"
            ] = district_neighbourhood_cand

        soup = BeautifulSoup(response.text, "html.parser")

        num_results = gratka.get_results_count(soup)
        if not num_results:
            return False

        # results_per_page = 24
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

        m = re.search(r"allOffersIds \= \[((\d+,)*\d+)\]", response.text)
        offers_ids = list(set((m.group(1).split(","))))
        property_type = gratka.property_type_mapping[self.search_form["property_type"]]
        domain = generate_url(
            scheme=self.scheme,
            netloc=self.domain,
            path=f"/nieruchomosci/{property_type}/ob/",
        )
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
        #     with open("/home/janek/python/property_scraper/test_data/gratka-details.html", "w") as file:
        #         file.write(response.text)
        soup = BeautifulSoup(response.text, "html.parser", from_encoding="utf-8")
        js = next(
            filter(
                lambda t: "PPDataLayer.push({" in t.text,
                soup.body.find_all("script", resursive=False),
            )
        ).text
        data = chompjs.parse_js_object(js)
        try:
            js2 = next(
                filter(
                    lambda t: "@graph" in t.text,
                    soup.find_all(
                        "script", {"type": "application/ld+json"}, resursive=False
                    ),
                )
            ).text
            data2 = chompjs.parse_js_object(js2)["@graph"][0]
        except:
            data2 = None

        item = ScrapyItem()

        item = localization_fields_from_search_form(item, self.search_form)

        item["scrapyd_job_id"] = self.scrapyd_job_id
        item["service_id"] = self.parse_service_id(data)
        item["service_name"] = self.service_name
        item["service_url"] = response.request.url

        item["create_date"] = self.parse_create_date(soup)
        item["modify_date"] = self.parse_modify_date(soup)

        item["title"] = self.parse_title(data2)
        item["price"] = data["cena"]
        item["description"] = self.parse_description(data2)
        item["area"] = self.parse_area(data, soup)
        item["property_type"] = self.search_form["property_type"]
        item["offer_type"] = self.search_form["offer_type"]
        item["regular_user"] = self.parse_regular_user(soup)
        item["address"] = self.parse_address(soup)
        item["province"] = self.parse_province(data, data2)
        item["city"] = self.parse_city(data, data2)
        item["county"] = self.parse_county(soup)
        item["district"] = self.parse_district(soup)
        item["district_neighbourhood"] = self.parse_district_neighbourhood(soup)
        item["street"] = self.parse_street(data2)
        item["floor"] = self.parse_floor(data2)
        item["building_floors_num"] = self.parse_building_floors_num(soup)
        item["rent"] = self.parse_rent()
        item["flat_type"] = self.parse_flat_type(data2)
        item["ownership"] = self.parse_ownership(soup)
        item["heating"] = self.parse_heating()
        item["number_of_rooms"] = self.parse_number_of_rooms(data2)
        item["plot_type"] = self.parse_plot_type(data)
        item["house_type"] = self.parse_house_type(soup)
        item["garage_heating"] = self.parse_garage_heating(soup)
        item["garage_lighted"] = self.parse_garage_lighted(soup)
        item["garage_localization"] = self.parse_garage_localization(soup)
        item["forest_vicinity"] = self.parse_forest_vicinity()
        item["lake_vicinity"] = self.parse_lake_vicinity()
        item["electricity"] = self.parse_electricity(soup)
        item["gas"] = self.parse_gas(soup)
        item["sewerage"] = self.parse_sewerage(soup)
        item["water"] = self.parse_water(soup)
        item["basement"] = self.parse_basement(soup)
        item["fence"] = self.parse_fence(soup)
        item["build_year"] = self.parse_build_year(data2)
        item["market_type"] = self.parse_market_type(data)
        item["construction_status"] = self.parse_construction_status(soup)
        item["building_material"] = self.parse_building_material(soup)
        item["latitude"] = self.parse_latitude(data2)
        item["longitude"] = self.parse_longitude(data2)

        yield item

    def url_from_params(self, page=1):
        path = gratka.get_url_path(self.search_form)
        query = gratka.get_url_query(self.search_form, page=page)
        return generate_url(
            scheme=self.scheme, netloc=self.domain, path=path, query=query
        )

    def parse_service_id(self, data):
        with suppress(Exception):
            return str(data["id_oferty"])

    def parse_title(self, data2):
        print("///////////////////", data2)
        with suppress(Exception):
            return data2["name"]

    def parse_description(self, data2):
        with suppress(Exception):
            return data2["description"]

    def parse_area(self, data, soup):
        if "powierzchnia_m2" in data:
            return data["powierzchnia_m2"]
        else:
            _ = self.get_parameter_value(soup, "Powierzchnia działki w m2")
            if _:
                if re.search("^([\d\s\.\,]+) m2", _):
                    return float(re.search("^([\d\s\.\,]+) m2", _).group(1))
        return 0.0

    def parse_flat_type(self, data2):
        if self.search_form["property_type"] != "flat":
            return None
        house_type = data2["@type"]
        if house_type == "Apartment":
            return Property.TypesOfFlats.BLOCK_OF_FLATS.value
        elif house_type == "tenement":
            return Property.TypesOfFlats.TENEMENT.value
        elif house_type == "apartment":
            return Property.TypesOfFlats.APARTMENT.value
        return house_type

    def parse_property_type(self, type):
        if type == "mieszkania":
            return Property.TypesOfProperties.FLAT.value
        elif type == "dzialki-grunty":
            return Property.TypesOfProperties.PLOT.value
        else:
            return type

    def parse_plot_type(self, data):
        with suppress(Exception):
            if self.search_form["property_type"] != "plot":
                return None
            if "plot_type" in self.search_form:
                return self.search_form["plot_type"]
            t = data["kat_pelna"].split("_")[-1]
            if t == "budowlana":
                return Property.TypesOfPlots.BUILDING.value
            elif t == "rolna":
                return Property.TypesOfPlots.AGRICULTURAL.value
            elif t == "rekreacyjna":
                return Property.TypesOfPlots.RECREATIONAL.value
            elif t == "lesna":
                return Property.TypesOfPlots.FOREST.value
            return t

    def parse_create_date(self, soup):
        return self.parse_date(soup, "Dodane")

    def parse_modify_date(self, soup):
        return self.parse_date(soup, "Zaktualizowane")

    def parse_date(self, soup, str):
        with suppress(Exception):
            date_str = next(
                filter(lambda t: str in t.text, soup.find_all("li"))
            ).div.get_text("", strip=True)
            if date_str == "dziś":
                return date.today()
            elif date_str == "wczoraj":
                return date.today() + timedelta(days=-1)
            elif re.search("^(\d+) dni temu$", date_str):
                offset = int(re.search("^(\d+) dni temu$", date_str).group(1))
                return date.today() + timedelta(days=-offset)
            elif date_str == "ponad dwa tygodnie temu":
                return date.today() + timedelta(days=-14)
            elif date_str == "ponad miesiąc temu":
                return date.today() + timedelta(days=-31)
            elif date_str == "ponad pół roku temu":
                return date.today() + timedelta(days=-183)
            else:
                return None

    def parse_address(self, soup):
        with suppress(Exception):
            str = soup.find("div", id="localizationModalAddress").get_text(
                " ", strip=True
            )
            if str:
                return str
            else:
                return self.search_form["address"]

    def parse_province(self, data, data2):
        with suppress(Exception):
            if "province" in self.search_form:
                return self.search_form["province"]
            if "region" in data:
                return data["region"]
            return data2["address"]["addressRegion"]

    def parse_city(self, data, data2):
        with suppress(Exception):
            if "city" in self.search_form:
                return self.search_form["city"]
            if "miejscowosc" in data:
                return data["miejscowosc"]
            return data2["address"]["addressLocality"]

    def parse_county(self, soup):
        with suppress(Exception):
            return self.search_form["county"]

    def parse_district(self, soup):
        with suppress(Exception):
            return self.search_form["district"]

    def parse_district_neighbourhood(self, soup):
        with suppress(Exception):
            return self.search_form["district_neighbourhood"]

    def parse_street(self, data2):
        with suppress(Exception):
            if "street" in self.search_form:
                return self.search_form["street"]
            return data2["address"]["streetAddress"]

    def parse_floor(self, data2):
        with suppress(Exception):
            return data2["floorLevel"]

    def parse_building_floors_num(self, soup):
        with suppress(Exception):
            return int(self.get_parameter_value(soup, "Liczba pięter w budynku"))

    def parse_number_of_rooms(self, data2):
        with suppress(Exception):
            return data2["numberOfRooms"]

    def parse_house_type(self, soup):
        if self.search_form["property_type"] != "house":
            return None
        with suppress(Exception):
            house_type = self.get_parameter_value(soup, "Typ budynku")
            if not house_type:
                return None
            if house_type == "wolnostojący" or house_type == "rezydencja":
                return Property.TypesOfHouses.DETACHED_HOUSE.value
            elif house_type == "bliźniak":
                return Property.TypesOfHouses.SEMI_DETACHED_HOUSE.value
            elif house_type == "segment":
                return Property.TypesOfHouses.TERRACED_HOUSE.value
            return house_type

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
        with suppress(Exception):
            if soup.find("h3", class_="offerOwner__company"):
                return False
            elif soup.find("h3", class_="offerOwner__person"):
                return True

    def parameters_set(self, soup):
        with suppress(Exception):
            return soup.find("ul", class_="parameters__singleParameters").find_all("li")

    def grouped_parameters_set(self, soup):
        with suppress(Exception):
            return soup.find("ul", class_="parameters__groupedParameters").find_all(
                "li"
            )

    def get_parameter_value(self, soup, label):
        with suppress(Exception):
            return next(
                filter(lambda _: label in _.span.text, self.parameters_set(soup))
            ).b.get_text("", strip=True)

    def get_grouped_parameter_value(self, soup, label):
        with suppress(Exception):
            return next(
                filter(lambda _: label in _.text, self.grouped_parameters_set(soup))
            ).text

    def parse_ownership(self, soup):
        with suppress(Exception):
            t = self.get_parameter_value(soup, "Forma własności")
            if t == "własność":
                return Property.TypesOfOwnership.FULL_OWNERSHIP.value
            elif t == "spółdzielcze własnościowe z KW":
                return Property.TypesOfOwnership.COOPERATIVE_OWNERSHIP.value
            else:
                return t

    def parse_rent(self):
        return None

    def parse_heating(self):
        return None

    def parse_garage_heating(self, soup):
        return None

    def parse_garage_lighted(self, soup):
        with suppress(Exception):
            if self.get_grouped_parameter_value(soup, "oświetlenie"):
                return True

    def parse_garage_localization(self, soup):
        if self.search_form["property_type"] != "garage":
            return None
        with suppress(Exception):
            t = self.get_parameter_value(soup, "Położenie")
            if t == "W budynku":
                return Property.TypesOfGarageLocalizations.IN_BUILDING.value
            elif t == "miejsce parkingowe w hali garażowej":
                return Property.TypesOfGarageLocalizations.SEPARATE.value
            else:
                return t

    def parse_forest_vicinity(self):
        return None

    def parse_lake_vicinity(self):
        return None

    def parse_electricity(self, soup):
        with suppress(Exception):
            f = self.get_parameter_value(soup, "Prąd").lower()
            if "brak" in f:
                return False
            elif f:
                return True

    def parse_gas(self, soup):
        with suppress(Exception):
            f = self.get_parameter_value(soup, "Gaz").lower()
            if "brak" in f:
                return False
            elif f:
                return True

    def parse_water(self, soup):
        with suppress(Exception):
            f = self.get_parameter_value(soup, "Woda").lower()
            if "brak" in f:
                return False
            elif f:
                return True

    def parse_sewerage(self, soup):
        with suppress(Exception):
            f = self.get_parameter_value(soup, "Kanalizacja").lower()
            if "brak" in f:
                return False
            elif f:
                return True

    def parse_fence(self, soup):
        with suppress(Exception):
            f = self.get_parameter_value(soup, "Ogrodzenie działki").lower()
            if "brak" in f:
                return False
            elif f:
                return True

    def parse_basement(self, soup):
        with suppress(Exception):
            if self.get_grouped_parameter_value(soup, "piwnica"):
                return True
            _ = self.get_parameter_value(soup, "Podpiwniczenie")
            if _ == "brak":
                return False
            elif _:
                return True

    def parse_build_year(self, data2):
        with suppress(Exception):
            return data2["yearBuilt"]

    def parse_market_type(self, data):
        with suppress(Exception):
            _ = data["rynek"]
            if _ == "pierwotny":
                return Property.TypesOfMarket.PRIMARY.value
            elif _ == "wtorny":
                return Property.TypesOfMarket.SECONDARY.value

    def parse_construction_status(self, soup):
        with suppress(Exception):
            _ = self.get_parameter_value(soup, "Stan")
            if _ == "wykończony":
                return Property.TypesOfConstructionStatus.READY

    def parse_building_material(self, soup):
        with suppress(Exception):
            t = self.get_parameter_value(soup, "Materiał budynku")
            if t == "cegła":
                return Property.TypesOfBuildingMaterials.BRICK.value
            if t == "wielka płyta":
                return Property.TypesOfBuildingMaterials.GREAT_SLAB.value
            else:
                return t

    def parse_latitude(self, data2):
        with suppress(Exception):
            return data2["geo"]["latitude"]

    def parse_longitude(self, data2):
        with suppress(Exception):
            return data2["geo"]["longitude"]
