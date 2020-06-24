#!/bin/bash

GITHUB_WEBHOOKS_SECRET="THIS IS SECRET" \
    gunicorn \
        -b :8080 \
        --log-level debug \
        --access-logfile gunicorn_access.log \
        --error-logfile gunicorn_error.log \
        gunicorn_server
