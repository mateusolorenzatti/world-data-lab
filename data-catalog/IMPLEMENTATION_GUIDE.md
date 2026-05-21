# 🚀 Guia Prático - Sistema de Catálogo de Tabelas SQL

## 1️⃣ SETUP INICIAL (5 minutos)

### Passo 1: Criar estrutura de diretórios
```bash
cd seu-projeto-world-data-lab

# Criar pastas
mkdir -p db/{catalog,migrations,scripts,reports}

# Criar arquivo de versão
echo "1.0.0" > db/version.txt

# Git ignore
cat > db/.gitignore << EOF
*.pyc
__pycache__/
.env
*.tmp
sync_report_*.md
sync_report_*.json
EOF

git add db/.gitignore
```

### Passo 2: Copiar arquivos necessários
```bash
# Copiar catálogo YAML
cp tables.yaml db/catalog/

# Copiar script de sincronização
cp catalog_sync.py db/scripts/
chmod +x db/scripts/catalog_sync.py

# Copiar requirements.txt
cat > db/scripts/requirements.txt << EOF
PyYAML==6.0
mysql-connector-python==8.0.33
EOF

pip install -r db/scripts/requirements.txt
```

### Passo 3: Validar catálogo
```bash
cd db/scripts
python catalog_sync.py --validate --catalog ../catalog/tables.yaml

# Esperado:
# 🔍 Validando catálogo...
# ✅ Catálogo válido!
```

---

## 2️⃣ PRIMEIRA SINCRONIZAÇÃO (10 minutos)

Se você já tem tabelas no banco, use este processo:

### Opção A: Criar BD novo (recomendado para projeto inicial)

```bash
# 1. Criar banco de dados vazio
mysql -u root -p << EOF
CREATE DATABASE world_data_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE world_data_lab;
EOF

# 2. Gerar SQL de criação do catálogo
python db/scripts/catalog_sync.py \
    --catalog db/catalog/tables.yaml \
    --report \
    --output-dir db/reports

# 3. Aplicar migration
mysql -u root -p world_data_lab < db/migrations/auto_migration.sql

# 4. Verificar
mysql -u root -p world_data_lab -e "SHOW TABLES;"
```

### Opção B: Documentar BD existente (migração suave)

Se você já tem BD com tabelas:

```bash
# 1. Fazer backup
mysqldump -u root -p world_data_lab > db/backups/backup_initial.sql

# 2. Extrair schema atual (criar script custom):
python << 'PYTHON'
import mysql.connector
from pathlib import Path

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='sua_senha',
    database='world_data_lab'
)

cursor = conn.cursor(dictionary=True)

# Query para extrair informações das tabelas
cursor.execute("""
    SELECT 
        TABLE_NAME,
        COLUMN_NAME,
        COLUMN_TYPE,
        IS_NULLABLE,
        COLUMN_KEY
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'world_data_lab'
    ORDER BY TABLE_NAME, ORDINAL_POSITION
""")

current_schema = {}
for row in cursor.fetchall():
    table = row['TABLE_NAME']
    if table not in current_schema:
        current_schema[table] = []
    
    current_schema[table].append({
        'name': row['COLUMN_NAME'],
        'type': row['COLUMN_TYPE'],
        'nullable': row['IS_NULLABLE'] == 'YES',
        'constraints': row['COLUMN_KEY'],
        'description': f"[TODO] Documentar campo {row['COLUMN_NAME']}"
    })

# Salvar em formato que possa ser importado no YAML
import json
Path('db/current_schema.json').write_text(json.dumps(current_schema, indent=2))

cursor.close()
conn.close()

print("✅ Schema extraído para db/current_schema.json")
print("👉 Próximo passo: integrar manualmente no YAML")
PYTHON

# 3. Usar db/current_schema.json para atualizar tables.yaml
```

---

## 3️⃣ WORKFLOW DIÁRIO (operacional)

### Cenário 1: Adicionar Nova Tabela

