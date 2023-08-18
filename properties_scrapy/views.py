import json
import time
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties_scrapy.forms import SearchForm
from properties_scrapy.models import Property
from properties_scrapy.scrapy_factory import ScrapydSpiderFactory
from properties_scrapy.scrapyd_api import scrapyd
from properties_scrapy.utils import *
from django.conf import settings


# Create your views here.
@login_required
def crawl(request):
    # process = subprocess.run(["python", "manage.py", "crawl"], check=True)
    # data = process.stdout
    # data = process
    # process = CrawlerProcess(get_project_settings())
    # process.crawl(PropertiesSpider) # Assuming that you are passing the argumment of the car_model to scrape specific models
    # process.start()
    # data = "abc"
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        if is_scrapyd_running():
        # if True:
            # settings = get_project_settings()
            # print('////////////',settings)
            if search_form.is_valid():
                print('///////////search_form.cleaned_data', search_form.cleaned_data)
                # job_id = scrapyd.schedule('scraper', 'gratka', search_form=json.dumps(search_form.cleaned_data))
                # job_id = scrapyd.schedule('default', 'gratka', search_form=json.dumps(search_form.cleaned_data))
                # job_id = scrapyd.schedule('default', 'otodom', search_form = json.dumps(search_form.cleaned_data))
                # job_id = scrapyd.schedule('default', 'otodom', settings=settings)
                try:
                    # scrapy_factory = ScrapydSpiderFactory(json.dumps(search_form.cleaned_data))
                    scrapy_factory = ScrapydSpiderFactory(search_form.cleaned_data)
                except Exception as e:
                    print(str(e))
                print('++++++++++++++++++scrapy_factory created')
                scrapy_factory.create_spiders()
                print('++++++++++++++++++scrapy_factory spiders created', scrapy_factory.job_ids)
                # while scrapy_factory.check_finished():
                #     print('++++++++++++++++++time.sleep(10)')
                #     time.sleep(10)

                # print('++++++++++++++++++job_id',job_id)
                # scrape_status = scrapyd.job_status('scraper', job_id)
                # scrape_job_id = uuid.UUID(hex=job_id)

                if not settings.TESTING:
                    # if not settings.get('TESTING'):
                    time.sleep(5)

                properties = Property.objects.filter(scrapyd_job_id__in=scrapy_factory.job_ids)
                print("$$$$$$$$$$$$$$ properties", properties)
                context = {"title": "search", "search_form": search_form, "properties": properties,
                           "scrape_status": "Running", "scrapyd_job_id": ",".join(scrapy_factory.job_ids)}
                print("$$$$$$$$$$$$$$ context", context)
                if scrapy_factory.check_finished():
                    context["scrape_status"] = "Finished"
                else:
                    context["scrape_status"] = "Running"
            else:
                search_form = SearchForm()
                context = {"title": "search", "search_form": search_form, 'error': 'Invalid form data'}
        else:
            context = {"title": "search", "search_form": search_form, 'error': 'Scrapyd unavailable'}
    else:
        search_form = SearchForm()
        if is_scrapyd_running():
            context = {"title": "search", "search_form": search_form}
        else:
            context = {"title": "search", "search_form": search_form, 'error': 'Scrapyd unavailable'}

    return render(request, "properties_scrapy/crawl.html", context)


@login_required
def get_crawl(request, uuids):
    search_form = SearchForm()
    uuids_list = uuids.split(',')
    try:
        uuids_list = list(map(lambda job_id: uuid.UUID(hex=job_id), uuids_list))
    except:
        context = {"title": "scrape", "search_form": search_form, "error": f"Wrong job ids: {uuids}"}
        return render(request, "properties/scrape.html", context)
    print(uuids_list)
    properties = Property.objects.filter(scrapyd_job_id__in=uuids_list)
    context = {"title": "scrape", "search_form": search_form, "properties": properties, 'scrape_job_id': uuids}
    if is_scrapyd_running():
        if check_finished(uuids_list):
            context["scrape_status"] = "Finished"
        else:
            context["scrape_status"] = "Running"
    else:
        context['error'] = 'Scrapyd unavailable'
    return render(request, "properties_scrapy/crawl.html", context)


def check_finished(uuids):
    """uuids - lista uuids
    return False - jeśli jest jakiś spider który jeszcze się nieskończył wykonywać"""
    return not any(scrapyd.job_status(project=settings.SCRAPYD_PROJECT, job_id=job_id) in ['running', 'pending'] for job_id in uuids)
