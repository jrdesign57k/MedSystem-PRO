"""Atualiza tabelas existentes quando o banco foi criado com schema antigo."""
from sqlalchemy import inspect, text
from extensions import db

# (coluna, definição SQL)
MIGRACOES = {
    'consulta': [
        ('hora_consulta', 'CHAR(5) NULL'),
        ('queixa_principal', 'TEXT NULL'),
        ('historia_molestia_atual', 'TEXT NULL'),
        ('antecedentes_pessoais', 'TEXT NULL'),
        ('antecedentes_familiares', 'TEXT NULL'),
        ('exame_fisico', 'TEXT NULL'),
        ('hipotese_diagnostica', 'TEXT NULL'),
        ('plano_terapeutico', 'TEXT NULL'),
        ('observacoes_consulta', 'TEXT NULL'),
        ('tipo_consulta', 'VARCHAR(50) NULL'),
        ('convenio', 'VARCHAR(100) NULL'),
    ],
    'receitas': [
        ('convenio', 'VARCHAR(100) NULL'),
    ],
}


def _adicionar_colunas(tabela, colunas, insp):
    if tabela not in insp.get_table_names():
        return False

    existentes = {c['name'] for c in insp.get_columns(tabela)}
    alterou = False

    for coluna, definicao in colunas:
        if coluna not in existentes:
            db.session.execute(text(f'ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}'))
            print(f'✓ Migração: coluna {tabela}.{coluna} adicionada')
            alterou = True

    return alterou


def upgrade_schema():
    """Adiciona colunas faltantes sem apagar dados existentes."""
    insp = inspect(db.engine)
    alterou = False

    for tabela, colunas in MIGRACOES.items():
        if _adicionar_colunas(tabela, colunas, insp):
            alterou = True

    if alterou:
        db.session.commit()