```yaml
# Editar db/catalog/tables.yaml

  nova_tabela_analise:
    description: "Novas análises de trends"
    category: "fact"
    created_at: "2025-05-21"
    owner: "seu_nome"
    status: "active"
    
    columns:
      - name: analise_id
        type: INTEGER
        constraints: "PRIMARY KEY, AUTO_INCREMENT"
        description: "ID único"
        nullable: false
      
      - name: pais_id
        type: INTEGER
        description: "Referência para dim_countries"
        nullable: false
      
      - name: valor_analise
        type: DECIMAL(10, 2)
        description: "Valor calculado"
        nullable: true
      
      - name: data_criacao
        type: TIMESTAMP
        constraints: "DEFAULT CURRENT_TIMESTAMP"
        description: "Data de criação"
        nullable: false
    
    indexes:
      - name: idx_pais_id
        columns: [pais_id]
        type: "BTREE"
    
    foreign_keys:
      - name: fk_pais
        column: pais_id
        references_table: dim_countries
        references_column: country_id
        on_delete: "CASCADE"
```

```bash
# Validar alteração
python db/scripts/catalog_sync.py \
    --catalog db/catalog/tables.yaml \
    --validate

# Gerar migration
python db/scripts/catalog_sync.py \
    --catalog db/catalog/tables.yaml \
    --report \
    --output-dir db/reports

# Revisar SQL gerado em db/migrations/
cat db/migrations/*auto_migration.sql

# Aplicar se correto
mysql -u root -p world_data_lab < db/migrations/auto_migration.sql

# Confirmar sincronização
python db/scripts/catalog_sync.py --validate
```

### Cenário 2: Adicionar Novo Campo

```yaml
# Em uma tabela existente (exemplo: fact_annual_indicators)

fact_annual_indicators:
  # ... campos existentes ...
  
  columns:
    # ... colunas anteriores ...
    
    - name: metadata_validacao  # ← NOVO CAMPO
      type: JSON
      description: "Metadados de validação da coleta"
      nullable: true
```

```bash
# Mesmo processo anterior
python db/scripts/catalog_sync.py --validate
python db/scripts/catalog_sync.py --report --output-dir db/reports
# Revisar e aplicar
```

### Cenário 3: Renomear Campo

⚠️ **Cuidado**: renomear requer migration manual!

```bash
# 1. Adicionar novo campo no YAML com novo nome
# 2. Gerar migration
# 3. Adicionar manualmente na migration:
#    ALTER TABLE tabela CHANGE COLUMN nome_antigo nome_novo TIPO;

# 4. Depois remover campo antigo do YAML em próxima sincronização
```

### Cenário 4: Deprecar Tabela

```yaml
  tabela_antiga:
    # ... definição ...
    status: "deprecated"  # ← Marcar como deprecated
    notes: |
      DEPRECATED em 2025-05-21.
      Use 'tabela_nova' em seu lugar.
      Será removida em 2025-12-31.
```

```bash
# Documentar em relatório
python db/scripts/catalog_sync.py --report

# BD continua funcionando, mas fica documentado
```

---

## 4️⃣ INTEGRAÇÕES

### Integração com Git (CI/CD)

```bash
# Criar arquivo: .github/workflows/validate-catalog.yml

name: Validate Catalog

on:
  pull_request:
    paths:
      - 'db/catalog/**'
      - 'db/scripts/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r db/scripts/requirements.txt
      
      - name: Validate catalog
        run: |
          python db/scripts/catalog_sync.py \
            --catalog db/catalog/tables.yaml \
            --validate
```

```bash
# Commit e push para testar
git add db/catalog/tables.yaml
git commit -m "feat: adicionar tabela de análise"
git push origin feature/nova-tabela
# GitHub Actions vai validar automaticamente
```

### Integração com Migration Tool (Alembic/Flyway)

```python
# alembic/env.py

from pathlib import Path
import yaml

def get_catalog_version():
    """Retorna versão do catálogo"""
    with open('db/catalog/tables.yaml') as f:
        return yaml.safe_load(f)['version']

# Usar na migration:
# migration_comment = f"Sync: v{get_catalog_version()}"
```

```sql
-- migrations/YYYYMMDD_HHMMSS_from_catalog_sync.sql
-- Gerado automaticamente
-- Versão do catálogo: 1.0.0
-- Data: 2025-05-21

CREATE TABLE nova_tabela (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    ...
);
```

### Integração com Documentação Auto-gerada

