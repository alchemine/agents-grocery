#!/bin/bash

# Export user id and group id
export UID=$(id -u)
export GID=$(id -g)

# Create network
docker network create base-network

# Create volumes
docker volume create base-database

# Run docker compose
docker compose -f docker/docker-compose.yml up -d --build