#!/bin/bash

GITHUB_WEBHOOKS_SECRET="THIS IS SECRET" \
    python3 \
        original/server.py 8080
