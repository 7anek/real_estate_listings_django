from django import forms
from django.conf import settings
from datetime import date


PROPERTY_TYPE_CHOICES = [
    ('flat', 'Mieszkanie'),
    ('house', 'Dom'),
    ('plot', 'Działka'),
    ('garage', 'Garaż'),
]

PLOT_TYPE_CHOICES = [
    (None, 'Brak'),
    ('agricultural', 'Rolna'),
    ('building', 'Budowlana'),
    ('recreational', 'Rekreacyjna'),
    ('forest', 'Leśna'),
]

OFFER_TYPE_CHOICES = [
    ('sell', 'Sprzedaż'),
    ('rent', 'Wynajem'),
]

HOUSE_TYPE_CHOICES = [
    (None, 'Brak'),
    ('detached_house', 'Dom wolnostojący'),
    ('semi_detached_house', 'Bliźniak'),
    ('terraced_house', 'Szeregowiec'),
]

FLAT_TYPE_CHOICES = [
    (None, 'Brak'),
    ('block_of_flats', 'Blok'),
    ('tenement', 'Kamienica'),
    ('apartament', 'Apartamentowiec')
]

class SearchForm(forms.Form):
    # area = forms.FloatField()
    # price = forms.FloatField()
    # number_of_rooms = forms.IntegerField()
    # description = forms.CharField()
    # floor = forms.IntegerField()
    # nazwa = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Wpisz coś"}))
    # opis = forms.CharField(widget=forms.Textarea(attrs={"class": "nowa-klasa","rows":20,"cols":50,"id":"moje-id-dla-polatekstowego","placeholder":"Wpisz coś" }))
    #główne pola
    address = forms.CharField(required=False, initial="Grodzisk Mazowiecki")
    # google_maps_location_json=forms.JSONField(required=False)
    province=forms.CharField(required=False)#województwo
    # county=forms.CharField(required=False)#powiat
    city=forms.CharField(required=False)
    district=forms.CharField(required=False)
    district_neighbourhood=forms.CharField(required=False)#poddzielnica np Muranów
    street=forms.CharField(required=False)
    price_min = forms.IntegerField(min_value=0, max_value=10000000, required=False, initial=300000)
    price_max = forms.IntegerField(min_value=0, max_value=10000000, required=False, initial=400000)
    area_min = forms.IntegerField(min_value=0, max_value=1000, required=False)
    area_max = forms.IntegerField(min_value=0, max_value=1000, required=False)
    property_type = forms.ChoiceField(choices=PROPERTY_TYPE_CHOICES, required=False)
    offer_type = forms.ChoiceField(choices=OFFER_TYPE_CHOICES, required=False)
    #dodatkowe pola
    plot_type = forms.ChoiceField(choices=PLOT_TYPE_CHOICES, required=False)
    house_type = forms.ChoiceField(choices=HOUSE_TYPE_CHOICES, required=False)
    flat_type = forms.ChoiceField(choices=FLAT_TYPE_CHOICES, required=False)
    build_year_from = forms.IntegerField(min_value=1800, max_value=date.today().year+20, required=False)
    build_year_to = forms.IntegerField(min_value=1800, max_value=date.today().year+20, required=False)

    class Media:
        # js = (settings.STATIC_URL+'properties/google-maps-places.js', settings.STATIC_URL+'properties/search-form.js')
        js = (settings.STATIC_URL+'properties_scrapy/search-form.js',)
        # js = (f"https://maps.google.com/maps/api/js?key={settings.GOOGLE_MAPS_API_KEY}&libraries=places", settings.STATIC_URL+'properties/search-form.js')
        # https://maps.google.com/maps/api/js?key={{ google_maps_api_key }}&libraries=places"

    # def clean(self):
    #     cleaned_data = super().clean()
    #     unknown_fields = set(self.data.keys()) - set(self.fields.keys())
    #
    #     if unknown_fields:
    #         raise forms.ValidationError(f"Nieznane pola: {', '.join(unknown_fields)}")
    #
    #     return cleaned_data
