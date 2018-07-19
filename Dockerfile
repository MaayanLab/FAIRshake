FROM debian:stable

RUN apt-get update && \
    apt-get -y install \
        vim \
        python \
        python-dev \
        python-pip \
        python-setuptools \
        nginx \
        uwsgi-core

RUN pip install -Iv Flask flask-cors requests uwsgi flask-login flask-mysql validators

#VOLUME /fairshake/ssl
ADD ./ssl /fairshake/ssl
EXPOSE 8080

ADD . /fairshake
RUN chmod -R 777 /fairshake
CMD /fairshake/boot.sh
