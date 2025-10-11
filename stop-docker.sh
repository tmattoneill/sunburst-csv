#!/bin/bash
# This script stops the docker containers.

docker compose --env-file .env.dev down
