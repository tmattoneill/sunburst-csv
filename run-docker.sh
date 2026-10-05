#!/bin/bash
# Docker serves the frontend on 3000, the port the host nginx proxies to.
# .env.dev holds the Vue dev-server port (8080) for runapp.sh, so it must not
# be used here.

docker compose --env-file .env.prod up --build -d
