# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from ..models import Property

class ScrapyItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = Property
