#!/bin/bash

# Nombre de la imagen y el contenedor
IMAGE_NAME=ollama-image
CONTAINER_NAME=ollama-container
NETWORK_NAME=ollama_network

# Construir la imagen de Docker
docker build -t $IMAGE_NAME .

# Iniciar el contenedor con la red existente en primer plano para ver los logs
docker run --rm --name $CONTAINER_NAME --network $NETWORK_NAME --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro $IMAGE_NAME

