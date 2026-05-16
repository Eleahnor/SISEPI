#!/bin/bash

echo "=== SISEPI - Iniciando servicios ==="

# Limpiar contenedores anteriores
docker-compose down -v 2>/dev/null

# Construir imágenes
echo "Construyendo imágenes..."
docker-compose build

# Iniciar servicios
echo "Iniciando servicios..."
docker-compose up -d

# Esperar
sleep 3

# Mostrar estado
echo ""
echo "=== Servicios activos ==="
docker-compose ps

echo ""
echo "=========================================="
echo "✅ SISEPI está corriendo!"
echo "🌐 Abre en tu navegador: http://localhost:8080"
echo "=========================================="
echo ""
echo "Para ver logs: docker-compose logs -f"
echo "Para detener: docker-compose down"