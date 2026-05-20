# 🧹 LIMPEZA DO BACKEND

## Como usar

Abra o terminal na pasta do projeto e execute:

```bash
python cleanup_backend.py
```

## O que será removido

### 📝 Documentação desnecessária
- CORRECOES_REALIZADAS.md
- ERRO_COLUNA_BANCO_DADOS.md
- GUIA_PAGINA_BRANCA.md
- LEIA_PRIMEIRO.txt
- RESUMO_CORRECAO.md
- SOLUCAO_FINAL.txt
- SOLUCAO_INICIALIZACAO.md

### 📊 Sumários e relatórios
- MEDSYSTEM_SUMMARY.html
- MEDSYSTEM_SUMMARY.md
- MEDSYSTEM_SUMMARY.pdf

### ⚠️ Instruções soltas
- EXECUTE_AGORA.txt
- FIX_BANCO.txt
- PRONTO.txt
- TESTE_AGORA.txt

### 🐍 Scripts desorganizados
- copy_backend.py
- fix_and_run.py
- fix_id_registro.py
- hard_reset.py
- quick_test.py
- reset_database.py
- restart.py
- run_debug.py
- test_app_fix.py
- test_startup.py
- test_web.py
- solucao_simples.py

### 🔧 Arquivos .bat (Windows)
- START_APP.bat
- copy_backend.bat
- reset_db.bat
- start_debug.bat
- setup.bat

### 📦 Cache Python
- __pycache__/

### 🗂️ Arquivos SQL desorganizados
- NOVO V3.sql

## O que será mantido (Essencial)

✅ **app.py** - Aplicação principal Flask
✅ **models.py** - Modelos do banco de dados
✅ **extensions.py** - Extensões Flask
✅ **requirements.txt** - Dependências do projeto
✅ **run_app.py** - Script para executar a aplicação
✅ **routes/** - Rotas da API
✅ **templates/** - Templates HTML
✅ **static/** - Arquivos estáticos (CSS, JS, etc)
✅ **instance/** - Pasta de configuração Flask
✅ **venv/** - Ambiente virtual Python

## Estrutura após limpeza

```
seu-projeto/
├── app.py                 # Aplicação principal
├── models.py              # Modelos
├── extensions.py          # Extensões
├── run_app.py             # Script de execução
├── requirements.txt       # Dependências
├── routes/                # Rotas da API
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos
├── instance/              # Configuração
├── venv/                  # Ambiente virtual
└── cleanup_backend.py     # Este script
```

## Próximos passos

Após a limpeza:

1. **Verifique se a app funciona:**
   ```bash
   python run_app.py
   ```

2. **Crie um .gitignore** para ignorar arquivos temporários:
   ```
   __pycache__/
   *.pyc
   .env
   venv/
   instance/
   ```

3. **Commit suas mudanças:**
   ```bash
   git add .
   git commit -m "Limpeza: Remover arquivos desnecessários"
   ```

---
**Nota:** Este script é seguro e só remove arquivos que você não precisa.
