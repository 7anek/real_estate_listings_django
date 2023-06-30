from django.urls import path, include
from rest_framework.routers import DefaultRouter
from properties_api.views import PropertyListAPIView, PropertyViewSet, PropertiesScrape, SignIn, SignOut, SignUp
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

app_name = 'properties_api'

router = DefaultRouter()
router.register('', PropertyViewSet)
# router.register('', PropertyListAPIView, basename='property')
# router.register('properties/search',PropertiesSearch, basename='propertiessearch')
# router.register('properties/<int:pk>', PropertyViewSet, basename='property')
# urlpatterns = router.urls
urlpatterns = [
    path('properties/', include(router.urls)),
    path('', PropertyListAPIView.as_view()),
    path('scrape', PropertiesScrape.as_view(), name='scrape'),
    # path('properties/scrape/<uuid:scrape_job_id>', PropertiesScrape.as_view(), name='properties_get_scrape'),
    path('scrape/<str:job_ids>', PropertiesScrape.as_view(), name='get_scrape'),
    path('signup/', SignUp.as_view(), name='sign_up'),
    path('signin/', SignIn.as_view(), name='token_obtain_pair'),
    path('signin/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signout/', SignOut.as_view(), name='token_blacklist'),
]

