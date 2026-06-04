"""
Script para popular tabela CID-10 com dados iniciais
"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import CID10

def seed_cid10():
    """Popula a tabela CID-10 com diagnósticos comuns"""
    
    cid_data = [
        # Doenças cardiovasculares
        {'codigo': 'I10', 'descricao': 'Hipertensão Arterial Sistêmica', 'categoria': 'Cardiovascular'},
        {'codigo': 'I25', 'descricao': 'Doença isquêmica crônica do coração', 'categoria': 'Cardiovascular'},
        {'codigo': 'I63', 'descricao': 'Acidente vascular cerebral isquêmico', 'categoria': 'Cardiovascular'},
        
        # Infecções respiratórias
        {'codigo': 'J06.9', 'descricao': 'Infecção aguda VAS não especificada', 'categoria': 'Respiratória'},
        {'codigo': 'J45', 'descricao': 'Asma', 'categoria': 'Respiratória'},
        {'codigo': 'J20.9', 'descricao': 'Bronquite aguda', 'categoria': 'Respiratória'},
        
        # Diabetes e metabolismo
        {'codigo': 'E11', 'descricao': 'Diabetes Mellitus tipo 2', 'categoria': 'Endócrina'},
        {'codigo': 'E10', 'descricao': 'Diabetes Mellitus tipo 1', 'categoria': 'Endócrina'},
        {'codigo': 'R73.0', 'descricao': 'Glicemia de jejum alterada', 'categoria': 'Endócrina'},
        
        # Musculoesquelético
        {'codigo': 'M54', 'descricao': 'Dorsalgia', 'categoria': 'Musculoesquelética'},
        {'codigo': 'M79.3', 'descricao': 'Mialgia', 'categoria': 'Musculoesquelética'},
        {'codigo': 'M17', 'descricao': 'Gonartrose (artrose de joelho)', 'categoria': 'Musculoesquelética'},
        
        # Transtornos mentais
        {'codigo': 'F41', 'descricao': 'Ansiedade', 'categoria': 'Mental'},
        {'codigo': 'F32', 'descricao': 'Depressão unipolar', 'categoria': 'Mental'},
        {'codigo': 'F43.2', 'descricao': 'Transtorno de ajustamento', 'categoria': 'Mental'},
        
        # Digestivo
        {'codigo': 'K21', 'descricao': 'Doença do refluxo gastroesofágico', 'categoria': 'Digestiva'},
        {'codigo': 'K29', 'descricao': 'Gastrite', 'categoria': 'Digestiva'},
        {'codigo': 'K59.1', 'descricao': 'Diarreia', 'categoria': 'Digestiva'},
        
        # Genitourinário
        {'codigo': 'N39.0', 'descricao': 'Infecção do trato urinário', 'categoria': 'Genitourinária'},
        {'codigo': 'N40', 'descricao': 'Hiperplasia da próstata', 'categoria': 'Genitourinária'},
        
        # Pele
        {'codigo': 'L89', 'descricao': 'Úlcera de pressão', 'categoria': 'Dermatológica'},
        {'codigo': 'L30', 'descricao': 'Dermatite', 'categoria': 'Dermatológica'},
    ]
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se já existe dados
            if CID10.query.first():
                print("✓ CID-10 já populado")
                return
            
            # Inserir dados
            for item in cid_data:
                cid = CID10(
                    codigo=item['codigo'],
                    descricao=item['descricao'],
                    categoria=item['categoria']
                )
                db.session.add(cid)
            
            db.session.commit()
            print(f"✓ {len(cid_data)} registros de CID-10 inseridos com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Erro ao popular CID-10: {e}")

if __name__ == '__main__':
    seed_cid10()
