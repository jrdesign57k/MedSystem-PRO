#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar migração de adicionar coluna 'motivo' à tabela 'consulta'
"""
import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  MIGRAÇÃO - ADICIONAR COLUNA 'motivo' À TABELA 'consulta'")
print("=" * 60)

try:
    print("\nCarregando aplicação...")
    from app import create_app
    from extensions import db
    from sqlalchemy import text
    
    app = create_app()
    
    with app.app_context():
        print("✓ Aplicação carregada")
        print("\nExecutando migração...")
        
        try:
            with db.engine.connect() as conn:
                # Verifica se a coluna 'motivo' existe
                result = conn.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'consulta' AND COLUMN_NAME = 'motivo'
                """))
                
                if result.fetchone():
                    print("✓ Coluna 'motivo' já existe na tabela 'consulta'")
                else:
                    # Adiciona a coluna se não existir
                    conn.execute(text("ALTER TABLE consulta ADD COLUMN motivo VARCHAR(255) NULL"))
                    conn.commit()
                    print("✓ Coluna 'motivo' adicionada com sucesso à tabela 'consulta'")
        
        except Exception as e:
            print(f"✗ Erro ao executar migração: {str(e)}")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("  ✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 60)
        print("\nAgora você pode agendar consultas sem erros!")
        
except Exception as e:
    print(f"\n✗ Erro: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
