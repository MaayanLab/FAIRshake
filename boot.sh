#!/usr/bin/env bash

user=r

diskroot=/fairshake
sslroot=/ssl
log=$diskroot/error.log

servername=fairshake.cloud
webroot=

function setup {

echo "Creating user..." >> $log
adduser --disabled-password --gecos '' $user >> $log

echo "Writing wsgi.ini..." >> $log
cat << EOF | tee -a $diskroot/wsgi.ini >> $log
[uwsgi]
uid = $user
gid = $user
master = true
processes = 8
harakiri = 60
max-requests = 5000
vacuum = true

chdir = $diskroot

module = FAIRshake.wsgi:application
env = DJANGO_SETTINGS_MODULE=FAIRshake.settings

socket = 0.0.0.0:8080
daemonize = $log
EOF

echo "Writing nginx.conf..." >> $log
cat << EOF | tee -a $diskroot/nginx.conf >> $log
user $user $user;
worker_processes 1;
events {
    worker_connections 1024;
}
http {
    access_log $log;
    error_log $log;
    gzip              on;
    gzip_http_version 1.0;
    gzip_proxied      any;
    gzip_min_length   500;
    gzip_disable      "MSIE [1-6]\.";
    gzip_types        text/plain text/xml text/css
                      text/comma-separated-values
                      text/javascript
                      application/x-javascript
                      application/atom+xml;
    server {
        listen          80;
        server_name     $servername;
        rewrite ^/(.*)  https://\$host/\$1 permanent;
    }
    server {
        listen 443;
        server_name $servername;

        ssl on;
        ssl_certificate $sslroot/cert.crt;
        ssl_certificate_key $sslroot/cert.key;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';

        include /etc/nginx/mime.types;
        charset utf-8;
        client_max_body_size 20M;
        sendfile on;
        keepalive_timeout 0;
        large_client_header_buffers 8 32k;

        location / {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         127.0.0.1:8080;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
            proxy_read_timeout 60s;
            proxy_send_timeout 60s;
            uwsgi_read_timeout 60s;
            uwsgi_send_timeout 60s;
        }
        location /static/ {
            alias $diskroot/static/;
        }
        location /api_documentation/ {
            rewrite ^/api_documentation/(.*)$ https://\$server_name/documentation/\$1 redirect;
        }
        location ~ ^/v2/ {
            rewrite ^/v2/(.*)$ https://\$server_name/\$1 redirect;
        }
        location ~ ^/assessment/add/ {
            rewrite ^/assessment/add/(.*)$ https://\$server_name/assessment/perform/\$1 redirect;
        }
        location ~ ^/static/v2/ {
            rewrite ^/static/v2/(.*)$ https://\$server_name/v2/static/\$1 redirect;
        }
        location ~ ^/api/v2/ {
            rewrite ^/api/v2/$ https://\$server_name/v2/swagger/ redirect;
            rewrite ^/api/v2/(.+)$ https://\$server_name/v2/\$1 redirect;
            rewrite ^/api/v2/coreapi/(.*)$ https://\$server_name/v2/coreapi/\$1 redirect;
            rewrite ^/api/v2/static/(.*)$ https://\$server_name/v2/static/\$1 redirect;
        }
    }
}
EOF

echo "Preparing django..." >> $log
python3 $diskroot/manage.py collectstatic

echo "Starting uwsgi..." >> $log
uwsgi --ini $diskroot/wsgi.ini >> $log

echo "Starting nginx..." >> $log
nginx -c $diskroot/nginx.conf >> $log

}

if [ -f $log ]; then
    rm $log;
fi

echo "Booting..." > $log
setup &

tail -f $log
