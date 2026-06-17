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
    'prescricoes': [
        ('dosagem', 'VARCHAR(100) NULL'),
        ('posologia', 'TEXT NULL'),
        ('frequencia', 'VARCHAR(100) NULL'),
        ('duracao', 'VARCHAR(100) NULL'),
        ('quantidade', 'INT NULL'),
        ('tipo_receita', 'VARCHAR(50) NULL'),
        ('orientacoes', 'TEXT NULL'),
        ('data_prescricao', 'DATETIME NULL DEFAULT CURRENT_TIMESTAMP'),
        ('status', "VARCHAR(20) NULL DEFAULT 'ATIVA'"),
    ],
    'diagnosticos': [
        ('id_paciente', 'INT NULL'),
        ('id_medico', 'INT NULL'),
        ('status', "VARCHAR(20) NULL DEFAULT 'ATIVO'"),
        ('data_diagnostico', 'DATETIME NULL DEFAULT CURRENT_TIMESTAMP'),
    ],
    'paciente': [
        ('data_cadastro', 'DATETIME NULL DEFAULT CURRENT_TIMESTAMP'),
        ('ativo', 'TINYINT(1) NOT NULL DEFAULT 1'),
    ],
    'exames': [
        ('id_paciente', 'INT NULL'),
        ('id_medico', 'INT NULL'),
        ('nome_exame', 'VARCHAR(200) NULL'),
        ('laudo', 'TEXT NULL'),
        ('prioridade', "VARCHAR(20) NULL DEFAULT 'NORMAL'"),
        ('data_solicitacao', 'DATETIME NULL DEFAULT CURRENT_TIMESTAMP'),
        ('data_resultado', 'DATETIME NULL'),
    ],
}

# Colunas cujo TIPO precisa ser ajustado quando o banco foi criado com ENUMs
# restritivos (ex.: gravidade sem 'CRITICA'). (coluna, tipo_desejado)
MODIFICACOES = {
    'diagnosticos': [
        ('gravidade', 'VARCHAR(20) NULL'),
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
            print(f'[OK] Migracao: coluna {tabela}.{coluna} adicionada')
            alterou = True

    return alterou


def _ajustar_tipos(tabela, colunas, insp):
    """Converte ENUMs antigos para o tipo desejado (idempotente)."""
    if tabela not in insp.get_table_names():
        return False

    alterou = False
    for coluna, tipo_desejado in colunas:
        try:
            atual = db.session.execute(text(
                "SELECT COLUMN_TYPE FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
            ), {'t': tabela, 'c': coluna}).scalar()
        except Exception:
            atual = None

        if not atual:
            continue

        atual_norm = atual.lower().replace(' ', '')
        # Só altera se o tipo atual difere do desejado (ex.: ainda é enum)
        if atual_norm != tipo_desejado.split()[0].lower():
            db.session.execute(text(f'ALTER TABLE {tabela} MODIFY {coluna} {tipo_desejado}'))
            print(f'[OK] Migracao: coluna {tabela}.{coluna} convertida de {atual} para {tipo_desejado}')
            alterou = True

    return alterou


def _backfill_referencias():
    """Preenche FKs a partir de consulta quando colunas foram adicionadas depois."""
    backfills = [
        """
        UPDATE diagnosticos d
        INNER JOIN consulta c ON d.id_consulta = c.id_consulta
        SET d.id_paciente = c.id_paciente, d.id_medico = c.id_medico
        WHERE d.id_paciente IS NULL OR d.id_medico IS NULL
        """,
        """
        UPDATE exames e
        INNER JOIN consulta c ON e.id_consulta = c.id_consulta
        SET e.id_paciente = c.id_paciente, e.id_medico = c.id_medico
        WHERE e.id_paciente IS NULL OR e.id_medico IS NULL
        """,
    ]
    for sql in backfills:
        try:
            db.session.execute(text(sql))
        except Exception:
            pass


def upgrade_schema():
    """Adiciona colunas faltantes sem apagar dados existentes."""
    insp = inspect(db.engine)
    alterou = False

    for tabela, colunas in MIGRACOES.items():
        if _adicionar_colunas(tabela, colunas, insp):
            alterou = True

    for tabela, colunas in MODIFICACOES.items():
        if _ajustar_tipos(tabela, colunas, insp):
            alterou = True

    _backfill_referencias()

    if alterou:
        db.session.commit()
