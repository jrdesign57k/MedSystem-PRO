#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar migração de adicionar coluna 'hora_consulta' à tabela 'consulta'
"""
import mysql.connector
import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

print("=" * 60)
print("  MIGRAÇÃO - ADICIONAR COLUNA 'hora_consulta' À TABELA")
print("=" * 60)

def adicionar_colunas():
    try:
        print("\nConectando ao banco de dados...")
        conexao = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'medsystem')
        )
        
        print("✓ Conectado com sucesso")
        cursor = conexao.cursor()
        
        # ──────────────────────────────────────────────────────────
        # 1. VERIFICAR E ADICIONAR COLUNA 'motivo'
        # ──────────────────────────────────────────────────────────
        print("\n1. Verificando coluna 'motivo'...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'consulta' AND COLUMN_NAME = 'motivo'
        """)
        
        if not cursor.fetchone():
            print("   → Adicionando coluna 'motivo'...")
            cursor.execute("""
                ALTER TABLE consulta 
                ADD COLUMN motivo VARCHAR(255) NULL
            """)
            conexao.commit()
            print("   ✓ Coluna 'motivo' adicionada com sucesso")
        else:
            print("   ✓ Coluna 'motivo' já existe")
        
        # ──────────────────────────────────────────────────────────
        # 2. VERIFICAR E ADICIONAR COLUNA 'hora_consulta'
        # ──────────────────────────────────────────────────────────
        print("\n2. Verificando coluna 'hora_consulta'...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'consulta' AND COLUMN_NAME = 'hora_consulta'
        """)
        
        if not cursor.fetchone():
            print("   → Adicionando coluna 'hora_consulta'...")
            cursor.execute("""
                ALTER TABLE consulta 
                ADD COLUMN hora_consulta VARCHAR(5) NULL
            """)
            conexao.commit()
            print("   ✓ Coluna 'hora_consulta' adicionada com sucesso")
        else:
            print("   ✓ Coluna 'hora_consulta' já existe")
        
        cursor.close()
        conexao.close()
        
        print("\n" + "=" * 60)
        print("  ✓ TODAS AS MIGRAÇÕES FORAM EXECUTADAS COM SUCESSO!")
        print("=" * 60)
        print("\n✓ Agora você pode agendar consultas com horário!")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao executar migração: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = adicionar_colunas()
    sys.exit(0 if sucesso else 1)
