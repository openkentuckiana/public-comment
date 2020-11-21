FROM python:3.8

RUN apt-get update && \
	apt-get install zlib1g-dev binutils libproj-dev gdal-bin libgeoip1 python-gdal -y && \
	apt-get install python3-pip git -y && \
	apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi gettext postgresql-client -y && \
	pip3 install pipenv && \
	apt-get clean

RUN mkdir /app
WORKDIR /app

ADD Pipfile .
ADD Pipfile.lock .

# arg to pass to pipenv. useful for passing in `dev` when dev dependencies are needed.
ARG pipenv_arg=
RUN pipenv install --system --ignore-pipfile $pipenv_arg

ADD ./public_comment/ /app

ENV REDISCLOUD_URL=UNSET
ENV DJANGO_SETTINGS_MODULE=public_comment.settings.base
RUN python manage.py compilescss
RUN python manage.py collectstatic --noinput --ignore=*.scss

ENV DJANGO_SETTINGS_MODULE=public_comment.settings.production

CMD /app/docker-entrypoint.sh