import os
import shutil

os.chdir(r'c:\Users\Meu PC\Downloads\novo00')

arquivos = [
    'CORRECOES_REALIZADAS.md',
    'ERRO_COLUNA_BANCO_DADOS.md',
    'EXECUTE_AGORA.txt',
    'FIX_BANCO.txt',
    'GUIA_PAGINA_BRANCA.md',
    'LEIA_PRIMEIRO.txt',
    'MEDSYSTEM_SUMMARY.html',
    'MEDSYSTEM_SUMMARY.md',
    'MEDSYSTEM_SUMMARY.pdf',
    'NOVO V3.sql',
    'PRONTO.txt',
    'RESUMO_CORRECAO.md',
    'SOLUCAO_FINAL.txt',
    'SOLUCAO_INICIALIZACAO.md',
    'TESTE_AGORA.txt',
    'START_APP.bat',
    'copy_backend.bat',
    'reset_db.bat',
    'start_debug.bat',
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
    'setup.bat',
    'cleanup.py',
    'remover_arquivos.py',
    'limpar.bat'
]

count = 0
for arquivo in arquivos:
    try:
        if os.path.exists(arquivo):
            os.remove(arquivo)
            count += 1
    except Exception as e:
        pass

if os.path.exists('__pycache__'):
    try:
        shutil.rmtree('__pycache__')
        count += 1
    except:
        pass

print(f'Limpeza concluída! {count} arquivos removidos.')
