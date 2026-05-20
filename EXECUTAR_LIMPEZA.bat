@echo off
chcp 65001 >nul
title Limpeza Backend MedSystem

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           LIMPEZA DO BACKEND FLASK - MEDSYSTEM                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

setlocal enabledelayedexpansion

set count=0

REM Remove arquivos de documentação
for %%f in (
    "CORRECOES_REALIZADAS.md"
    "ERRO_COLUNA_BANCO_DADOS.md"
    "EXECUTE_AGORA.txt"
    "FIX_BANCO.txt"
    "GUIA_PAGINA_BRANCA.md"
    "LEIA_PRIMEIRO.txt"
    "MEDSYSTEM_SUMMARY.html"
    "MEDSYSTEM_SUMMARY.md"
    "MEDSYSTEM_SUMMARY.pdf"
    "NOVO V3.sql"
    "PRONTO.txt"
    "RESUMO_CORRECAO.md"
    "SOLUCAO_FINAL.txt"
    "SOLUCAO_INICIALIZACAO.md"
    "TESTE_AGORA.txt"
    "START_APP.bat"
    "copy_backend.bat"
    "reset_db.bat"
    "start_debug.bat"
    "copy_backend.py"
    "fix_and_run.py"
    "fix_id_registro.py"
    "hard_reset.py"
    "quick_test.py"
    "reset_database.py"
    "restart.py"
    "run_debug.py"
    "test_app_fix.py"
    "test_startup.py"
    "test_web.py"
    "setup.bat"
    "cleanup.py"
    "remover_arquivos.py"
    "limpar.bat"
) do (
    if exist %%f (
        del /f /q %%f >nul 2>&1
        set /a count+=1
        echo [✓] Removido: %%f
    )
)

REM Remove __pycache__
if exist __pycache__ (
    rmdir /s /q __pycache__ >nul 2>&1
    set /a count+=1
    echo [✓] Removido: __pycache__
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  ✅ LIMPEZA CONCLUÍDA COM SUCESSO!                            ║
echo ║  Total de arquivos removidos: !count!                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Arquivos mantidos no projeto:
echo.
echo ✅ app.py                    - Aplicação principal
echo ✅ models.py                 - Modelos do banco
echo ✅ extensions.py             - Extensões Flask
echo ✅ requirements.txt          - Dependências
echo ✅ run_app.py                - Script de execução
echo ✅ routes/                   - Rotas da API
echo ✅ templates/                - Templates HTML
echo ✅ static/                   - Arquivos estáticos
echo ✅ instance/                 - Configuração Flask
echo ✅ venv/                     - Ambiente virtual
echo.

echo.
pause
