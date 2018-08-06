#!/usr/bin/env bash

user=r

diskroot=/proxy
sslroot=/ssl
log=$diskroot/error.log

servername=localhost
webroot=

function setup {

echo "Creating user..." >> $log
adduser --disabled-password --gecos '' $user >> $log

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

        location / {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         fairshake:8080;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
        }

        location ~ ^/(v2|static/v2|api/v2)/ {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         django:8080;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
        }
    }
}
EOF

echo "Starting nginx..." >> $log
nginx -c $diskroot/nginx.conf >> $log

}

if [ -f $log ]; then
    rm $log;
fi

echo "Booting..." > $log
setup &

tail -f $log
