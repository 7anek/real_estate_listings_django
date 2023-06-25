import unicodedata
from properties_scrapy.utils import *
import re

offer_type_mapping = {
    'sell': 'sprzedam',
    'rent': 'wynajme',
}
property_type_mapping = {
    'flat': 'mieszkanie',
    'house': 'dom',
    'plot': 'dzialke',
    'garage': 'garaz'
}

def get_url_path(search_params):
    url_path = []
    if 'property_type' in search_params:
        url_path.append(property_type_mapping[search_params['property_type']])
    if 'offer_type' in search_params:
        url_path.append(offer_type_mapping[search_params['offer_type']])
    # url_path.append(slugify(search_params['localization']))
    if 'street' in search_params:
        url_path.append(slugify(search_params['province']))
        url_path.append(slugify(search_params['city']))
        url_path.append(slugify(search_params['street']))
    elif 'district_neighbourhood' in search_params:
        url_path.append(slugify(search_params['province']))
        url_path.append(slugify(search_params['city']))
        url_path.append(slugify(search_params['district_neighbourhood']))
    elif 'district' in search_params:
        url_path.append(slugify(search_params['province']))
        url_path.append(slugify(search_params['city']))
        url_path.append(slugify(search_params['district']))
    elif 'city' in search_params:
        url_path.append(slugify(search_params['province']))
        url_path.append(slugify(search_params['city']))
    elif 'province' in search_params:   
        url_path.append(slugify(search_params['province'])) 
    
    return f"/{'/'.join(url_path)}"


def get_url_query(search_params,page=1,limit=24):
    url_query = {'PageNumber': page }

    if 'price_min' in search_params:
        url_query['Price.From'] = search_params['price_min']
    if 'price_max' in search_params:
        url_query['Price.To'] = search_params['price_max']
    if 'area_min' in search_params:
        url_query['Surface.From'] = search_params['area_min']
    if 'area_max' in search_params:
        url_query['Surface.To'] = search_params['area_max']
    if 'year_of_construction_from' in search_params:
        url_query['RokBudowy.From'] = search_params['year_of_construction_from']
    if 'year_of_construction_to' in search_params:
        url_query['RokBudowy.To'] = search_params['year_of_construction_to']

    print('url_query', url_query)
    return url_query

def get_results_count(soup):
    return int(soup.find("span",{"class":"summary__title"}).b.get_text("",strip=True))

def get_results_set(soup):
    return soup.find_all("article",{"class":"sneakpeak"})

def get_single_search_result_url(single_result_soup):
    return single_result_soup["data-href"]

def get_single_search_result_image_url(single_result_soup):
    return single_result_soup.find("img",{"class":"sneakpeak__picture_cover"})["data-src"]

def get_single_search_result_title(single_result_soup):
    return single_result_soup.find("span",{"class":"sneakpeak__title--bold"}).text

def get_single_search_result_price(single_result_soup):
    return float(re.sub(r"[^\d.,]","",single_result_soup.find("span",{"class":"sneakpeak__price_value"}).get_text("",strip=True)).replace(",","."))

def get_single_search_result_additional_features_set(single_result_soup):
    return single_result_soup.find("div",{"class":"sneakpeak__details"}).find_all("span",{"class":"sneakpeak__details_item"})

def get_single_search_result_area(additional_features_set):
    return float(next(filter(lambda t:"Powierzchnia" in t.attrs.values(),additional_features_set)).text.split()[0].replace(",","."))

def get_single_search_result_number_of_rooms(additional_features_set):
    try:
        ret=int(next(filter(lambda t:"Liczba pokoi" in t.attrs.values(),additional_features_set)).text.split()[0])
    except:
        ret=None
    return ret