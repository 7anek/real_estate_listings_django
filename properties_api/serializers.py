from rest_framework import serializers
from properties_scrapy.models import Property


# from properties.search_results import SearchResults

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        # fields = ('id', 'title', 'price')
        fields = (
            'id', 'service_id', 'service_name', 'service_url', 'scrapyd_job_id', 'create_date', 'modify_date', 'title',
            'price', 'description', 'area', 'property_type', 'offer_type', 'regular_user', 'address', 'province',
            'county',
            'city','community', 'district', 'district_neighbourhood', 'street', 'floor', 'building_floors_num', 'rent', 'flat_type',
            'ownership', 'heating', 'market_type', 'construction_status', 'number_of_rooms', 'build_year', 'plot_type',
            'house_type', 'plot_area', 'garage_heating', 'garage_lighted', 'garage_localization', 'forest_vicinity',
            'open_terrain_vicinity', 'lake_vicinity', 'electricity', 'gas', 'sewerage', 'water', 'fence',
            'building_material')
        model = Property


class SearchResultSerializer(serializers.Serializer):
    offer_url = serializers.CharField()
    offer_url_path = serializers.CharField()
    main_image_url = serializers.CharField()
    title = serializers.CharField()
    price = serializers.CharField()
    price_per_square_meter = serializers.CharField()
    number_of_rooms = serializers.CharField()
    area = serializers.CharField()
    service = serializers.CharField()


class SearchResultsSerializer(serializers.Serializer):
    objects = serializers.ListField(child=SearchResultSerializer())
