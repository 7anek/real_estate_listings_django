from .scrapyd_singleton import ScrapydAPISingleton
from django.conf import settings
import json
from celery import shared_task
import concurrent.futures
from requests.exceptions import ConnectionError, Timeout, RequestException
from bs4 import BeautifulSoup
import requests


class ScrapydSpiderFactory:
    job_ids = []
    # Lista pająków, które wymagają użycia proxy z powodu blokowania
    required_proxy = ['otodom','olx']
    def __init__(self, search_form, scrapyd=None):
        self.search_form = search_form
        self.project_name = "scraper"
        self.project_name = settings.SCRAPYD_PROJECT
        if not scrapyd:
            self.scrapyd = ScrapydAPISingleton(settings.SCRAPYD_URL)
        print("self.project_name", self.project_name)
        self.job_ids = []
        self.proxies = []

    def create_spiders(self):
        print('create_spiders')
        spider_names = ['otodom', 'olx', 'domiporta', 'morizon', 'gratka']
        self.proxies = proxy_list()
        # spider_names=['domiporta', 'morizon', 'gratka']
        # spider_names = ['otodom']
        location_level = determine_location_level(self.search_form)
        if location_level:
            for spider_name in spider_names:
                if is_location_level_supported(spider_name, location_level):
                    if not (spider_name in self.required_proxy and not self.proxies):
                        job_id = self.schedule_spider(spider_name)
                        print('spider_name', spider_name, 'job_id', job_id)
                        self.job_ids.append(job_id)
                    else:
                        print('proxy list is empty, spider_name', spider_name, 'requires proxy')
                else:
                    print('spider_name', spider_name, 'does not support location level', location_level)
        else:
            print('No valid location level found in search form.')
        # for spider_name in spider_names:
        #     if self.is_location_level_supported(spider_name):
        #         job_id = self.schedule_spider(spider_name)
        #         print('spider_name', spider_name, 'job_id', job_id)
        #         self.job_ids.append(job_id)

    def schedule_spider(self, spider_name):
        spider_args = {
            'search_form': json.dumps(self.search_form),
            'proxies': json.dumps(self.proxies)
        }
        if settings.TESTING:
            spider_args['is_testing'] = settings.TESTING
        print('schedule_spider spider_args', spider_args)
        url = 'http://127.0.0.1:6800/schedule.json'
        # url = "http://django:6800/schedule.json"
        return self.scrapyd.schedule(self.project_name, spider_name, url=url, **spider_args)

    def check_finished(self):
        return not any(
            self.scrapyd.job_status(project=settings.SCRAPYD_PROJECT, job_id=job_id) in ['running', 'pending'] for
            job_id in self.job_ids)

def determine_location_level(search_form_data):
    if search_form_data['street']:
        return 'street'
    elif search_form_data['district_neighbourhood']:
        return 'district_neighbourhood'
    elif search_form_data['district']:
        return 'district'
    elif search_form_data['city']:
        return 'city'
    elif search_form_data['province']:
        return 'province'
    else:
        return None


def is_location_level_supported(service_name, location_level):
    supported_levels = {
        'otodom': ['province', 'city', 'district', 'district_neighbourhood'],
        'olx': ['city', 'district'],
        # 'gratka': ['province', 'city', 'district', 'district_neighbourhood', 'street'],
        'gratka': ['province', 'city', 'district', 'street'],
        'morizon': ['province', 'city', 'district', 'district_neighbourhood', 'street'],
        'domiporta': ['province', 'city', 'district', 'district_neighbourhood', 'street'],
        'nieruchomosci-online': ['city', 'district', 'district_neighbourhood']
    }

    return location_level in supported_levels.get(service_name, [])

@shared_task
def getProxies():
    print('getProxies')
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
        if row.find_all('td')[4].text =='elite proxy':
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
        else:
            pass
    print('proxies',proxies)
    return proxies

@shared_task
def extract(proxy):
    print('extract')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    try:
        #change the url to https://httpbin.org/ip that doesnt block anything
        # r = requests.get('https://httpbin.org/ip', headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        r = requests.get('https://google.com', headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        # print(r.json(), r.status_code)
        if r.status_code == 200:
            print("found working proxy:", proxy)
            return proxy
    except (ConnectionError, Timeout, RequestException) as err:
        print(f"Error while processing proxy {proxy}: {err}")
        # print(repr(err))
    return None


def proxy_list():
    print('proxy_list')
    proxylist = getProxies.delay()  # Uruchomienie getProxies jako zadania Celery
    print('getProxies delayed')
    # Pobranie wyników z zadania asynchronicznego
    proxylist_result = proxylist.get()
    print('proxylist.get')
    working_proxies = []
    if proxylist_result:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_proxy = {executor.submit(extract, proxy): proxy for proxy in proxylist_result}
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                result = future.result()
                if result:
                    working_proxies.append(result)
    print("Working proxies:", working_proxies)
    return working_proxies