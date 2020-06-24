FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y apt-utils vim curl apache2 apache2-utils
RUN apt-get -y install python3 libapache2-mod-wsgi-py3
RUN ln /usr/bin/python3 /usr/bin/python
RUN apt-get -y install python3-pip
RUN ln /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
RUN pip install django==1.11.29 ptvsd
ADD ./site.conf /etc/apache2/sites-available/000-default.conf
EXPOSE 80 3500 81

ARG DJANGO_ENV

ENV PYTHONUNBUFFERED=1
ENV WEBAPP_DIR=/var/www/html/msbacklog

RUN groupadd varwwwusers
RUN adduser www-data varwwwusers
RUN chgrp -R varwwwusers /var/www/
RUN usermod -a -G varwwwusers root
RUN chmod -R 770 /var/www/

WORKDIR $WEBAPP_DIR

ADD requirements/base.txt $WEBAPP_DIR/ 
ADD requirements/$DJANGO_ENV.txt $WEBAPP_DIR/

RUN pip install -r $DJANGO_ENV.txt

RUN python -m spacy download es_core_news_sm
RUN python -m spacy download es_core_news_md
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download en_core_web_md

ADD . $WEBAPP_DIR/

CMD ["apache2ctl", "-D", "FOREGROUND"]