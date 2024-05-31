#!/bin/bash

# Create Postgres DB
docker stop postgres_re_miner_dashboard_bff
docker rm --rm postgres_re_miner_dashboard_bff
docker build -t postgres_re_miner_dashboard_bff -f db/Dockerfile.db db/

# Script vars
CONTAINER_NAME="re_miner_dashboard_bff"
IMAGE_NAME="mtiessler/re_miner_dashboard_bff:latest"

docker pull $IMAGE_NAME

docker stop $CONTAINER_NAME

docker rm $CONTAINER_NAME

docker run -d --name $CONTAINER_NAME -p 3001:3001 $IMAGE_NAME
