# Dockerfile

# FROM directive instructing base image to build upon
FROM python:3.7-buster


RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/searchapp
COPY requirements.txt start-server.sh /opt/app/
COPY .pip_cache /opt/app/pip_cache/
COPY mysite /opt/app/mysite/
COPY .env /opt/app/
WORKDIR /opt/app
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app

RUN python ./mysite/manage.py makemigrations
RUN python ./mysite/manage.py migrate
ENV GLEAN_LOG_PINGS true
ENV GLEAN_DEBUG_VIEW_TAG mlhackweek-search
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]