# Real Estate Listings Search Engine

## Overview:
This project is a web application that allows users to search for real estate listings on popular classified ad websites, such as Otodom, OLX, Gratka, Morizon, and Domiporta. The application collects details of the found listings and stores them in a database. It is a web scraping project written in Python and built using the Django framework.

## Features:

### Search Form:
The application includes a custom search form that enables users to define search criteria for real estate listings. The form fields include options for address, province, county, city, municipality, district, sub-district, street, minimum and maximum price, minimum and maximum area, ad type, property type, plot type, house type, apartment type, and year of construction.

### Web Scraping (Scrapy):
The project utilizes the Scrapy framework for web crawling and parsing data from classified ad websites. When it is not possible to search automatically using the custom search form, the project employs the Selenium library to fill out forms on web pages.

### Django REST framework:
The application uses the Django REST framework to create an API that allows users to access functions such as setting up searches, checking search status, and browsing a list of real estate listings.

### Celery:
The Celery library is used to fetch a list of proxy servers. It is also used when creating Scrapy tasks and task queuing. The project bypasses website blocks using proxy IP addresses.

### PostGIS Database:
The project uses the PostGIS database, which supports geographic data, including longitude and latitude.

### Authentication:
The application has an authentication system that utilizes JWT (JSON Web Token) from Django REST framework for API access. Users are required to provide a username, email address, and password. After registration, a verification email is sent. In Django views, authentication is based on the standard Django user model, with additional fields for email verification.

### Testing:
All major project functions are covered by unit tests. Selenium is used for testing views. When testing code that queries external services, mock objects are used to control the return values of functions during testing. Note that tests related to web scraping may be misleading, as they are based on previously downloaded HTML code, and the structure of web pages may change.

### Docker:
The project is delivered as Docker containers. The docker-compose.yml file contains container configurations for an Nginx server, PostGIS database, Redis, and Selenium library.

## Running the Project:
To run the project, use the following command:
``` bash
sudo docker-compose --env-file env/.env.prod -f docker/docker-compose.yml up --build
```
