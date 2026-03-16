#!/bin/bash
# ============================================
# Docker Entrypoint Script
# ============================================
# Este script garante permissões adequadas
# sem usar chmod 777 (prática insegura)

set -e

echo "==> Lakehouse Docker Entrypoint"
echo "==> User: $(whoami)"
echo "==> UID: $(id -u)"
echo "==> GID: $(id -g)"

# Garantir que diretórios críticos existam e tenham permissões corretas
echo "==> Configurando permissões de diretórios..."

# Criar diretórios se não existirem
mkdir -p /app/data/bronze
mkdir -p /app/data/silver
mkdir -p /app/data/gold
mkdir -p /app/logs

# Ajustar ownership para o usuário atual (não usa 777)
# Isso permite leitura/escrita sem expor a todos
chown -R "$(whoami):$(whoami)" /app/data 2>/dev/null || true
chown -R "$(whoami):$(whoami)" /app/logs 2>/dev/null || true

# Garantir permissões de execução em diretórios
chmod -R u+rwX /app/data 2>/dev/null || true
chmod -R u+rwX /app/logs 2>/dev/null || true

echo "==> Permissões configuradas"
echo "==> Estrutura de diretórios:"
ls -la /app/

# Executar comando passado
echo "==> Executando: $@"
exec "$@"
