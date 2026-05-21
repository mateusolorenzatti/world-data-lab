# Base oficial dos Jupyter Docker Stacks com PySpark (Spark + Hadoop + Jupyter)
FROM quay.io/jupyter/pyspark-notebook:python-3.11.8

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalações de sistema úteis (opcional) e baixa o JDBC do Postgres
USER root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Versão recente do JDBC (ajuste se quiser outra)
ENV POSTGRES_JDBC_VERSION=42.7.3
RUN curl -fsSL -o /usr/local/spark/jars/postgresql-${POSTGRES_JDBC_VERSION}.jar \
    https://jdbc.postgresql.org/download/postgresql-${POSTGRES_JDBC_VERSION}.jar

# Volta pro usuário jovyan (default do stack)
USER ${NB_UID}

# Instale libs Python extras do projeto
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Cria uma pasta de "work" padrão
WORKDIR /home/jovyan/work