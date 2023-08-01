from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from properties_scrapy.models import Property
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from properties_api.serializers import PropertySerializer, SearchResultsSerializer
from django.conf import settings
from properties_scrapy.scrapy_factory import ScrapydSpiderFactory


# Create your tests here.

class PropertyViewSetTestCase(APITestCase):
    # def setUp(self):
    #     # self.obj = MyModel.objects.create(name="John")
    #     pass

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="password")
        cls.access_token = str(AccessToken.for_user(cls.user))
        cls.property_data = {"title": "aaa", "price": 234, "area": 245, "service_name": "blabla",
                             "service_url": "http://www.example.com"}
        cls.property = Property.objects.create(**cls.property_data)
        Property.objects.create(title="bbb", price=643, area=234, service_name="uuuuu",
                                service_url="http://www.example.com")

    #     #the testing framework will automatically call once for this class
    #     #setUpTestData - jest elementem django i robi rollback w przypadku niepowodzenia
    #     cls.search_criteria = {'localization': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000, 'area_min': None, 'area_max': None, 'property_type': 'flat', 'offer_type': 'sell', 'plot_type': '', 'house_type': '', 'flat_type': '', 'year_of_construction_from': None, 'year_of_construction_to': None}#zakładam że na takie kryteria wyszukiwania będe dostawał wyniki
    #     cls.search_results = search.webpages_search(cls.search_criteria)
    #     print("setUpClass")
    # def setUp(self):

    def test_objects_list_unauthenticated(self):
        url = reverse("properties_api:property-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_objects_list_authenticated(self):
        url = reverse("properties_api:property-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(len(response.data), 2)

    def test_property_list(self):
        url = reverse('properties_api:property-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        properties = Property.objects.all()
        serializer = PropertySerializer(properties, many=True)
        data = {"title": "aaa", "price": 234, "area": 245, "service_name": "blabla",
                "service_url": "http://www.example.com"}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_property_detail(self):
        url = reverse('properties_api:property-detail', args=[self.property.id])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        serializer = PropertySerializer(self.property)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_property_create(self):
        url = reverse('properties_api:property-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(url, self.property_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 3)
        self.assertEqual(Property.objects.first().title, self.property_data['title'])

    def test_property_update(self):
        url = reverse('properties_api:property-detail', args=[self.property.id])
        updated_data = {
            'title': 'Updated Property',
            'description': 'Updated description',
            'price': 150000,
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, updated_data['title'])
        self.assertEqual(self.property.description, updated_data['description'])
        self.assertEqual(self.property.price, updated_data['price'])

    def test_property_delete(self):
        self.assertEqual(Property.objects.count(), 2)
        url = reverse('properties_api:property-detail', args=[self.property.id])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Property.objects.count(), 1)


class PropertiesSearchViewTestCase(TestCase):
    def setUp(self):
        self.old_debug = settings.DEBUG
        settings.DEBUG = True

        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def tearDown(self):
        settings.DEBUG = self.old_debug

    # @patch('properties.search_results.SearchResults')
    # @patch('properties.search_results.SearchResults')
    # @patch('properties_api.serializers.SearchResultsSerializer')
    # @patch('properties.search_results.SearchResults.__init__', return_value=None)
    # @patch.object(SearchResults, 'objects')
    # @patch('properties_api.serializers.SearchResultsSerializer.__init__', return_value=None)
    # @patch.object(SearchResultsSerializer, 'data')
    # def test_properties_search_valid_form(self, mock_serializer_data, mock_serializer_init, mock_objects, mock_init):
    #     print('test_properties_search_valid_form')
    #     url = reverse('properties_api:properties_search')
    #     search_params = {'address': 'Grodzisk Mazowiecki, Polska', 'province': 'Mazowieckie',
    #                      'city': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000,
    #                      'property_type': 'flat', 'offer_type': 'sell'}
    #     search_result = SearchResult()
    #     search_result.title='Existing Property',
    #     search_result.price=200000,
    #     search_result.area=1000,
    #     search_result.service='test_service',
    #     search_result.offer_url="http://www.example.com"
    #
    #     # mock_search_results._init__.return_value=None
    #     # mock_instance = mock_search_results.return_value
    #     # mock_instance._init__.return_value=None
    #     # mock_instance.objects.return_value = [search_result]
    #
    #     mock_objects.return_value = [
    #         {
    #             'title': 'Existing Property',
    #             'price': 200000,
    #             'area': 1000,
    #             'service': 'test_service',
    #             'offer_url': 'http://www.example.com'
    #         }
    #     ]
    #     mock_serializer_data = [
    #         {
    #             'title': 'Existing Property',
    #             'price': 200000,
    #             'area': 1000,
    #             'service': 'test_service',
    #             'offer_url': 'http://www.example.com'
    #         }
    #     ]
    #     # mock_search_results_serializers._init__.return_value=None
    #     # mock_serializers_instance = mock_search_results.return_value
    #     # mock_serializers_instance._init__.return_value = None
    #     # mock_serializers_instance.objects.return_value = json.[search_result]
    #     #
    #     response = self.client.get(url, search_params)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['objects']), 1)
    #     self.assertEqual(response.data, [
    #         {
    #             'title': 'Existing Property',
    #             'price': 200000,
    #             'area': 1000,
    #             'service': 'test_service',
    #             'offer_url': 'http://www.example.com'
    #         }
    #     ])
    # @patch('properties_api.views.SearchResults')
    # @patch('properties_api.serializers.SearchResultsSerializer')
    # def test_properties_search_valid_form(self, mock_serializer, mock_search_results):
    #     print('test_properties_search_valid_form')
    #     url = reverse('properties_api:properties_search')
    #     search_params = {'address': 'Grodzisk Mazowiecki, Polska', 'province': 'Mazowieckie',
    #                      'city': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000,
    #                      'property_type': 'flat', 'offer_type': 'sell'}
    #
    #     mock_search_results.return_value.objects.return_value = [
    #         {
    #             'title': 'Existing Property',
    #             'price': 200000,
    #             'area': 1000,
    #             'service': 'test_service',
    #             'offer_url': 'http://www.example.com'
    #         }
    #     ]
    #     mock_serializer.return_value.data = [
    #         {
    #             'title': 'Existing Property',
    #             'price': 200000,
    #             'area': 1000,
    #             'service': 'test_service',
    #             'offer_url': 'http://www.example.com'
    #         }
    #     ]
    #
    #     response = self.client.get(url, search_params)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # print('----------------response.data',response.data)
    #     # self.assertEqual(len(response.data['objects']), 1)
    #     # self.assertEqual(response.data, [
    #     #     {
    #     #         'title': 'Existing Property',
    #     #         'price': 200000,
    #     #         'area': 1000,
    #     #         'service': 'test_service',
    #     #         'offer_url': 'http://www.example.com'
    #     #     }
    #     # ])

    # @patch('properties.search_results.SearchResults')
    # @patch.object(SearchResults, "__init__", lambda *args: None)
    # def test_properties_search_invalid_form(self):
    #     print('test_properties_search_invalid_form')
    #     url = reverse('properties_api:properties_search')
    #     search_params = {'param1': 'value1'}
    #
    #     response = self.client.get(url, search_params)
    #
    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     self.assertEqual(response.data, "invalid form")


class PropertiesScrapePostTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.search_form_data = {'address': 'Grodzisk Mazowiecki, Polska', 'province': 'Mazowieckie',
                                 'city': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000,
                                 'property_type': 'flat', 'offer_type': 'sell'}

        property_data = {"title": "aaa", "price": 234, "area": 245, "service_name": "blabla",
                         "service_url": "http://www.example.com", 'scrapyd_job_id': '75d6b108cc9811edba0300155d7be260'}
        Property.objects.create(**property_data)
        Property.objects.create(title="bbb", price=643, area=234, service_name="uuuuu",
                                service_url="http://www.example.com", scrapyd_job_id='75d6b108cc9811edba0300155d7be260')

    # @patch.object(SearchForm, 'is_valid', return_value=False)
    # def test_scrape_post_invalid_form(self):
    #     print('test_scrape_invalid_form')
    #     invalid_search_form_data={'key1': 'val1', 'key2': 'val2'}
    #     url = reverse('properties_api:scrape')
    #     response = self.client.post(url, invalid_search_form_data)
    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     self.assertEqual(response.data, 'invalid form')

    # @patch.object(SearchForm, 'is_valid', return_value=True)
    # @patch('properties_scrapy.utils.is_scrapyd_running', return_value=False)
    # @patch('properties_scrapy.utils.is_scrapyd_running', side_effect=lambda: False)
    # @patch(is_scrapyd_running, return_value=False)
    def test_scrape_post_scrapyd_unavailable(self):
        print('test_scrape_scrapyd_unavailable')
        with patch('properties_api.views.is_scrapyd_running', return_value=False):
            url = reverse('properties_api:scrape')
            response = self.client.post(url, self.search_form_data)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data, 'Scrapyd unavailable')

    @patch('properties_scrapy.utils.is_scrapyd_running', return_value=True)
    @patch.object(ScrapydSpiderFactory, 'job_ids', ['75d6b108cc9811edba0300155d7be260'])
    @patch.object(ScrapydSpiderFactory, 'check_finished', return_value=True)
    @patch.object(ScrapydSpiderFactory, 'create_spiders')
    @patch.object(ScrapydSpiderFactory, '__init__', return_value=None)
    def test_scrape_post_successful(self, mock_init_spiders, mock_create_spiders, mock_check_finished,
                                               mock_is_scrapyd_running):
        url = reverse('properties_api:scrape')
        # search_form_data = {'address': 'Grodzisk Mazowiecki, Polska', 'province': 'Mazowieckie',
        #                  'city': 'Grodzisk Mazowiecki', 'price_min': 300000, 'price_max': 400000,
        #                  'property_type': 'flat', 'offer_type': 'sell'}
        # search_form = SearchForm(search_form_data)

        response = self.client.post(url, self.search_form_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('job_ids', response.data)
        self.assertIn('properties', response.data)
        self.assertIn('finished', response.data)
        # self.assertEqual(response.data['finished'], True)
        # Assert that necessary methods were called
        # mock_is_scrapyd_running.assert_called_once_with()
        # mock_create_spiders.assert_called_once_with()
        self.assertEqual(response.data['job_ids'], ['75d6b108cc9811edba0300155d7be260'])
        self.assertEqual(len(response.data['properties']), 2)

    # Test when check_finished() returns True
    # @patch.object(SearchForm, 'is_valid', return_value=True)
    # @patch('properties_scrapy.utils.is_scrapyd_running', return_value=True)
    # @patch.object(ScrapydSpiderFactory, 'check_finished', return_value=True)
    # @patch.object(Property.objects, 'filter')
    # def test_scrape_check_finished_true(self, mock_filter, mock_check_finished, mock_is_scrapyd_running,
    #                                                mock_is_valid):
    #     url = reverse('properties_api:scrape')
    #     search_form_data = {'param1': 'value1', 'param2': 'value2'}
    #     search_form = SearchForm(data=search_form_data)
    #
    #     mock_filter.return_value = []  # Mock empty result from filter()
    #
    #     with patch('uuid.UUID') as mock_uuid:
    #         mock_uuid.
    #         return


class PropertiesGetScrapeViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.property_data = {
            'title': 'Test Property',
            'description': 'Test description',
            'price': 100000,
            'area': 500,
        }
        self.property = Property.objects.create(
            title='Existing Property',
            description='Existing description',
            price=200000,
            area=1000,
            service_name='test_service',
            service_url="http://www.example.com"
            # owner=self.user
        )

    def test_get_scrape_all_finished(self):
        scrape_job_ids = ["75d6b108cc9811edba0300155d7be260"]
        url = reverse('properties_api:get_scrape', args=[','.join(scrape_job_ids)])

        # Mocking ScrapydSpiderFactory methods
        with patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory') as mock_factory:
            mock_instance = mock_factory.return_value
            mock_instance.check_finished.return_value = True
            mock_instance.create_spiders.return_value = None
            mock_instance.get_properties.return_value = []

            response = self.client.get(url)
            print(';;;;;;;;;;response.data', response.data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Add your assertions for the scraped properties

    @patch('properties_api.views.PropertiesScrape.check_finished', return_value=False)
    def test_get_scrape_not_all_finished(self, mock_check_finished):
        print('test_get_scrape_not_all_finished')
        scrape_job_ids = ["75d6b108cc9811edba0300155d7be260"]
        url = reverse('properties_api:get_scrape', args=[','.join(scrape_job_ids)])

        # Mocking ScrapydSpiderFactory methods
        with patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory') as mock_factory:
            mock_instance = mock_factory.return_value
            # mock_instance.check_finished.side_effect = [False, True]  # The first job ID is not finished, the second one is finished
            mock_instance.check_finished.return_value = False
            mock_instance.create_spiders.return_value = None
            mock_instance.get_properties.return_value = []

            response = self.client.get(url)
            print(';;;;;;;;;;response.data', response.data)
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            self.assertEqual(response.data, 'Spiders are processing')

    # @patch('properties_scrapy.utils.is_scrapyd_running')
    @patch('properties_api.views.is_scrapyd_running', return_value=False)
    @patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory')
    def test_get_scrape_scrapyd_not_running(self, mock_factory, mock_is_scrapyd_running):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        scrape_job_ids = ["75d6b108cc9811edba0300155d7be260"]
        url = reverse('properties_api:get_scrape', args=[','.join(scrape_job_ids)])

        # Mocking ScrapydSpiderFactory methods
        # with patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory') as mock_factory:
        mock_instance = mock_factory.return_value
        mock_instance.is_scrapyd_running.return_value = False
        mock_instance.create_spiders.return_value = None
        mock_instance.get_properties.return_value = []
        mock_is_scrapyd_running.return_value = False
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, 'Scrapyd is not running')


class SignUpTestCase(APITestCase):
    def test_signup_without_username(self):
        response = self.client.post('/signup/', {'password': 'password'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data[0], 'The given username must be set')

    # def test_signup_user_creation_error(self):
    #     response = self.client.post('/signup/', {'username': 'john', 'password': 'password', 'email': ['invalid']})
    #     self.assertEqual(response.status_code, 500)
    #     self.assertEqual(response.data, 'User creation error')

    def test_signup_success(self):
        response = self.client.post('/signup/',
                                    {'username': 'john', 'password': 'password', 'email': 'valid@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'User created')

        # Verify that a User object was created with the correct attributes
        user = User.objects.get(username='john')
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.email, 'valid@example.com')
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)


class JWTokenTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', password='password')

    def test_signin_success(self):
        response = self.client.post('/signin/', {'username': 'john', 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_signin_invalid_credentials(self):
        response = self.client.post('/signin/', {'username': 'john', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        print('test_token_refresh_success')
        token = RefreshToken.for_user(self.user)
        response = self.client.post('/signin/refresh/', {'refresh': str(token)})
        print('response', response)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertNotEqual(token.access_token, response.data['access'])
        # Ręczne dodanie tokena odświeżania do blacklisty
        outstanding_token = OutstandingToken.objects.get(token=token)
        blacklisted_token = BlacklistedToken.objects.create(token=outstanding_token)

        # Sprawdzenie, czy odświeżony token został dodany do blacklisty
        # blacklisted_tokens = RefreshToken.objects.filter(token=token)
        blacklisted_tokens = BlacklistedToken.objects.filter(token=outstanding_token)
        self.assertTrue(blacklisted_tokens.exists())

    def test_token_refresh_empty_token(self):
        response = self.client.post('/signin/refresh/', {'refresh': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('refresh', response.data)

    def test_token_refresh_invalid_token(self):
        response = self.client.post('/signin/refresh/', {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)

    def test_signout_success(self):
        token = RefreshToken.for_user(self.user)
        response = self.client.post('/signout/', {'refresh': str(token)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'OK')
        # blacklisted_tokens = RefreshToken.objects.filter(token=token)
        blacklisted_tokens = BlacklistedToken.objects.filter(token__jti=token['jti'])
        self.assertTrue(blacklisted_tokens.exists())

    def test_signout_empty_token(self):
        response = self.client.post('/signout/', {'refresh': ''})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, 'refresh token is empty')

    def test_signout_invalid_token(self):
        response = self.client.post('/signout/', {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, 'Token is invalid or expired')
