-- Script de inicialização do banco de dados Superset
-- Este script cria o usuário e banco de dados para o Apache Superset

-- Criar usuário superset se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'superset') THEN
        CREATE USER superset WITH PASSWORD 'superset';
    END IF;
END
$$;

-- Criar banco de dados superset se não existir
SELECT 'CREATE DATABASE superset'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'superset')\gexec

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE superset TO superset;

-- Conectar ao banco superset e criar extensões necessárias
\c superset

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Conceder privilégios no schema public
GRANT ALL ON SCHEMA public TO superset;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO superset;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO superset;

-- Permissões para o Airflow (para futuras integrações)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO airflow;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO airflow;
