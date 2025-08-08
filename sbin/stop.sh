#!/bin/bash

# Export user id and group id
export UID=$(id -u)
export GID=$(id -g)

# Stop docker compose
docker compose -f docker/docker-compose.yml down

# Remove volumes
docker volume rm base-database

# Remove network
docker network rm base-network