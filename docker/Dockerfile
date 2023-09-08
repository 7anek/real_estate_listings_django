# Plik Dockerfile dla aplikacji Django

# Użyj obrazu bazowego Pythona
FROM python:3.10

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

RUN apt-get update && apt-get upgrade -y
#do bazy danych postgis
RUN apt-get install -y libgdal-dev
#do bazy danych postgis
RUN #pip install GDAL==3.2.2.1

# Skopiuj plik requirements.txt do kontenera
COPY requirements.txt .

# Zainstaluj zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

#scrapyd - do uruchamiania spiderów scrapy
RUN pip install git+https://github.com/scrapy/scrapyd-client.git

RUN pip install webdriver-manager

# Zainstaluj tmux do otwierania nowych zakładem konsoli i odpalania tam zadań w tle, potrzebne do uruchomienia scrapyd
#RUN apt-get update && apt-get install -y tmux

# Skopiuj resztę projektu do kontenera
COPY . .

RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]
# Uruchom serwer Django oraz uruchom Scrapyd w osobnej zakładce konsoli tmux
#CMD tmux new-session -d -s scrapyd 'cd /app/properties_scrapy && scrapyd' && \
#    cd /app && gunicorn --config docker/gunicorn.conf.py real_estate_listings.wsgi:application


