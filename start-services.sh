#!/bin/bash
# ============================================
# Script de Inicialização - Lakehouse
# ============================================
# Este script inicia todos os serviços do Lakehouse

set -e

echo "============================================"
echo "🚀 Lakehouse - Inicializando Serviços"
echo "============================================"

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "AIRFLOW_UID=$(id -u)" >> .env
    echo "AIRFLOW_GID=$(id -g)" >> .env
    echo "SUPERSET_UID=$(id -u)" >> .env
    echo "SUPERSET_GID=$(id -g)" >> .env
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p dags
mkdir -p data/bronze
mkdir -p data/silver
mkdir -p data/gold
mkdir -p logs

# Iniciar serviços
echo "🐳 Iniciando containers Docker..."
docker compose up -d

echo ""
echo "============================================"
echo "✅ Serviços Iniciados!"
echo "============================================"
echo ""
echo "🌐 Interfaces Disponíveis:"
echo "   - Airflow:     http://localhost:8080"
echo "   - Superset:    http://localhost:8088"
echo "   - MinIO:       http://localhost:9000"
echo "   - MinIO UI:    http://localhost:9001"
echo ""
echo "📝 Credenciais: Ver arquivo .env (NÃO versione!)"
echo ""
echo "📝 Para ver os logs:"
echo "   docker compose logs -f"
echo ""
echo "⏹️  Para parar os serviços:"
echo "   docker compose down"
echo ""
echo "============================================"
echo "🚀 Kubernetes - Deploy"
echo "============================================"
echo ""
echo "Para fazer deploy no Kubernetes:"
echo ""
echo "1. Criar namespace:"
echo "   kubectl create namespace lakehouse"
echo ""
echo "2. Aplicar manifestos:"
echo "   kubectl apply -f k8s/secret-fernet-key.yaml"
echo "   kubectl apply -f k8s/configmap-airflow.yaml"
echo "   kubectl apply -f k8s/rbac.yaml"
echo "   kubectl apply -f k8s/services.yaml"
echo "   kubectl apply -f k8s/airflow-deployment.yaml"
echo ""
echo "3. Verificar status:"
echo "   kubectl get pods -n lakehouse"
echo ""
echo "4. Acessar Airflow:"
echo "   kubectl port-forward -n lakehouse svc/airflow-webserver 8080:8080"
echo ""
