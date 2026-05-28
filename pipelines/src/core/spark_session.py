import os

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

def build_spark(app_name: str = "PySparkJupyter") -> SparkSession:
    """
    Cria uma SparkSession pronta para usar JDBC do Postgres.
    Requer o driver .jar já presente em /usr/local/spark/jars (feito no Dockerfile).
    """
    # Opções comuns; ajuste conforme seu caso
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        # Recomendações para Arrow/Parquet e performance em notebook
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.sql.shuffle.partitions", "200")
        .getOrCreate()
    )

    # Variáveis do Postgres, lidas do ambiente (passadas pelo docker-compose)
    spark.conf.set("spark.app.postgres.host", "postgres")
    spark.conf.set("spark.app.postgres.port", os.getenv("POSTGRES_PORT"))
    spark.conf.set("spark.app.postgres.db", os.getenv("POSTGRES_DB"))
    spark.conf.set("spark.app.postgres.user", os.getenv("POSTGRES_USER"))
    spark.conf.set("spark.app.postgres.password", os.getenv("POSTGRES_PASSWORD"))

    return spark

def jdbc_url() -> str:
    host = "postgres"
    port = os.getenv("POSTGRES_PORT")
    db   = os.getenv("POSTGRES_DB")
    return f"jdbc:postgresql://{host}:{port}/{db}"

def jdbc_props() -> dict:
    return {
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "driver": "org.postgresql.Driver",
        # "ssl": "true",  # habilite se necessário
    }

def read_table(spark_session, table_name) -> DataFrame:
    df = spark_session.read.jdbc( \
        url=jdbc_url(), \
        table=table_name, \
        properties=jdbc_props() \
    )

    return df

def write_table(df, schema, table, mode) -> None: 
    df.write.jdbc( \
        url=jdbc_url(), \
        table=f"{schema}.{table}", \
        mode=mode, \
        properties=jdbc_props() \
    )


def run_sql(sql_command) -> None:
    import psycopg2

    try:
        conn = psycopg2.connect(database = os.getenv("POSTGRES_DB"),
                            host= "postgres",
                            user = os.getenv("POSTGRES_USER"),
                            password = os.getenv("POSTGRES_PASSWORD"),
                            port = os.getenv("POSTGRES_PORT"))

        cursor = conn.cursor()
        cursor.execute(sql_command)
        
        conn.commit() 

        print(cursor.statusmessage)

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(e)
        raise e

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()