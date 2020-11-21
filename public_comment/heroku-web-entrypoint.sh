#!/bin/bash

if [[ $NEW_RELIC_LICENSE_KEY ]]; then
    echo "Starting web with newrelic"
    NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn public_comment.wsgi --access-logfile -
else
    echo "Starting web without newrelic"
    gunicorn public_comment.wsgi --access-logfile -
fi