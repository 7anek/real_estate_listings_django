from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from rest_framework.exceptions import APIException, ValidationError
from properties_scrapy.models import Property
from properties_api.serializers import PropertySerializer, SearchResultsSerializer
from properties_scrapy.forms import SearchForm
import json, uuid
from properties_scrapy.scrapy_factory import ScrapydSpiderFactory
from properties_scrapy.utils import is_scrapyd_running
from properties_scrapy.scrapyd_api import scrapyd
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
import uuid


# Create your views here.

class PropertyListAPIView(ListAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    # permission_classes = [AllowAny]


class PropertiesScrape(APIView):
    # scrapyd = ScrapydAPI('http://localhost:6800')
    serializer_class = PropertySerializer
    # permission_classes = [AllowAny]

    # @csrf_exempt
    def post(self, request):
        search_form = SearchForm(request.POST)

        # settings = get_project_settings()
        print('////////////', request.POST)
        # print('////////////',search_form)

        if search_form.is_valid():
            print('//////////// form is ok', search_form.cleaned_data)
            if not is_scrapyd_running():
                return Response("Scrapyd unavailable", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                # scrapy_factory = ScrapydSpiderFactory(json.dumps(search_form.cleaned_data))
                scrapy_factory = ScrapydSpiderFactory(search_form.cleaned_data)
                print('++++++++++++++++++scrapy_factory created')
                scrapy_factory.create_spiders()
                print('++++++++++++++++++scrapy_factory spiders created', scrapy_factory.job_ids)
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # while scrapy_factory.check_finished():
            #     print('++++++++++++++++++time.sleep(10)')
            #     time.sleep(10)

            # scrape_job_id = uuid.UUID(hex=job_id)
            properties = Property.objects.filter(scrapyd_job_id__in=scrapy_factory.job_ids)
            serializer = PropertySerializer(properties, many=True)
            return Response({'job_ids': scrapy_factory.job_ids, 'properties': serializer.data,
                             'finished': scrapy_factory.check_finished()})
        print('//////////// error - invalid form', search_form.cleaned_data)
        return Response("invalid form", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def get(self, request, scrape_job_id, format="json"):
    def get(self, request, job_ids, format="json"):

        # uuids_list = uuids.replace('-','').split(',')
        uuids_list = job_ids.split(',')
        uuids_list = list(map(lambda job_id: uuid.UUID(hex=job_id), uuids_list))
        print(uuids_list)

        if is_scrapyd_running():
            if self.check_finished(uuids_list):
                properties = Property.objects.filter(scrapyd_job_id__in=uuids_list)
                serializer = PropertySerializer(properties, many=True)
                print('serializer.data:', serializer.data)
                return Response(serializer.data)
            else:
                return Response("Spiders are processing", status=status.HTTP_202_ACCEPTED)
        else:
            print("niepodłączono scrapyd")
            return Response("Scrapyd is not running", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def check_finished(self, uuids):
        """
        czy któryś ze spiderów ma status running albo pending
        uuids - lista uuids
        return False - jeśli jest jakiś spider który jeszcze się nieskończył wykonywać"""
        return not any(
            scrapyd.job_status(project=settings.SCRAPYD_PROJECT, job_id=job_id) in ['running', 'pending'] for job_id in
            uuids)



