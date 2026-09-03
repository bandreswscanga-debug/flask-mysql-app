#!/bin/bash
set -e

echo "============================================="
echo " INSTALACIÓN DE DOCKER EN EC2 (Ubuntu)"
echo "============================================="

# Actualizar paquetes
sudo apt-get update -y
sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Agregar key de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Habilitar y arrancar Docker
sudo systemctl enable docker
sudo systemctl start docker

# Agregar usuario al grupo docker (evitar sudo)
sudo usermod -aG docker $USER

echo ""
echo "Docker instalado correctamente."
docker --version
docker compose version
echo "NOTA: Desconecta y vuelve a conectar (o ejecuta: newgrp docker) para usar docker sin sudo."
