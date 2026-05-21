#!/bin/bash
set -e

# Conectar ao banco padrão como superuser
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  -- Criar banco de dados WDL
  CREATE DATABASE wdl;

  -- Criar banco de dados AIRFLOW
  CREATE DATABASE airflow;

  -- Criar usuário para WDL
  CREATE USER ${WDL_USER} WITH PASSWORD '${WDL_PASSWORD}';
  GRANT ALL PRIVILEGES ON DATABASE wdl TO ${WDL_USER};
  ALTER DATABASE wdl OWNER TO ${WDL_USER};

  -- Criar usuário para AIRFLOW
  CREATE USER ${AIRFLOW_USER} WITH PASSWORD '${AIRFLOW_PASSWORD}';
  GRANT ALL PRIVILEGES ON DATABASE airflow TO ${AIRFLOW_USER};
  ALTER DATABASE airflow OWNER TO ${AIRFLOW_USER};
EOSQL