from .scrapyd_singleton import ScrapydAPISingleton
from django.conf import settings


class ScrapydSpiderFactory:
    job_ids = []

    def __init__(self, search_form_json, scrapyd=None):
        self.search_form = search_form_json
        self.project_name = "scraper"
        self.project_name = settings.SCRAPYD_PROJECT
        if not scrapyd:
            self.scrapyd = ScrapydAPISingleton(settings.SCRAPYD_URL)
        print("self.project_name", self.project_name)
        self.job_ids = []

    def create_spiders(self):
        print('create_spiders')
        spider_names = ['otodom', 'olx', 'domiporta', 'morizon', 'gratka']
        # spider_names=['domiporta']
        for spider_name in spider_names:
            job_id = self.schedule_spider(spider_name)
            print('spider_name', spider_name, 'job_id', job_id)
            self.job_ids.append(job_id)

    def schedule_spider(self, spider_name):
        spider_args = {'search_form': self.search_form}
        if settings.TESTING:
            spider_args['is_testing'] = settings.TESTING
        print('schedule_spider spider_args', spider_args)
        return self.scrapyd.schedule(self.project_name, spider_name, **spider_args)

    def check_finished(self):
        return not any(
            self.scrapyd.job_status(project=settings.SCRAPYD_PROJECT, job_id=job_id) in ['running', 'pending'] for
            job_id in self.job_ids)
