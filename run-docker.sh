#!/bin/bash
# This script starts the docker containers and loads the .env.dev file.

docker compose --env-file .env.dev up --build -d
