#!/usr/bin/env python
"""
SOLUÇÃO SIMPLES - Remove id_registro e recria banco
"""
import os, sys, shutil, re, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("  SOLUÇÃO FINAL - Limpeza Completa")
print("="*70 + "\n")

# 1. Remove id_registro de TODAS as rotas
print("1. Limpando código Python...")
routes_dir = 'routes'
for filename in os.listdir(routes_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(routes_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove id_registro=X,
        new_content = re.sub(r',?\s*id_registro\s*=\s*[^,\)]+', '', content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"   ✓ {filename}")

# 2. Deletar banco
print("\n2. Deletando banco antigo...")
if os.path.exists('instance'):
    try:
        shutil.rmtree('instance')
        print("   ✓ Banco deletado")
    except:
        print("   (não foi possível deletar, mas vai ser recriado)")

# 3. Limpar cache
print("\n3. Limpando cache...")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in dirs:
        try:
            shutil.rmtree(os.path.join(root, '__pycache__'))
        except:
            pass

print("   ✓ Cache limpo")

# 4. Recriar banco
print("\n4. Recriando banco e inicializando...")
time.sleep(1)
try:
    from app import create_app
    app = create_app()
    print("   ✓ Banco criado\n")
except Exception as e:
    print(f"   ✗ Erro: {e}\n")
    sys.exit(1)

print("="*70)
print("  ✓ SUCESSO - Sistema pronto!")
print("="*70)
print("\n📖 Login:")
print("   Email: recep@medsystem.com")
print("   Senha: 123456\n")
print("🚀 Para iniciar servidor:")
print("   python run_debug.py\n")
