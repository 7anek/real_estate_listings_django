import unicodedata
from urllib.parse import unquote, parse_qs, urlparse, urlunparse, urlencode

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import requests
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

def localization_fields_from_search_form(item, search_form):
    item["address"] = search_form["address"] if "address" in search_form else None
    item["province"] = search_form["province"] if "province" in search_form else None
    item["county"] = search_form["county"] if "county" in search_form else None
    item["city"] = search_form["city"] if "city" in search_form else None
    item["district"] = search_form["district"] if "district" in search_form else None
    item["district_neighbourhood"] = search_form[
        "district_neighbourhood"] if "district_neighbourhood" in search_form else None
    item["street"] = search_form["street"] if "street" in search_form else None
    return item


def selenium_browser(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # return webdriver.Chrome("/home/janek/python/property_scraper/chromedriver", options=chrome_options)
    #return webdriver.Chrome("chromedriver", options=chrome_options)


    # webdriver_service = Service('static/properties_scrapy/chrome-linux64/chrome')
    # self.driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    return webdriver.Remote("http://selenium:4444/wd/hub", options=chrome_options)


def is_scrapyd_running():
    """scrapyd: obiekt scrapyd_api.ScrapydAPI('host:port')"""
    scrapyd_url = settings.SCRAPYD_URL
    logger.debug(f'333333scrapyd url: {scrapyd_url}')
    try:
        response = requests.get(f'{scrapyd_url}/daemonstatus.json')
        if response.status_code == 200:
            print('Scrapyd is running.')
            is_scrapyd_running = True
        else:
            print('Scrapyd is not running.')
            is_scrapyd_running = False
    except requests.exceptions.ConnectionError:
        print('Unable to connect to Scrapyd.')
        is_scrapyd_running = False
    return is_scrapyd_running


def url_encode(url):
    return unquote(url)


def dict_filter_none(d):
    return {key: value for key, value in d.items() if value}


def remove_accents(str):
    return ''.join(c for c in unicodedata.normalize('NFD', str) if unicodedata.category(c) != 'Mn')


def lowercase_with_hyphen_str(str):
    return '-'.join(str.lower().split())


def slugify(str):
    """używane do wygenerowania lokalizacji jako parametr urla"""
    return lowercase_with_hyphen_str(remove_accents(str))


def flatten_dict(d):
    """
    input:{'search[filter_float_price:from]': ['300000'], 'search[filter_float_price:to]': ['400000'], 'page': ['1']}
    output:{'search[filter_float_price:from]': '300000', 'search[filter_float_price:to]': '400000', 'page': '1'}
    """
    return {k: v[0] for k, v in d.items()}


def url_to_params_dict(url):
    """
    input:https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/grodzisk-mazowiecki/?search%5Bfilter_float_price%3Afrom%5D=300000&search%5Bfilter_float_price%3Ato%5D=400000&page=1
    output:{'search[filter_float_price:from]': '300000', 'search[filter_float_price:to]': '400000', 'page': '1'}
    """
    d = parse_qs(urlparse(url).query)
    fd = flatten_dict(d)
    return fd


def get_url_path(url):
    """
    input:https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/grodzisk-mazowiecki/?search%5Bfilter_float_price%3Afrom%5D=300000&search%5Bfilter_float_price%3Ato%5D=400000&page=1
    output:/nieruchomosci/mieszkania/sprzedaz/grodzisk-mazowiecki
    """
    return urlparse(url).path


def generate_url(scheme='https', netloc='', path='', url='', query='', fragment=''):
    """
    scheme - protokół,
    netloc - adres hosta,
    path - reszta ścieżki,
    query - niewiem coto, dożuca średnik, zostawiać puste,
    params - parametry http get,
    fragment - html id
    https://stackoverflow.com/questions/15799696/how-to-build-urls-in-python
    https://docs.python.org/3/library/urllib.parse.html
    """
    return urlunparse((
        scheme,
        netloc,
        path,
        url,
        urlencode(query),
        fragment
    )
    )


def soup_from_file(path):
    page = open(path, encoding="utf8")
    return BeautifulSoup(page.read(), "html.parser")


def safe_execute(default, exception, function, *args):
    """
    safe_execute(
        "Division by zero is invalid.",
        ZeroDivisionError,
        div, 1, 0
    )
    # Returns "Division by zero is invalid."
    """
    try:
        return function(*args)
    except exception:
        return default


class DictAutoVivification(dict):
    """
    Implementation of perl's autovivification feature.
    >>> d = DictAutoVivification()
    >>> d['b']['s']['f']=4
    >>> d
    {'b': {'s': {'f': 4}}}
    >>> d['b']['r']['d']=7
    >>> d
    {'b': {'s': {'f': 4}, 'r': {'d': 7}}}
    """

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
