from .scrapyd_singleton import ScrapydAPISingleton
from django.conf import settings
import json


class ScrapydSpiderFactory:
    job_ids = []

    def __init__(self, search_form, scrapyd=None):
        self.search_form = search_form
        self.project_name = "scraper"
        self.project_name = settings.SCRAPYD_PROJECT
        if not scrapyd:
            self.scrapyd = ScrapydAPISingleton(settings.SCRAPYD_URL)
        print("self.project_name", self.project_name)
        self.job_ids = []

    def create_spiders(self):
        print('create_spiders')
        # spider_names = ['otodom', 'olx', 'domiporta', 'morizon', 'gratka']
        spider_names=['domiporta', 'morizon', 'gratka']
        # spider_names=['morizon']
        location_level = determine_location_level(self.search_form)
        if location_level:
            for spider_name in spider_names:
                if is_location_level_supported(spider_name, location_level):
                    job_id = self.schedule_spider(spider_name)
                    print('spider_name', spider_name, 'job_id', job_id)
                    self.job_ids.append(job_id)
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
        spider_args = {'search_form': json.dumps(self.search_form)}
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