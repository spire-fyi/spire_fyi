#!/bin/bash
# see: https://blog.jarrousse.org/2022/04/09/an-elegant-way-to-use-docker-compose-to-obtain-and-renew-a-lets-encrypt-ssl-certificate-with-certbot-and-configure-the-nginx-service-to-use-it/

DOMAIN="spire.fyi"
EMAIL="info@spire.fyi"
 
# Phase 1
docker compose -f ./docker-compose-initiate.yml up -d nginx
docker compose -f ./docker-compose-initiate.yml up certbot
docker compose -f ./docker-compose-initiate.yml down
 
# some configurations for let's encrypt
curl -L --create-dirs -o etc/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
openssl dhparam -out etc/letsencrypt/ssl-dhparams.pem 2048
 
# Phase 2
# crontab ./etc/crontab
docker compose -f ./docker-compose.yml -d up