```python
# db/scripts/generate_documentation.py

import yaml
from pathlib import Path

def generate_docs():
    """Gera documentação markdown do catálogo"""
    with open('db/catalog/tables.yaml') as f:
        catalog = yaml.safe_load(f)
    
    doc = f"# Dicionário de Dados\n\n"
    doc += f"*Versão: {catalog['version']}*\n"
    doc += f"*Atualizado: {catalog['last_updated']}*\n\n"
    
    for table_name, table_def in catalog['tables'].items():
        doc += f"## {table_name}\n"
        doc += f"{table_def['description']}\n\n"
        
        doc += "### Colunas\n\n"
        doc += "| Nome | Tipo | Nullable | Descrição |\n"
        doc += "|------|------|----------|----------|\n"
        
        for col in table_def['columns']:
            doc += f"| {col['name']} | {col['type']} | "
            doc += f"{'Sim' if col.get('nullable', True) else 'Não'} | "
            doc += f"{col.get('description', '')} |\n"
        
        doc += "\n"
    
    Path('docs/data_dictionary.md').write_text(doc)
    print("✅ Documentação gerada em docs/data_dictionary.md")

if __name__ == '__main__':
    generate_docs()
```

```bash
# Executar antes de gerar docs
python db/scripts/generate_documentation.py
```

---

## 5️⃣ TROUBLESHOOTING

### Problema: "Catálogo inválido - Versão não definida"

```yaml
# Certifique-se de ter no início do tables.yaml:
version: "1.0.0"
last_updated: "2025-05-21"
database: "world_data_lab"
```

### Problema: "Tabela no BD mas não no catálogo"

```bash
# Opção 1: Adicionar ao catálogo
# Editar tables.yaml e adicionar tabela faltante

# Opção 2: Remover do BD (se não for usada)
# mysql -u root -p -e "DROP TABLE tabela_indesejada;"

# Opção 3: Marcar como não gerenciada
# Adicionar comentário no YAML
```

### Problema: "Migration contém erros SQL"

```bash
# 1. Revisar arquivo gerado
cat db/migrations/*auto_migration.sql

# 2. Editar manualmente se necessário
vim db/migrations/YYYYMMDD_HHMMSS_auto_migration.sql

# 3. Testar em BD de teste primeiro
mysql -u root -p test_world_data_lab < db/migrations/auto_migration.sql

# 4. Se OK, aplicar em produção
mysql -u root -p world_data_lab < db/migrations/auto_migration.sql
```

---

## 6️⃣ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Estrutura de diretórios criada
- [ ] Arquivo `tables.yaml` preenchido com suas tabelas
- [ ] Scripts Python instalados e testados
- [ ] Primeira validação executada com sucesso
- [ ] BD sincronizado (via migration ou manual)
- [ ] Relatório inicial gerado
- [ ] Git configurado para rastrear mudanças
- [ ] CI/CD configurado para validação automática
- [ ] Documentação atualizada
- [ ] Equipe treinada no processo

---

## 7️⃣ BOAS PRÁTICAS

✅ **FAÇA:**
- Sempre validar antes de sincronizar
- Fazer backup antes de grandes mudanças
- Documentar decisões em `notes` do YAML
- Revisar migrations geradas antes de aplicar
- Versionar todas as mudanças no Git
- Testar em BD de teste primeiro

❌ **NÃO FAÇA:**
- Modificar BD diretamente sem atualizar catálogo
- Aplicar migrations sem revisar
- Deixar campos sem descrição
- Remover tabelas do YAML sem certificação
- Usar nomes de colunas inconsistentes
- Esquecer de fazer backup

---

## 📞 SUPORTE

Se tiver problemas:

1. Verificar logs da validação
2. Consultar relatório de sincronização
3. Revisar exemplo de YAML fornecido
4. Testar em banco de teste isolado
5. Fazer backup antes de mudar estrutura

---

## 🎓 PRÓXIMOS PASSOS

1. **Implementar versionamento de dados**: rastrear histórico de schema
2. **Dashboard de monitoramento**: visualizar estado do catálogo
3. **Webhooks**: notificar equipe de mudanças
4. **Lineage automático**: mapear dependências entre tabelas
5. **Testes de integridade**: validar dados após migrations

---

**Versão**: 1.0.0  
**Última atualização**: 2025-05-21  
**Autor**: Seu Time de Dados
