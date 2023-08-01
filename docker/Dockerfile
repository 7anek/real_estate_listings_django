# Plik Dockerfile dla aplikacji Django

# Użyj obrazu bazowego Pythona
FROM python:3.10

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y libgdal-dev

RUN pip install GDAL==3.2.2.1

# Skopiuj plik requirements.txt do kontenera
#COPY ../../requirements.txt .
COPY requirements.txt .

# Zainstaluj zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install git+https://github.com/scrapy/scrapyd-client.git

# Zainstaluj tmux
RUN apt-get update && apt-get install -y tmux

#biblioteki do przeglądarki Chrome
RUN #apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2




# Skopiuj resztę projektu do kontenera
COPY .. .

#ENV SCRAPYD_URL="http://django"
#ENV SCRAPYD_PROJECT="default"

#WORKDIR /app/properties_scrapy

#CMD ["scrapyd &"]
#CMD scrapyd &
#CMD ["scrapyd"]

# Uruchom Scrapyd w osobnej zakładce konsoli tmux
CMD tmux new-session -d -s scrapyd 'cd /app/properties_scrapy && scrapyd' && \
    cd /app && gunicorn --config docker/gunicorn.conf.py real_estate_listings.wsgi:application
# Uruchom serwer Django

#WORKDIR /app
##CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["gunicorn", "--config", "gunicorn.conf.py", "real_estate_listings.wsgi:application"]

