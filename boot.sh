#!/usr/bin/env bash

user=r

diskroot=/fairshake
sslroot=$diskroot/ssl
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
processes = 5

chdir = $diskroot
wsgi-file = $diskroot/wsgi.py

socket = 127.0.0.1:8080
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

        charset utf-8;
        client_max_body_size 20M;
        sendfile on;
        keepalive_timeout 0;
        large_client_header_buffers 8 32k;

        location $webroot/static  {
            alias $diskroot/app/static;
        }

        location / {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         127.0.0.1:8080;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
        }
    }
}
EOF

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
