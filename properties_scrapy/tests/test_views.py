from properties_scrapy.models import Property
from unittest.mock import patch
from selenium.webdriver.common.by import By
from django.conf import settings
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from django.contrib.auth.models import User


class ScrapeSeleniumTestCase(LiveServerTestCase):
    def setUp(self):
        self.old_debug = settings.DEBUG
        settings.DEBUG = True

        self.user = User.objects.create_user("testuser", password="password")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        webdriver_service = Service('chromedriver')
        self.driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        self.driver.set_window_size(1280, 1024)
        # self.driver = webdriver.Chrome('chromedriver')

    def tearDown(self):
        self.driver.quit()
        settings.DEBUG = self.old_debug

    def handle_login(self):
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        submit_button = self.driver.find_element(By.XPATH, '//input[@type="submit"]')

        # Wprowadź dane logowania
        username_input.send_keys('testuser')
        password_input.send_keys('password')

        # Zaloguj się
        submit_button.click()

    def test_login(self):
        self.driver.get(self.live_server_url + '/scrapy/crawl/')

        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        submit_button = self.driver.find_element(By.XPATH, '//input[@type="submit"]')

        # Wprowadź dane logowania
        username_input.send_keys('testuser')
        password_input.send_keys('password')

        # Zaloguj się
        submit_button.click()

        # Sprawdź, czy użytkownik jest zalogowany i przekierowany na inną stronę
        self.assertEqual(self.driver.current_url, self.live_server_url + '/scrapy/crawl/')

    def test_search_with_google_maps_suggestion(self):
        self.driver.get(f"{self.live_server_url}/scrapy/crawl/")

        self.handle_login()

        # Znajdź pole adresu i wpisz "Jaktorów"
        address_input = self.driver.find_element(By.ID, 'id_address')
        address_input.clear()
        address_input.send_keys('Jaktorów')

        # Poczekaj na pojawienie się sugestii z Google Maps
        self.driver.implicitly_wait(1)

        # Wybierz pierwszą sugestię z Google Maps
        suggestions = self.driver.find_elements(By.CLASS_NAME, 'pac-item')
        suggestions[0].click()

        # Sprawdź, czy wartość pola adresu została ustawiona na wybraną sugestię
        self.assertEqual(address_input.get_attribute('value'), 'Jaktorów, Polska')

        # Znajdź przycisk submit i kliknij go
        # Ten kod spowoduje wyszukiwanie po tych serwisach, trzeba by najpierw dać mockowanie żeby zrobić to bezpiecznie
        # submit_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        # submit_button.click()

    def handle_form(self):
        # Wypełnij pozostałe pola formularza
        self.driver.find_element(By.ID, 'id_address').clear()
        self.driver.find_element(By.ID, 'id_province').clear()
        self.driver.find_element(By.ID, 'id_city').clear()
        self.driver.find_element(By.ID, 'id_district').clear()
        self.driver.find_element(By.ID, 'id_district_neighbourhood').clear()
        self.driver.find_element(By.ID, 'id_street').clear()
        self.driver.find_element(By.ID, 'id_price_min').clear()
        self.driver.find_element(By.ID, 'id_price_max').clear()
        self.driver.find_element(By.ID, 'id_area_min').clear()
        self.driver.find_element(By.ID, 'id_area_max').clear()
        self.driver.find_element(By.ID, 'id_build_year_from').clear()
        self.driver.find_element(By.ID, 'id_build_year_to').clear()

        self.driver.find_element(By.ID, 'id_address').send_keys('Grodzisk Mazowiecki, Polska')
        self.driver.find_element(By.ID, 'id_province').send_keys('Mazowieckie')
        self.driver.find_element(By.ID, 'id_city').send_keys('Grodzisk Mazowiecki')
        self.driver.find_element(By.ID, 'id_price_min').send_keys('300000')
        self.driver.find_element(By.ID, 'id_price_max').send_keys('400000')
        # self.driver.find_element(By.ID, 'id_property_type').send_keys('flat')
        # self.driver.find_element(By.ID, 'id_offer_type').send_keys('sell')

        # Wyślij formularz
        # time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, 'form input[type="submit"]').click()

    def test_scrape_view(self):
        # Test widoku scrape
        # Użyj biblioteki Selenium do wypełnienia formularza i wysłania żądania
        # Sprawdź oczekiwane rezultaty

        print(';;;;;;;;;;;;;;;;;;;; DEBUG', settings.DEBUG)
        # Zmockowanie metody create_spider w ScrapyFactory
        with patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory.__init__') as mock_init, \
                patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory.create_spiders') as mock_create_spider, \
                patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory.job_ids', ["75d6b108cc9811edba0300155d7be260"]), \
                patch('properties_scrapy.scrapy_factory.ScrapydSpiderFactory.check_finished') as mock_check_finished:
            # Zmockowanie parse i parse_offer w scrapy spiderze
            # mock_spider = mock_create_spider.return_value
            # mock_spider.parse.return_value = None
            mock_init.return_value = None
            mock_create_spider.return_value = None
            mock_check_finished.return_value = True
            Property.objects.create(scrapyd_job_id="75d6b108cc9811edba0300155d7be260", service_name='test',
                                    service_url='www.test.pl', price=350000, area=50, province='Mazowieckie',
                                    city='Grodzisk Mazowiecki', property_type='flat', offer_type='sell')

            self.driver.get(f"{self.live_server_url}/scrapy/crawl/")
            self.handle_login()
            self.handle_form()
            self.driver.save_screenshot('test_data/test_scrape_view.png')
            # time.sleep(10)
            self.assertIn("Finished", self.driver.page_source)
            elements = self.driver.find_elements(By.CLASS_NAME, "scrapy-item")
            self.assertTrue(len(elements) > 0)
