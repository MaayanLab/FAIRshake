FROM debian:stable

RUN apt-get update && \
    apt-get -y install \
        gcc \
        git \
        libffi-dev \
        libmariadb-dev \
        libmariadb-dev-compat \
        libpq-dev \
        nginx \
        python3 \
        python3-dev \
        python3-mysqldb \
        python3-pip \
        python3-setuptools \
        uwsgi-core \
        vim

ADD requirements.txt /requirements.txt
RUN pip3 install -Ivr /requirements.txt && \
    pip3 install -Iv uwsgi

VOLUME /config
EXPOSE 80
EXPOSE 443

ADD . /fairshake
RUN chmod -R 777 /fairshake
CMD /fairshake/boot.sh
