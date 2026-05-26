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
print(f"\n✓ Python {sys.version}")

# STEP 2: Verificar dependências
print("\nVerificando dependências...")
required_packages = ['flask', 'flask_cors', 'flask_sqlalchemy', 'flask_jwt_extended', 'flask_bcrypt']
missing = []

for package in required_packages:
    try:
        __import__(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - NÃO INSTALADO")
        missing.append(package)

if missing:
    print(f"\n⚠️  ERRO: Pacotes faltando: {', '.join(missing)}")
    print("\nExecute: pip install -r requirements.txt")
    sys.exit(1)

# STEP 3: Tentar importar o app
print("\nCarregando aplicação...")
try:
    from app import create_app
    print("  ✓ app.py carregado")
except Exception as e:
    print(f"  ✗ Erro ao carregar app.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# STEP 4: Criar a app
print("\nCriando aplicação Flask...")
try:
    app = create_app()
    print("  ✓ Aplicação criada com sucesso")
except Exception as e:
    print(f"  ✗ Erro ao criar aplicação: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# STEP 5: Verificar configurações
print("\nVerificando configurações...")
print(f"  ✓ Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')}")
print(f"  ✓ Debug: {app.debug}")

# STEP 6: Pronto para rodar
print("\n" + "=" * 60)
print("  ✓ SUCESSO! Aplicação pronta para rodar")
print("=" * 60)
print("\nIniciando servidor em http://0.0.0.0:5000 ...")
print("Pressione CTRL+C para parar.\n")

try:
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
except KeyboardInterrupt:
    print("\n\nServidor interrompido.")
    sys.exit(0)
