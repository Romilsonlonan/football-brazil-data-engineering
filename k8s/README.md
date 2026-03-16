# Kubernetes - Lakehouse Brasileiro

Este diretório contém os manifestos Kubernetes para deploy do Lakehouse.

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `secret-fernet-key.yaml` | Secrets para credenciais e chaves de criptografia |
| `configmap-airflow.yaml` | ConfigMap com variáveis de ambiente |
| `rbac.yaml` | Configuração RBAC para o Airflow |
| `services.yaml` | Services e PersistentVolumeClaims |
| `airflow-deployment.yaml` | Deployments do Airflow (webserver, scheduler, triggerer) |

## Pré-requisitos

- Kubernetes 1.24+
- kubectl configurado
- StorageClass disponível (padrão: `standard`)

## Instalação

### 1. Criar namespace
```bash
kubectl create namespace lakehouse
```

### 2. Aplicar Secrets e ConfigMaps
```bash
kubectl apply -f k8s/secret-fernet-key.yaml
kubectl apply -f k8s/configmap-airflow.yaml
```

### 3. Aplicar RBAC
```bash
kubectl apply -f k8s/rbac.yaml
```

### 4. Aplicar Services e PVCs
```bash
kubectl apply -f k8s/services.yaml
```

### 5. Aplicar Deployments
```bash
kubectl apply -f k8s/airflow-deployment.yaml
```

## Verificar Status

```bash
# Ver pods
kubectl get pods -n lakehouse

# Ver services
kubectl get svc -n lakehouse

# Ver PVCs
kubectl get pvc -n lakehouse

# Ver secrets
kubectl get secrets -n lakehouse
```

## Acessar Airflow

```bash
# Port forward para o webserver
kubectl port-forward -n lakehouse svc/airflow-webserver 8080:8080

# Ou verificar o IP externo
kubectl get svc -n lakehouse airflow-webserver
```

Acesse: http://localhost:8080 (ou IP externo)
- Usuário: admin
- Senha: admin

## Limpar Recursos

```bash
kubectl delete -f k8s/
kubectl delete namespace lakehouse
```

## Notas de Segurança

### Fernet Key

A chave Fernet é usada para criptografar:
- Conexões de banco de dados
- Variáveis sensíveis
- Configurações de API

**IMPORTANTE:**
1. **NUNCA versione a chave em repositórios Git**
2. Gere sua própria chave: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
3. Armazene a chave em local seguro (password manager, HashiCorp Vault, AWS Secrets Manager, etc.)
4. Em produção, use um secret manager externo

### Credenciais

As credenciais neste exemplo são para **desenvolvimento apenas**:
- Altere senhas em produção
- Use secrets externos
- Implemente rotação de senhas

## Troubleshooting

### Pod não inicia
```bash
kubectl describe pod <pod-name> -n lakehouse
kubectl logs <pod-name> -n lakehouse
```

### Problemas de permissão
```bash
# Verificar service account
kubectl get sa airflow -n lakehouse

# Verificar role bindings
kubectl get rolebindings -n lakehouse
```

### Problemas de storage
```bash
# Ver eventos de PVC
kubectl describe pvc <pvc-name> -n lakehouse

# Ver storage classes disponíveis
kubectl get storageclass
```
