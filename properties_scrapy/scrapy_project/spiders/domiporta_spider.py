import os
from properties_scrapy.utils import *
from scrapy.spiders import Spider
import math
import re
import chompjs
import json
from properties_scrapy.models import Property
from properties_scrapy.scrapy_project.spiders import domiporta
from contextlib import suppress
from properties_scrapy.scrapy_project.items import ScrapyItem


class DomiportaSpider(Spider):
    name = "domiporta"
    service_name = "domiporta"
    domain = "www.domiporta.pl"
    scheme = "http"
    results_per_page = 35
    first_offer_detail = True
    max_pages_download = 5

    def __init__(self, *args, **kwargs):
        self.is_testing = kwargs.pop('is_testing', False)
        super(DomiportaSpider, self).__init__(*args, **kwargs)

        search_form_json = kwargs.get("search_form", False)
        self.scrapyd_job_id = kwargs.get("_job")
        search_form = json.loads(search_form_json) if search_form_json else {}

        search_form = dict_filter_none(search_form)
        if search_form:
            # add pagination params
            search_form["limit"] = self.results_per_page
            search_form["PageNumber"] = 1

            self.search_form = search_form
            self.current_url = self.url_from_params()
            self.start_urls = [self.current_url]
        else:
            self.search_form = search_form
            self.query_params = ""
            self.current_url = ""
            self.start_urls = []

        if self.is_testing:
            print('Kod wykonywany w trybie testowym')
            path=f"file://{os.path.abspath('../test_data/domiporta/domiporta-search.html')}"
            self.current_url = path
            self.start_urls = [path]

        print('DomiportaSpider __init__ start_urls', self.start_urls)
        print('DomiportaSpider __init__ current_url', self.current_url)


    def parse(self, response):
        with open("../test_data/domiporta-search-2.html", "w") as file:
            file.write(response.text)
        if self.is_testing:
            parsed_url = url_to_params_dict("http://www.domiporta.pl/mieszkanie/sprzedam/mazowieckie/grodzisk-mazowiecki?PageNumber=1&Price.From=300000&Price.To=400000")
        else:
            parsed_url = url_to_params_dict(response.request.url)

        if not "PageNumber" in parsed_url:
            print("domiporta - not page in parsed_url")
            return False

        current_page = parsed_url["PageNumber"]
        if not current_page:
            print("domiporta - not current_page")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        try:
            num_results = domiporta.get_results_count(soup)
        except:
            num_results = 0

        if not num_results:
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

        ids_raw = re.findall(r"WynikiOdslonaOgloszeniaOrganic'\, ((?:'a.*\d+'\,?)+)", str(soup))
        if not ids_raw:
            #trzeba by parsować kod html żeby wyciągnąć urle ofert
            return None
        ids_str = ids_raw[0]
        ids_list=ids_str.split(",")
        ids = [re.search(r'\d+', _).group() for _ in ids_list if '/DPRP/' not in _]
        # js = re.findall(
        #     r"WynikiOdslonaOgloszeniaOrganic'\, ((?:'a\d+'\,?)+)", soup.prettify(), re.MULTILINE
        # )
        # ids = re.findall("\d+", js[0])
        property_type = domiporta.property_type_mapping[
            self.search_form["property_type"]
        ]
        url = generate_url(
            scheme=self.scheme,
            netloc=self.domain,
            path=f"/nieruchomosci/{property_type}/",
        )
        if self.is_testing:
            print('Kod DomiportaSpider parse wykonywany w trybie testowym')
            path = f"file://{os.path.abspath('../test_data/domiporta/domiporta-details.html')}"
            yield response.follow(path, callback=self.parse_offer)
        else:
            for offer in ids:
                yield response.follow(url + offer, callback=self.parse_offer)

    def parse_offer(self, response):
        if self.first_offer_detail:
            with open("../test_data/domiporta-details-2.html", "w") as file:
                file.write(response.text)
        # if self.first_offer_detail:
        #     with open("/home/janek/python/property_scraper/test_data/domiporta-details.html", "w") as file:
        #         file.write(response.text)
        soup = BeautifulSoup(response.text, "html.parser")

        features_list = soup.find("ul", {"class": "features__list-2"}).find_all("li")
        try:
            js = next(
                filter(
                    lambda _: "dataLayer" in _.text,
                    soup.head.find_all("script", resursive=False),
                )
            ).text
            js_obj = js[
                js.index("dataLayer = [") + len("dataLayer = [") : js.index("];\n")
            ]
            js_obj_clean = js_obj.replace(
                "'mailHash': userHash != null && userHash != '' ? userHash : '',", ""
            )
            data = chompjs.parse_js_object(js_obj_clean)
            additional_info = re.split(
                ",\s?",
                ",".join(
                    map(
                        lambda _: _.text,
                        soup.find_all("dd", class_="features__item_value"),
                    )
                ),
            )
        except:
            data = None
            additional_info = None

        # item = {}
        item = ScrapyItem()
        item = localization_fields_from_search_form(item, self.search_form)

        item["scrapyd_job_id"] = self.scrapyd_job_id
        item["service_id"] = self.parse_service_id(response.request.url)
        item["service_name"] = self.service_name
        item["service_url"] = response.request.url

        item["create_date"] = None
        item["modify_date"] = None

        item["title"] = self.parse_title(soup)
        item["price"] = self.parse_price(soup, data)
        item["description"] = self.parse_description(soup)
        item["area"] = self.parse_area(features_list, data)
        item["property_type"] = self.search_form["property_type"]
        item["offer_type"] = self.search_form["offer_type"]
        item["regular_user"] = self.parse_regular_user(soup, data)
        item["address"] = self.parse_address(soup)
        item["province"] = self.parse_province(data)
        item["city"] = self.parse_city(data)
        # item["county"]=self.parse_county(soup)
        # item["district"]=self.parse_district(soup)
        # item["district_neighbourhood"]=self.parse_district_neighbourhood(soup)
        # item["street"]=self.parse_street(data2)
        item["floor"] = self.parse_floor(features_list)
        item["building_floors_num"] = self.parse_building_floors_num(features_list)
        item["rent"] = self.parse_rent(features_list)
        item["flat_type"] = self.parse_flat_type(features_list)
        item["ownership"] = self.parse_ownership(features_list)
        item["heating"] = self.parse_heating(additional_info)
        item["number_of_rooms"] = self.parse_number_of_rooms(features_list)
        item["plot_type"] = self.parse_plot_type(features_list)
        item["house_type"] = self.parse_house_type(features_list)
        item["garage_heating"] = None
        item["garage_lighted"] = None
        item["garage_localization"] = None
        item["forest_vicinity"] = self.parse_forest_vicinity(additional_info)
        item["lake_vicinity"] = self.parse_lake_vicinity(additional_info)
        item["electricity"] = self.parse_electricity(features_list)
        item["gas"] = self.parse_gas(features_list)
        item["sewerage"] = self.parse_sewerage(features_list)
        item["water"] = self.parse_water(features_list)
        item["basement"] = None
        item["fence"] = self.parse_fence(features_list)
        item["build_year"] = self.parse_build_year(features_list)
        item["market_type"] = self.parse_market_type(data)
        item["construction_status"] = None
        item["building_material"] = self.parse_building_material(features_list)
        # item["latitude"]=self.parse_latitude(data2)
        # item["longitude"]=self.parse_longitude(data2)

        yield item

    def url_from_params(self, page=1):
        path = domiporta.get_url_path(self.search_form)
        query = domiporta.get_url_query(self.search_form, page=page)
        return generate_url(
            scheme=self.scheme, netloc=self.domain, path=path, query=query
        )

    def get_feature_value(self, features_list, label):
        with suppress(Exception):
            return (
                next(filter(lambda _: label in _.text, features_list), None)
                .find("span", {"class": "features__item_value"})
                .get_text("", strip=True)
            )

    def parse_service_id(self, url):
        with suppress(Exception):
            return url.split("/")[-1]

    def parse_price(self, soup, data):
        try:
            if data:
                if "price" in data:
                    return float(data["price"])
            return float(soup.find("span", {"itemprop": "price"})["content"])
        except:
            return 0.0

    def parse_area(self, features_list, data):
        try:
            if data:
                if "surface" in data:
                    return float(data["surface"])
            return float(
                re.sub(
                    r"[^\d.,]",
                    "",
                    list(
                        next(
                            filter(
                                lambda _: "Powierzchnia całkowita" in _.text,
                                features_list,
                            )
                        ).strings
                    )[1],
                ).replace(",", ".")
            )
        except:
            return 0.0

    def parse_title(self, soup):
        with suppress(Exception):
            return soup.find("span", {"class": "summary__subtitle-2"}).get_text(
                "", strip=True
            )

    def parse_description(self, soup):
        with suppress(Exception):
            return soup.find("div", {"class": "description__panel"}).get_text(
                "", strip=True
            )

    def parse_address(self, soup):
        with suppress(Exception):
            return soup.find("div", {"class": "detials__map__location"}).get_text(
                "", strip=True
            )

    def parse_province(self, data):
        with suppress(Exception):
            if "province" in self.search_form:
                return self.search_form["province"]
            elif data and "region" in data:
                return data["region"]

    def parse_city(self, data):
        with suppress(Exception):
            if "city" in self.search_form:
                return self.search_form["city"]
            elif data and "city" in data:
                return data["city"]

    def parse_floor(self, features_list):
        if self.search_form["property_type"] != "flat":
            return None
        try:
            _ = self.get_feature_value(features_list, "Piętro")
            if _ in ["parter", "Parter"]:
                return 0
            else:
                return int(_)
        except:
            with suppress(Exception):
                f = next(
                    filter(
                        lambda t: re.search("[pP]iętro|[pP]arter]", t.text),
                        features_list,
                    ),
                    None,
                )
                if f:
                    s = f.get_text("", strip=True)
                    m = re.search("(\d+)/\d", s)
                    if m:
                        return int(m.group(1))
                    else:
                        m = re.search("[pP]arter]", s)
                        if m:
                            return 0

    def parse_building_floors_num(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Liczba pięter w budynku")
            if _ in ["parter", "Parter"]:
                return 0
            else:
                return int(_)

    def parse_number_of_rooms(self, features_list):
        if self.search_form["property_type"] != "flat":
            return None
        with suppress(Exception):
            return int(self.get_feature_value(features_list, "Liczba pokoi"))

    def parse_rent(self, features_list):
        with suppress(Exception):
            return float(self.get_feature_value(features_list, "Czynsz"))

    def parse_build_year(self, features_list):
        with suppress(Exception):
            return int(self.get_feature_value(features_list, "Rok budowy"))

    def parse_building_material(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Materiał")
            if _ == "cegła":
                return Property.TypesOfBuildingMaterials.BRICK.value
            elif _ == "wielka płyta":
                return Property.TypesOfBuildingMaterials.GREAT_SLAB.value
            return _

    def parse_house_type(self, features_list):
        if self.search_form["property_type"] != "house":
            return None
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Typ budynku")
            if not _:
                return None
            _ = _.lower()
            if _ == "wolnostojący":
                return Property.TypesOfHouses.DETACHED_HOUSE.value
            elif _ == "bliźniak":
                return Property.TypesOfHouses.SEMI_DETACHED_HOUSE.value
            elif _ == "szeregowiec":
                return Property.TypesOfHouses.TERRACED_HOUSE.value
            return _

    def parse_flat_type(self, features_list):
        if self.search_form["property_type"] != "flat":
            return None
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Typ budynku")
            if not _:
                return None
            _ = _.lower()
            if _ == "blok":
                return Property.TypesOfFlats.BLOCK_OF_FLATS.value
            elif _ == "kamienica":
                return Property.TypesOfFlats.TENEMENT.value
            elif _ == "apartament":
                return Property.TypesOfFlats.APARTMENT.value
            return _

    def parse_plot_type(self, features_list):
        if self.search_form["property_type"] != "plot":
            return None
        with suppress(Exception):
            type = self.get_feature_value(features_list, "Rodzaj działki")
            if type == "budowlana":
                return Property.TypesOfPlots.BUILDING.value
            elif type == "rolna":
                return Property.TypesOfPlots.AGRICULTURAL.value
            elif type == "rekreacyjna":
                return Property.TypesOfPlots.RECREATIONAL.value
            elif type == "leśna":
                return Property.TypesOfPlots.FOREST.value
            return type

    def parse_ownership(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Forma własności")
            if _ == "Własność" or _ == "własność":
                return Property.TypesOfOwnership.FULL_OWNERSHIP.value
            return _

    def parse_regular_user(self, soup, data):
        with suppress(Exception):
            if data and "advertiserType" in data:
                if data["advertiserType"] == "agencja":
                    return False
                elif data["advertiserType"] == "prywatny":
                    return True
        # można jeszcze z soup próbować wyciągać

    def parse_market_type(self, data):
        with suppress(Exception):
            _ = data["market"]
            if _ == "rp":
                return Property.TypesOfMarket.PRIMARY.value
            elif _ == "rw":
                return Property.TypesOfMarket.SECONDARY.value

    def parse_gas(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Media")
            if "gaz" in _:
                return True

    def parse_sewerage(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Media")
            if "kanalizacja" in _:
                return True

    def parse_electricity(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Media")
            if "prąd" in _:
                return True

    def parse_water(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Media")
            if "woda" in _:
                return True

    def parse_fence(self, features_list):
        with suppress(Exception):
            _ = self.get_feature_value(features_list, "Ogrodzenie działki")
            if "brak" == _:
                return False
            elif _:
                return True

    def parse_heating(self, additional_info):
        with suppress(Exception):
            if "ogrzewanie miejskie" in additional_info:
                return Property.TypesOfHeating.URBAN.value
            elif "ogrzewanie gazowe" in additional_info:
                return Property.TypesOfHeating.GAS.value

    def parse_forest_vicinity(self, additional_info):
        with suppress(Exception):
            _ = "las" in additional_info
            if _:
                return True

    def parse_lake_vicinity(self, additional_info):
        with suppress(Exception):
            _ = "jezioro" in additional_info
            if _:
                return True
