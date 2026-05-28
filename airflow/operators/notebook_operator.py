from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from docker import DockerClient
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_NOTEBOOK_DIR = '/home/jovyan/work/src/'
BASE_NOTEBOOK_DIR_EXEC = '/home/jovyan/work/logs/'

class NotebookOperator(BaseOperator):
    """
    Operador customizado para executar notebooks no container Jupyter
    
    :param notebook_path: Caminho do notebook dentro do container
    :param output_path: Caminho para salvar notebook executado
    :param parameters: Dict com parâmetros para o notebook
    :param container_name: Nome do container Jupyter
    """
    
    template_fields = ('notebook_path', 'output_path', 'parameters')
    
    def __init__(
        self,
        notebook_path: str,
        output_path: Optional[str] = None,
        parameters: Optional[Dict] = None,
        container_name: str = 'jupyter',
        **kwargs
    ):
        super().__init__(**kwargs)
        self.notebook_path = BASE_NOTEBOOK_DIR + notebook_path
        self.output_path = output_path or BASE_NOTEBOOK_DIR_EXEC + Path(BASE_NOTEBOOK_DIR + notebook_path).name.replace('.ipynb', '_executed.ipynb')
        self.parameters = parameters or {}
        self.container_name = container_name
    
    def execute(self, context):
        client = DockerClient(base_url='unix:///var/run/docker.sock')
        
        try:
            container = client.containers.get(self.container_name)
        except Exception as e:
            raise Exception(f"Container {self.container_name} não encontrado: {str(e)}")
        
        # Construir comando
        cmd = f"papermill {self.notebook_path} {self.output_path}"
        
        if self.parameters:
            for key, value in self.parameters.items():
                if isinstance(value, str):
                    value = f'"{value}"'
                cmd += f" -p {key} {value}"
        
        self.log.info(f"Executando: {cmd}")
        
        exit_code, output = container.exec_run(cmd=cmd, user='root')
        
        output_str = output.decode('utf-8')
        
        if exit_code != 0:
            self.log.error(f"Notebook falhou: {output_str}")
            raise Exception(f"Notebook execution failed\n{output_str}")
        
        self.log.info(f"Notebook executado com sucesso em {self.output_path}")
        
        return {
            'output_notebook': self.output_path,
            'exit_code': exit_code,
        }