import unicodedata
from properties_scrapy.utils import *
import re

offer_type_mapping = {
    'sell': '',
    'rent': 'do-wynajecia',
}
property_type_mapping = {
    'flat': 'mieszkania',
    'house': 'domy',
    'plot': 'dzialki',
    'garage': 'garaze'
}

def get_url_path(search_params):
    url_path = []
    if 'offer_type' in search_params:
        if search_params['offer_type'] == 'rent':
            url_path.append(offer_type_mapping[search_params['offer_type']])
    if 'property_type' in search_params:
        url_path.append(property_type_mapping[search_params['property_type']])
    
    if 'street' in search_params:
        url_path.append(slugify(search_params['city']))
        if 'district' in search_params:
            url_path.append(slugify(search_params['district']))
        url_path.append(slugify(search_params['street']))
    elif 'district_neighbourhood' in search_params:
        url_path.append(slugify(search_params['city']))
        url_path.append(slugify(search_params['district_neighbourhood']))
    elif 'district' in search_params:
        url_path.append(slugify(search_params['city']))
        url_path.append(slugify(search_params['district']))
    elif 'city' in search_params:
        url_path.append(slugify(search_params['city']))
    elif 'province' in search_params:   
        url_path.append(slugify(search_params['province'])) 
    
    return f"/{'/'.join(url_path)}/"


def get_url_query(search_params,page=1,limit=24):
    url_query = {'page': page }

    if 'price_min' in search_params:
        url_query['ps[price_from]'] = search_params['price_min']
    if 'price_max' in search_params:
        url_query['ps[price_to]'] = search_params['price_max']
    if 'area_min' in search_params:
        url_query['ps[living_area_from]'] = search_params['area_min']
    if 'area_max' in search_params:
        url_query['ps[living_area_to]'] = search_params['area_max']
    if 'year_of_construction_from' in search_params:
        url_query['ps[build_year_from]'] = search_params['year_of_construction_from']
    if 'year_of_construction_to' in search_params:
        url_query['ps[build_year_to]'] = search_params['year_of_construction_to']

    print('url_query', url_query)
    return url_query

def get_results_count(soup):
    return int(soup.find("h1").text.split()[0])

def get_results_set(soup):
    return soup.find_all("a",{"class":"offer__outer"})

def get_single_search_result_url(single_result_soup):
    return single_result_soup["href"]

def get_single_search_result_image_url(single_result_soup):
    try:
        return single_result_soup.find("div",{"data-index":"0"}).find("img")["src"]
    except:
        return None

def get_single_search_result_title(single_result_soup):
    return single_result_soup.find("span",{"class":"offer__title"}).get_text("",strip=True)

def get_single_search_result_price(single_result_soup):
    try:
        return float(re.sub(r"[^\d.,]","",single_result_soup.find("div",{"class":"offer-price__bottom"}).get_text("",strip=True)).replace(",","."))
    except Exception as e:
        print(e)
        return 0.0


def get_single_search_result_additional_features_set(single_result_soup):
    return single_result_soup.find("div",{"class":"property-info"}).contents

def get_single_search_result_area(additional_features_set):
    return float(additional_features_set[0].text.split()[0])

def get_single_search_result_number_of_rooms(additional_features_set):
    try:
        ret=int(next(filter(lambda f: "pok" in f.text,additional_features_set),None).text.split()[0])
    except:
        ret=None
    return ret