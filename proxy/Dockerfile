FROM debian:stable

RUN apt-get update && \
    apt-get -y install \
        nginx \
        vim

VOLUME /ssl
EXPOSE 80
EXPOSE 443

ADD . /proxy
RUN chmod -R 777 /proxy
CMD /proxy/boot.sh
