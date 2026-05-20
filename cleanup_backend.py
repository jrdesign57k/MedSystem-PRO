#!/usr/bin/env python3
"""
Script para limpeza do backend Flask
Execute: python cleanup_backend.py
"""
import os
import shutil
import sys

def cleanup():
    """Remove arquivos e pastas desnecessárias"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    files_to_remove = [
        # Documentação/Correções
        'CORRECOES_REALIZADAS.md',
        'ERRO_COLUNA_BANCO_DADOS.md',
        'GUIA_PAGINA_BRANCA.md',
        'LEIA_PRIMEIRO.txt',
        'RESUMO_CORRECAO.md',
        'SOLUCAO_FINAL.txt',
        'SOLUCAO_INICIALIZACAO.md',
        
        # Sumários e PDFs
        'MEDSYSTEM_SUMMARY.html',
        'MEDSYSTEM_SUMMARY.md',
        'MEDSYSTEM_SUMMARY.pdf',
        
        # Instruções soltas
        'EXECUTE_AGORA.txt',
        'FIX_BANCO.txt',
        'PRONTO.txt',
        'TESTE_AGORA.txt',
        
        # SQL antigos
        'NOVO V3.sql',
        
        # Scripts .bat
        'START_APP.bat',
        'copy_backend.bat',
        'reset_db.bat',
        'start_debug.bat',
        'setup.bat',
        
        # Scripts Python desnecessários
        'copy_backend.py',
        'fix_and_run.py',
        'fix_id_registro.py',
        'hard_reset.py',
        'quick_test.py',
        'reset_database.py',
        'restart.py',
        'run_debug.py',
        'test_app_fix.py',
        'test_startup.py',
        'test_web.py',
        'solucao_simples.py',
        'cleanup.py',
        'remover_arquivos.py',
        'limpar.bat',
    ]
    
    removed = []
    errors = []
    
    print("=" * 60)
    print("LIMPEZA DO BACKEND FLASK")
    print("=" * 60)
    print()
    
    # Remover arquivos
    for file in files_to_remove:
        try:
            if os.path.exists(file):
                os.remove(file)
                removed.append(file)
                print(f"✓ Removido: {file}")
        except Exception as e:
            errors.append((file, str(e)))
            print(f"✗ Erro: {file} - {e}")
    
    # Remover __pycache__
    if os.path.exists('__pycache__'):
        try:
            shutil.rmtree('__pycache__')
            removed.append('__pycache__')
            print(f"✓ Removido: __pycache__/")
        except Exception as e:
            errors.append(('__pycache__', str(e)))
            print(f"✗ Erro: __pycache__ - {e}")
    
    # Relatório final
    print()
    print("=" * 60)
    print(f"RESUMO: {len(removed)} arquivos removidos")
    if errors:
        print(f"ERROS: {len(errors)} problemas encontrados")
    print("=" * 60)
    print()
    print("✅ Limpeza concluída com sucesso!")
    print()
    print("Arquivos mantidos no projeto:")
    print("  - app.py (aplicação principal)")
    print("  - models.py (modelos do banco)")
    print("  - extensions.py (extensões Flask)")
    print("  - requirements.txt (dependências)")
    print("  - run_app.py (script principal de execução)")
    print("  - routes/ (rotas da API)")
    print("  - templates/ (templates HTML)")
    print("  - static/ (arquivos estáticos)")
    print("  - instance/ (configuração Flask)")
    print("  - venv/ (ambiente virtual)")

if __name__ == '__main__':
    try:
        cleanup()
    except KeyboardInterrupt:
        print("\n\n❌ Limpeza cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
