from properties_scrapy.utils import *

offer_type_mapping = {
    'sell': 'sprzedaz',
    'rent': 'wynajem'
}
property_type_mapping = {
    'flat': 'mieszkanie',
    'house': 'dom',
    'plot': 'dzialka',
}
# 31 parametrów wyszukiwania
FLAT_FILTERS_MAPPING = {
    'city': 4,
    'district': 5,
    'district_neighbourhood': 5,
    'price_min': 8,
    'price_max': 8,
    'area_min': 9,
    'area_max': 9,
    'property_type': 1,
    'offer_type': 2,
    'flat_type': 30,
    'year_of_construction_from': 7
}
# 22 pola
PLOT_FILTERS_MAPPING = {
    'city': 4,
    'district': 5,
    'district_neighbourhood': 5,
    'price_min': 8,
    'price_max': 8,
    'area_min': 9,
    'area_max': 9,
    'property_type': 1,
    'offer_type': 2,
    'plot_type': 21,
}
# 18 pól
HOUSE_FILTERS_MAPPING = {
    'city': 4,
    'district': 5,
    'district_neighbourhood': 5,
    'price_min': 8,
    'price_max': 8,
    'area_min': 9,
    'area_max': 9,
    'property_type': 1,
    'offer_type': 2,
    'house_type': 17,
}


def get_url_path(search_params):
    return "/szukaj.html"


def get_property_filter_params(search_params, mapping, size):
    filters = [''] * size
    pa = list(filter(lambda l: "price" in l or "area" in l, search_params))
    for l in pa:
        s = str(search_params[l])
        filters[mapping[l]] += f"-{s}" if "max" in l else s

    npa = filter(lambda l: "price" not in l and "area" not in l, search_params)
    for l in npa:
        if l == 'offer_type':
            v = offer_type_mapping[search_params[l]]
        elif l == 'property_type':
            v = property_type_mapping[search_params[l]]
        else:
            v = search_params[l]
        filters[mapping[l]] = v
    return ','.join(filters)


def get_request_params(search_params, page=1):
    if 'district_neighbourhood' in search_params:
        search_params.pop('district', None)
    if 'address' in search_params:
        search_params.pop('address', None)
    if 'province' in search_params:
        search_params.pop('province', None)

    if search_params['property_type'] == 'flat':
        filters = get_property_filter_params(search_params, FLAT_FILTERS_MAPPING, 31)
    elif search_params['property_type'] == 'plot':
        filters = get_property_filter_params(search_params, PLOT_FILTERS_MAPPING, 22)
    elif search_params['property_type'] == 'house':
        filters = get_property_filter_params(search_params, HOUSE_FILTERS_MAPPING, 18)
    request_params = {filters: '', 'page': page}
    return request_params
