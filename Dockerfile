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

ADD requirements.txt /requirements.txt
RUN pip install -Ivr /requirements.txt

ENV CONFIG=/ssl/config.py
VOLUME /ssl
EXPOSE 8080

ADD . /fairshake
RUN chmod -R 777 /fairshake
CMD /fairshake/boot.sh
