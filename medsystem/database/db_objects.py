"""
Aplica os objetos de banco (views, procedures com transacao e triggers de auditoria)
definidos em migrations/004_objetos_banco.sql.

Executa cada statement individualmente (separados pela sentinela "-- @@SPLIT@@")
usando a conexao bruta do driver, para suportar CREATE PROCEDURE/TRIGGER sem DELIMITER.
Cada objeto e aplicado com try/except: se um falhar (ex.: restricao do RDS), os demais
continuam e a aplicacao nao quebra.
"""
import os
from extensions import db

SENTINELA = '-- @@SPLIT@@'
_ARQUIVO = os.path.join(os.path.dirname(__file__), 'migrations', '004_objetos_banco.sql')


def _carregar_statements():
    if not os.path.exists(_ARQUIVO):
        return []
    with open(_ARQUIVO, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    blocos = conteudo.split(SENTINELA)
    statements = []
    for bloco in blocos:
        # Remove linhas de comentario puro e espacos
        linhas = [ln for ln in bloco.splitlines() if not ln.strip().startswith('--')]
        stmt = '\n'.join(linhas).strip().rstrip(';').strip()
        if stmt:
            statements.append(stmt)
    return statements


def aplicar_objetos_banco():
    """Cria/atualiza views, procedures e triggers. Idempotente e resiliente."""
    statements = _carregar_statements()
    if not statements:
        return

    raw = db.engine.raw_connection()
    ok, falhas = 0, 0
    try:
        cursor = raw.cursor()
        for stmt in statements:
            try:
                cursor.execute(stmt)
                # Consome eventuais resultados para nao travar a conexao
                try:
                    cursor.fetchall()
                except Exception:
                    pass
                ok += 1
            except Exception as e:
                falhas += 1
                rotulo = stmt.split('\n', 1)[0][:60]
                print(f'[db_objects] Falha ao aplicar: {rotulo}... -> {e}')
        raw.commit()
        cursor.close()
    finally:
        raw.close()

    print(f'✓ Objetos de banco aplicados (ok={ok}, falhas={falhas})')
