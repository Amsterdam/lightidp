#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

# source /app/docker-wait.sh

# run uwsgi
exec uwsgi --ini /app/uwsgi.ini
