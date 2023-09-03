import unicodedata
from properties_scrapy.utils import *
import re

offer_type_mapping = {
    'sell': '',
    'rent': 'wynajem',
}
property_type_mapping = {
    'flat': 'mieszkania',
    'house': 'domy',
    'plot': 'dzialki-grunty',
    'garage': 'garaze'
}


def get_url_path(search_params):
    url_path = []
    if 'property_type' in search_params:
        url_path.append(property_type_mapping[search_params['property_type']])
    # url_path.append(slugify(search_params['localization']))

    if 'street' in search_params:
        url_path.append(slugify(search_params['city']))
        url_path.append('ul-' + slugify(search_params['street']))
    elif 'district' in search_params:
        url_path.append(slugify(search_params['city']))
        url_path.append(slugify(search_params['district']))
    elif 'district_neighbourhood_from_url' in search_params:
        url_path.append(search_params['district_neighbourhood_from_url'])
    elif 'city' in search_params:
        url_path.append(slugify(search_params['city']))
    elif 'province' in search_params:
        url_path.append(slugify(search_params['province']))

    if 'offer_type' in search_params:
        if search_params['offer_type'] == 'rent':
            url_path.append(offer_type_mapping[search_params['offer_type']])

    return f"/nieruchomosci/{'/'.join(url_path)}"


def get_url_query(search_params, page=1, limit=24):
    url_query = {'page': page}

    if 'price_min' in search_params:
        url_query['cena-calkowita:min'] = search_params['price_min']
    else:
        url_query['cena-calkowita:min'] = 1#dają mnóstwo ofert z ceną "Zapytaj o cenę", w ten sposób się nieznajdą
    if 'price_max' in search_params:
        url_query['cena-calkowita:max'] = search_params['price_max']
    if 'area_min' in search_params:
        url_query['powierzchnia-w-m2:min'] = search_params['area_min']
    if 'area_max' in search_params:
        url_query['powierzchnia-w-m2:max'] = search_params['area_max']
    if 'year_of_construction_from' in search_params:
        url_query['rok-budowy:min'] = search_params['year_of_construction_from']
    if 'year_of_construction_to' in search_params:
        url_query['rok-budowy:max'] = search_params['year_of_construction_to']

    print('url_query', url_query)
    return url_query


def get_results_count(soup):
    return int(soup.find("span", {"data-cy": "offersCount"}).text[1:-1].replace(" ", ""))


def get_results_set(soup):
    return soup.find_all("article", {"class": "teaserUnified"})


def get_single_search_result_url(single_result_soup):
    return single_result_soup["data-href"]


def get_single_search_result_image_url(single_result_soup):
    return single_result_soup.find("img")["src"]


def get_single_search_result_title(single_result_soup):
    return single_result_soup.find("h2").text.strip()


def get_single_search_result_price(single_result_soup):
    return re.sub(r"\s+", "", single_result_soup.find("p", {"data-cy": "teaserPrice"}).contents[0])


def get_single_search_result_additional_features_set(single_result_soup):
    return single_result_soup.find_all("li", {"class": "teaserUnified__listItem"})


def get_single_search_result_area(additional_features_set):
    return float(additional_features_set[0].text.split()[0].replace(',', '.'))


def get_single_search_result_number_of_rooms(additional_features_set):
    try:
        ret = int(next(filter(lambda f: "pok" in f.text, additional_features_set), None).text.split()[0])
    except:
        ret = None
    return ret
