from app import create_app
from extensions import db
from models import Especialidade

# Cria a instância do app usando a sua factory
app = create_app()

with app.app_context():
    # Lista com as IDs exatas que o seu Javascript (Frontend) usa
    especialidades_iniciais = [
        (1, "Clínica Geral"),
        (2, "Cardiologia"),
        (3, "Neurologia"),
        (4, "Pediatria"),
        (5, "Oftalmologia")
    ]
    
    adicionadas = 0
    for id_esp, nome in especialidades_iniciais:
        # Verifica se a especialidade já existe
        existe = Especialidade.query.get(id_esp)
        if not existe:
            nova_esp = Especialidade(id=id_esp, nome=nome)
            db.session.add(nova_esp)
            adicionadas += 1
            
    db.session.commit()
    print(f"✅ {adicionadas} especialidades foram inseridas no banco de dados!")