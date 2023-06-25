from properties_scrapy.utils import *

offer_type_mapping = {
    'sell': 'sprzedaz',
    'rent': 'wynajem'
}
property_type_mapping = {
    'flat': 'mieszkania',
    'house': 'domy',
    'plot': 'dzialki',
    'garage': 'garaze-parkingi'
}

def get_url_path(search_params):
    url_path = []
    if 'property_type' in search_params:
        url_path.append(property_type_mapping[search_params['property_type']])
    if 'offer_type' in search_params:
        url_path.append(offer_type_mapping[search_params['offer_type']])
    if "city" in search_params:
        url_path.append(slugify(search_params['city']))
    return f"/d/nieruchomosci/{'/'.join(url_path)}"

def get_request_params(search_params,page=1):
    request_params = {'page': page}
    if 'price_min' in search_params:
        request_params['search[filter_float_price:from]'] = search_params['price_min']
    if 'price_max' in search_params:
        request_params['search[filter_float_price:to]'] = search_params['price_max']
    if 'area_min' in search_params:
        request_params['search[filter_float_m:from]'] = search_params['area_min']
    if 'area_max' in search_params:
        request_params['search[filter_float_m:to]'] = search_params['area_max']
    
    if 'search[district_id]' in search_params:
        request_params['search[district_id]'] = search_params['search[district_id]']
    return request_params