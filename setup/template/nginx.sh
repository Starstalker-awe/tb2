#!/bin/sh
domain=$1
cat << EOF
server {
    listen 80;
    server_name $domain;

    location / {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        include proxy_params;
        proxy_pass http://unix:/home/$(id -u -n)/tb2/tb2.sock;
    }
}