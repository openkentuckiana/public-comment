#!/bin/bash

if [[ $NEW_RELIC_LICENSE_KEY ]]; then
    echo "Starting celery with newrelic"
    NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program /app/manage.py celery_worker
else
    echo "Starting celery without newrelic"
    /app/manage.py celery_worker
fi
