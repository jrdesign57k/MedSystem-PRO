#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste rápido do Dashboard MedSystem
Verifica se os endpoints estão funcionando corretamente
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Usuario, Medico, Especialidade, Paciente, Consulta, Diagnostico
from datetime import datetime, timedelta
import json

print("=" * 70)
print("  TESTE DO DASHBOARD - MEDSYSTEM")
print("=" * 70)

# Criar app
print("\n[1/5] Criando aplicação...")
app = create_app()

with app.app_context():
    print("✓ Aplicação criada")
    
    # Verificar dados
    print("\n[2/5] Verificando dados no banco...")
    
    usuarios = Usuario.query.count()
    pacientes = Paciente.query.count()
    consultas = Consulta.query.count()
    diagnosticos = Diagnostico.query.count()
    
    print(f"  • Usuários: {usuarios}")
    print(f"  • Pacientes: {pacientes}")
    print(f"  • Consultas: {consultas}")
    print(f"  • Diagnósticos: {diagnosticos}")
    
    # Testar endpoints internamente
    print("\n[3/5] Testando endpoints...")
    
    # GET do dashboard/metricas
    print("\n  ✓ Testando /api/dashboard/metricas")
    from routes.additional import dashboard_bp
    
    # Test client
    client = app.test_client()
    
    # Primeiro, fazer login
    print("\n[4/5] Obtendo token JWT...")
    
    # Tentar fazer login com admin
    response = client.post('/api/auth/login', json={
        'email': 'medico@medsystem.com',
        'senha': 'MedSystem12#'
    })
    
    if response.status_code == 200:
        token_data = response.get_json()
        token = token_data.get('token')
        print(f"  ✓ Token obtido: {token[:20]}...")
        
        # Testar endpoints com token
        print("\n[5/5] Testando endpoints do dashboard...")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Métricas
        resp = client.get('/api/dashboard/metricas', headers=headers)
        if resp.status_code == 200:
            print("  ✓ /api/dashboard/metricas: OK")
        else:
            print(f"  ✗ /api/dashboard/metricas: {resp.status_code}")
        
        # Próximas consultas
        resp = client.get('/api/dashboard/proximas-consultas', headers=headers)
        if resp.status_code == 200:
            print("  ✓ /api/dashboard/proximas-consultas: OK")
        else:
            print(f"  ✗ /api/dashboard/proximas-consultas: {resp.status_code}")
        
        # Alertas
        resp = client.get('/api/dashboard/alertas', headers=headers)
        if resp.status_code == 200:
            print("  ✓ /api/dashboard/alertas: OK")
        else:
            print(f"  ✗ /api/dashboard/alertas: {resp.status_code}")
        
        # Gráfico atendimentos
        resp = client.get('/api/dashboard/grafico/atendimentos', headers=headers)
        if resp.status_code == 200:
            data = resp.get_json()
            if data.get('sucesso'):
                print("  ✓ /api/dashboard/grafico/atendimentos: OK")
            else:
                print(f"  ✗ /api/dashboard/grafico/atendimentos: {data.get('mensagem')}")
        else:
            print(f"  ✗ /api/dashboard/grafico/atendimentos: {resp.status_code}")
        
        # Gráfico risco
        resp = client.get('/api/dashboard/grafico/classificacao-risco', headers=headers)
        if resp.status_code == 200:
            data = resp.get_json()
            if data.get('sucesso'):
                print("  ✓ /api/dashboard/grafico/classificacao-risco: OK")
            else:
                print(f"  ✗ /api/dashboard/grafico/classificacao-risco: {data.get('mensagem')}")
        else:
            print(f"  ✗ /api/dashboard/grafico/classificacao-risco: {resp.status_code}")
        
        # Dashboard HTML
        resp = client.get('/dashboard')
        if resp.status_code == 200:
            print("  ✓ /dashboard (HTML): OK")
        else:
            print(f"  ✗ /dashboard (HTML): {resp.status_code}")
            
    else:
        print(f"  ✗ Erro ao fazer login: {response.status_code}")
        print(f"    {response.get_json()}")

print("\n" + "=" * 70)
print("  ✓ TESTE CONCLUÍDO!")
print("=" * 70)
print("\n📊 Dashboard está pronto em: http://localhost:5000/dashboard")
print("   Acesse com token JWT no localStorage (chave: 'token')")
print("\n")
