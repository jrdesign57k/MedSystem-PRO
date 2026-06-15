#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para diagnosticar e corrigir erros de inicialização do MedSystem
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  DIAGNÓSTICO E INICIALIZAÇÃO - MEDSYSTEM")
print("=" * 60)

# STEP 1: Verificar Python version
print(f"\n[OK] Python {sys.version.split()[0]}")

# STEP 2: Verificar dependências
print("\nVerificando dependências...")
required_packages = ['flask', 'flask_cors', 'flask_sqlalchemy', 'flask_jwt_extended', 'flask_bcrypt']
missing = []

for package in required_packages:
    try:
        __import__(package)
        print(f"  [OK] {package}")
    except ImportError:
        print(f"  [X] {package} - NAO INSTALADO")
        missing.append(package)

if missing:
    print(f"\n[!] ERRO: Pacotes faltando: {', '.join(missing)}")
    print("\nExecute: pip install -r requirements.txt")
    sys.exit(1)

# STEP 3: Tentar importar o app
print("\nCarregando aplicação...")
try:
    from app import create_app
    print("  [OK] app.py carregado")
except Exception as e:
    print(f"  [X] Erro ao carregar app.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# STEP 4: Criar a app
print("\nCriando aplicação Flask...")
try:
    app = create_app()
    print("  [OK] Aplicacao criada com sucesso")
except Exception as e:
    print(f"  [X] Erro ao criar aplicacao: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# STEP 5: Verificar configurações
print("\nVerificando configurações...")
print(f"  [OK] Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')}")
print(f"  [OK] Debug: {app.debug}")

# STEP 6: Pronto para rodar
print("\n" + "=" * 60)
print("  [OK] SUCESSO! Aplicacao pronta para rodar")
print("=" * 60)
print("\nIniciando servidor em http://0.0.0.0:5000 ...")
print("Pressione CTRL+C para parar.\n")

try:
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
except KeyboardInterrupt:
    print("\n\nServidor interrompido.")
    sys.exit(0)
