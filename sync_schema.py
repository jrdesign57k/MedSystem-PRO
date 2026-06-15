# -*- coding: utf-8 -*-
"""
Sincronizador de schema do MedSystem.

Compara os models SQLAlchemy com o banco de dados real e adiciona,
via ALTER TABLE, as colunas que estiverem faltando (sem apagar dados).

Uso:
    python sync_schema.py
"""
import warnings
warnings.filterwarnings('ignore')

from sqlalchemy import inspect, text
from app import create_app
from extensions import db


def sincronizar():
    app = create_app()
    with app.app_context():
        insp = inspect(db.engine)
        dialect = db.engine.dialect
        db_tables = set(insp.get_table_names())
        alteracoes = 0

        for table_name, table in db.metadata.tables.items():
            if table_name not in db_tables:
                table.create(bind=db.engine, checkfirst=True)
                print(f'[CRIADA] tabela {table_name}')
                continue

            cols_db = {c['name'] for c in insp.get_columns(table_name)}
            for col in table.columns:
                if col.name in cols_db:
                    continue
                tipo = col.type.compile(dialect=dialect)
                ddl = f'ALTER TABLE `{table_name}` ADD COLUMN `{col.name}` {tipo} NULL'
                try:
                    db.session.execute(text(ddl))
                    db.session.commit()
                    print(f'[+] {table_name}.{col.name} ({tipo})')
                    alteracoes += 1
                except Exception as e:
                    db.session.rollback()
                    print(f'[ERRO] {table_name}.{col.name}: {e}')

        if alteracoes == 0:
            print('Schema ja esta sincronizado. Nada a fazer.')
        else:
            print(f'\nConcluido: {alteracoes} coluna(s) adicionada(s).')


if __name__ == '__main__':
    sincronizar()
