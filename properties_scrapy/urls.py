from django.urls import path
from properties_scrapy import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(template_name="properties/login.html"), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("crawl/", views.crawl, name="crawl"),
    # path("scrape/<uuid:scrape_job_id>", views.get_scrape, name="get_scrape")
    path("crawl/<str:uuids>", views.get_crawl, name="get_crawl")
]