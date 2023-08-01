# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from asgiref.sync import sync_to_async
from properties_scrapy.models import Property


class PropertiesScrapyPipeline:

    @sync_to_async
    def process_item(self, item, spider):
        print('|||||||||||||||||||| ScraperPipeline process_item')
        print('ScraperPipeline Property.objects.all().count()', Property.objects.all().count())
        # p = Property.objects.create(service_name='b', service_url='b', price=1, area=1, property_type='b')
        # print('ScraperPipeline Property.objects.all().count()', Property.objects.all().count())

        if item["service_id"]:
            existing_objects = Property.objects.filter(
                service_id=item["service_id"], service_name=item["service_name"]
            )
            print('existing_objects', existing_objects)
            if existing_objects:
                existing_objects.first().delete()
                print('|||||||||||||||||||| ScraperPipeline existing_object deleted')
        item.save()
        print('|||||||||||||||||||| ScraperPipeline item saved')
