# -*- coding: utf-8 -*-
"""
Importador do banco MedSystem.

Recria o banco a partir de medsystem/database/medsystem_banco.sql,
executando DDL, procedures (DELIMITER), triggers, views e seed.

Uso:
    python import_database.py            # recria o banco (DROP + CREATE)
    python import_database.py --keep     # nao dropa, apenas aplica o script

Apos importar, rode a aplicacao (run_app.py) — o startup cria os
usuarios de login (medico@medsystem.com / MedSystem12#).
"""
import os
import sys
import mysql.connector
from dotenv import load_dotenv

BASE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE, '.env'), override=True)

SQL_PATH = os.path.join(BASE, 'medsystem', 'database', 'medsystem_banco.sql')

DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME', 'medsystem')

SKIP_KEYWORDS = ('CREATE USER', 'GRANT ', 'FLUSH PRIVILEGES', 'DROP USER')


def split_statements(sql):
    """Divide o script em statements respeitando blocos DELIMITER."""
    statements = []
    delimiter = ';'
    buffer = ''
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith('DELIMITER'):
            if buffer.strip():
                statements.append(buffer.strip())
                buffer = ''
            delimiter = stripped.split()[1]
            continue
        buffer += line + '\n'
        if buffer.rstrip().endswith(delimiter):
            stmt = buffer.rstrip()[:-len(delimiter)].strip()
            if stmt:
                statements.append(stmt)
            buffer = ''
    if buffer.strip():
        statements.append(buffer.strip())
    return statements


def main():
    keep = '--keep' in sys.argv
    if not os.path.exists(SQL_PATH):
        print(f'[ERRO] SQL nao encontrado: {SQL_PATH}')
        sys.exit(1)

    sql = open(SQL_PATH, encoding='utf-8').read()

    cnx = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
    cur = cnx.cursor()

    if not keep:
        print(f'[1] Dropando e recriando o banco `{DB_NAME}`...')
        cur.execute(f'DROP DATABASE IF EXISTS `{DB_NAME}`')
        cnx.commit()

    statements = split_statements(sql)
    print(f'[2] Executando {len(statements)} statements...')

    ok, skip, err = 0, 0, 0
    for stmt in statements:
        upper = stmt.upper()
        if any(k in upper for k in SKIP_KEYWORDS):
            skip += 1
            continue
        try:
            cur.execute(stmt)
            # consome resultados se houver
            try:
                cur.fetchall()
            except Exception:
                pass
            cnx.commit()
            ok += 1
        except mysql.connector.Error as e:
            err += 1
            head = ' '.join(stmt.split())[:70]
            print(f'   [erro] {e.msg}  ::  {head}...')

    cur.close()
    cnx.close()
    print(f'\n[OK] Executados: {ok} | Pulados (permissoes): {skip} | Erros: {err}')
    print('Proximo passo: inicie a aplicacao para criar os usuarios de login.')


if __name__ == '__main__':
    main()
