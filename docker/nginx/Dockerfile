FROM python:3.10

RUN pip install awscli

FROM nginx:latest

RUN mkdir -p /usr/src/app/static/

COPY nginx.conf /etc/nginx/nginx.conf
COPY sites-available/django.conf /etc/nginx/sites-available/django.conf

#USER root
#RUN ln -s /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled/django.conf
