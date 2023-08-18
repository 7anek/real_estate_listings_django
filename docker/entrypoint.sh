#!/bin/bash

python manage.py makemigrations
python manage.py migrate

#tmux new-session -d -s scrapyd 'cd /app/properties_scrapy && scrapyd' && \
#    cd /app && gunicorn --config docker/gunicorn.conf.py real_estate_listings.wsgi:application
echo "000000000000000000 ENVIRONMENT: $ENVIRONMENT"
if [ "$ENVIRONMENT" = "production" ]; then
    echo "production"

    apt-get update
    apt-get install -y wget
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar zxvf  ngrok-v3-stable-linux-amd64.tgz
    mv ngrok /usr/local/bin/
    chmod +x /usr/local/bin/ngrok
#    echo "000000000000000000 NGROK_API_KEY: $NGROK_API_KEY"
#    echo "Current directory: $(pwd)"
    ngrok config add-authtoken "$NGROK_API_KEY"

    # Uruchomienie procesu scrapyd w tle
    cd /app/properties_scrapy && scrapyd &

    # Uruchomienie procesu gunicorn w tle
    cd /app && gunicorn --config docker/gunicorn.conf.py real_estate_listings.wsgi:application &

    # Poczekaj chwilę, aby dać procesom czas na uruchomienie (opcjonalne)
    sleep 5

    # Uruchomienie ngrok
    ngrok http --domain="$NGROK_URL" 8000

    # Zakończenie skryptu
    echo "Skrypt został wykonany"
else
    # Zainstaluj tmux do otwierania nowych zakładem konsoli i odpalania tam zadań w tle, potrzebne do uruchomienia scrapyd
    apt-get update && apt-get install -y tmux
    echo "not production"
    tmux new-session -d -s scrapyd 'cd /app/properties_scrapy && scrapyd' && \
        cd /app && gunicorn --config docker/gunicorn.conf.py real_estate_listings.wsgi:application
fi