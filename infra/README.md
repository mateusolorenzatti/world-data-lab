# Infraestrucutre

This folder contains Docker infrastructure for a development stack with:

- Jupyter + PySpark environment
- PostgreSQL database
- Apache Airflow scheduler and webserver

## Services

- `jupyter`: JupyterLab with PySpark, pandas, and SQL support.
- `postgres`: PostgreSQL backend for Airflow and other data workloads.
- `airflow-init`: initializes the Airflow metadata database and creates an admin user.
- `airflow-webserver`: Airflow web UI on port `8080`.
- `airflow-scheduler`: Airflow scheduler for DAG execution.

## Run

From the `infraestrucutre` folder:

```bash
docker compose up --build
```

Then access:

- JupyterLab: http://localhost:8888
- Airflow UI: http://localhost:8080

## Notes

- Airflow uses `LocalExecutor` with PostgreSQL metadata.
- DAGs, logs, and plugins are mounted from the host folders `dags`, `logs`, and `plugins`.
- Jupyter workspace files are mounted in `jupyter-work`.
