#!/bin/bash
set -e

echo "============================================="
echo " SRE PROJECT - SETUP AUTOMÁTICO EN EC2"
echo "============================================="

# 0. Copiar .env de ejemplo si no existe
if [ ! -f /opt/proyecto-sre/.env ]; then
  cp /opt/proyecto-sre/.env.example /opt/proyecto-sre/.env
  echo "[0/8] Se creó .env a partir de .env.example (edítalo si es necesario)"
fi

# 1. Ampliar filesystem si el volumen se aumentó en consola AWS
echo "[1/8] Verificando y ampliando filesystem..."
if lsblk /dev/nvme0n1 | grep -q "20G" || lsblk /dev/nvme0n1 | grep -q "30G" || lsblk /dev/nvme0n1 | grep -q "50G"; then
  sudo growpart /dev/nvme0n1 1 2>/dev/null || true
  sudo resize2fs /dev/nvme0n1p1 2>/dev/null || echo "  resize: no necesario aún"
fi
df -h / | tail -1

# 2. Instalar Docker si no está (asumimos que ya está)
echo "[2/8] Verificando Docker..."
docker --version 2>/dev/null || (echo "Docker no instalado. Instalando..." && sudo bash /opt/instalar_docker.sh)

# 3. Subir proyecto con SCP desde local
echo "[3/8] Proyecto ya debe estar en /opt/proyecto-sre"

# 4. Desplegar Docker Compose
echo "[4/8] Desplegando Docker Compose..."
cd /opt/proyecto-sre
sudo chown -R ubuntu:ubuntu /opt/proyecto-sre
docker compose down 2>/dev/null || true
docker compose up -d --build

# 5. Esperar a que MySQL esté saludable
echo "[5/8] Esperando que MySQL esté listo..."
sleep 20
docker ps | grep servidor-bd

# 6. Configurar Nginx Proxy Manager
echo "[6/8] NPM desplegado en puerto 81 (configura manual: http://18.118.206.166:81)"

# 7. Configurar Uptime Kuma
echo "[7/8] Uptime Kuma en puerto 3001 (configura manual: http://18.118.206.166:3001)"

# 8. Verificar Dozzle
echo "[8/8] Dozzle en puerto 8080 (configura manual: http://18.118.206.166:8080)"

echo ""
echo "============================================="
echo " ESTADO FINAL DE CONTENEDORES"
echo "============================================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
