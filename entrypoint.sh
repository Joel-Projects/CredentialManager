#!/bin/bash

REQUIRED_ENV_VARS="APP_HOME CERTBOT_EMAIL HOSTNAME"

for val in $REQUIRED_ENV_VARS; do
  if [[ -z "${!val}" ]]; then
    echo "Environment variable $val is not set. Exiting..."
    exit 1
  fi
done
if [ ! -f "$APP_HOME/cloudflare.ini" ]; then
  if [[ "${DNS_CLOUDFLARE_API_TOKEN}" ]]; then
    echo "dns_cloudflare_api_token = $DNS_CLOUDFLARE_API_TOKEN" > $APP_HOME/cloudflare.ini
  elif [[ "${DNS_CLOUDFLARE_EMAIL}" && "${DNS_CLOUDFLARE_API_KEY}" ]]; then
    echo "dns_cloudflare_email = $DNS_CLOUDFLARE_EMAIL" > cloudflare.ini
    echo "dns_cloudflare_api_key = $DNS_CLOUDFLARE_API_KEY" >> cloudflare.ini
  else
    echo "Either DNS_CLOUDFLARE_API_TOKEN or (DNS_CLOUDFLARE_EMAIL and DNS_CLOUDFLARE_API_KEY) must be set in $APP_HOME/cloudflare.ini or as environment variables. Exiting..."
    exit 1
  fi
fi

chmod 600 $APP_HOME/cloudflare.ini
chown letsencrypt:letsencrypt $APP_HOME/cloudflare.ini
echo "05 5,17 * * * /usr/bin/certbot renew -q
" | gosu letsencrypt crontab -
service cron start
gosu letsencrypt certbot certonly -n \
  --agree-tos \
  --dns-cloudflare \
  --dns-cloudflare-credentials $APP_HOME/cloudflare.ini \
  -d $HOSTNAME \
  -m $CERTBOT_EMAIL

gosu app gunicorn
