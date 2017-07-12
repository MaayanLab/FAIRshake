FROM debian:stable

RUN apt-get update
RUN apt-get -y install vim
RUN apt-get -y install python python-dev python-pip python-setuptools
RUN apt-get -y install nginx uwsgi-core

RUN pip install -Iv Flask flask-cors requests uwsgi flask-login flask-mysql

EXPOSE 80

ADD . /lwfairness
RUN chmod -R 777 /lwfairness
CMD /lwfairness/boot.sh
