FROM debian:stable

RUN apt-get update && \
    apt-get -y install \
        nginx \
        python3 \
        python3-dev \
        python3-pip \
        python3-mysqldb \
        python3-setuptools \
        vim \
        uwsgi-core

ADD requirements.txt /requirements.txt
RUN pip3 install -Ivr /requirements.txt

VOLUME /ssl
EXPOSE 80
EXPOSE 443

ADD . /fairshake
RUN chmod -R 777 /fairshake
CMD /fairshake/boot.sh
