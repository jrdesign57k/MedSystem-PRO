"""
MedSystem Prontuário Routes - Prontuário eletrônico
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Consulta, Paciente, Medico, SinalVital, Diagnostico, Exame, Prescricao
from datetime import datetime

prontuario_bp = Blueprint('prontuario', __name__)

# ════════════════════════════════════════════════════════════
# POST /api/prontuarios
# Criar/Salvar prontuário
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('', methods=['POST'])
@jwt_required()
def criar_prontuario():
    try:
        dados = request.get_json()
        id_consulta = dados.get('id_consulta')
        
        # Buscar consulta existente
        consulta = Consulta.query.get(id_consulta)
        if not consulta:
            return jsonify({'sucesso': False, 'erro': 'Consulta não encontrada'}), 404
        
        # Atualizar campos do prontuário na consulta
        consulta.queixa_principal = dados.get('queixa_principal')
        consulta.historia_molestia_atual = dados.get('historia_molestia_atual')
        consulta.antecedentes_pessoais = dados.get('antecedentes_pessoais')
        consulta.antecedentes_familiares = dados.get('antecedentes_familiares')
        consulta.exame_fisico = dados.get('exame_fisico')
        consulta.hipotese_diagnostica = dados.get('hipotese_diagnostica')
        consulta.plano_terapeutico = dados.get('plano_terapeutico')
        consulta.status = 'CONCLUÍDA'
        
        # Salvar sinais vitais
        sinal = SinalVital()
        sinal.id_consulta = id_consulta
        sinal.pressao_arterial = dados.get('pa')
        sinal.frequencia_cardiaca = dados.get('fc')
        sinal.temperatura = dados.get('temperatura')
        sinal.saturacao_oxigenio = dados.get('spo2')
        sinal.peso = dados.get('peso')
        
        db.session.add(sinal)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Prontuário salvo com sucesso',
            'id_consulta': id_consulta
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/prontuarios/:id
# Obter prontuário
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('/<int:id_consulta>', methods=['GET'])
@jwt_required()
def obter_prontuario(id_consulta):
    try:
        consulta = Consulta.query.get(id_consulta)
        if not consulta:
            return jsonify({'sucesso': False, 'erro': 'Consulta não encontrada'}), 404
        
        # Buscar sinais vitais
        sinais = SinalVital.query.filter_by(id_consulta=id_consulta).first()
        
        # Buscar diagnósticos
        diagnosticos = Diagnostico.query.filter_by(id_consulta=id_consulta).all()
        
        # Buscar exames solicitados
        exames = Exame.query.filter_by(id_consulta=id_consulta).all()
        
        return jsonify({
            'sucesso': True,
            'consulta': {
                'id': consulta.id_consulta,
                'paciente': consulta.paciente.nome if consulta.paciente else '',
                'medico': consulta.medico.usuario.nome if (consulta.medico and consulta.medico.usuario) else '',
                'data': consulta.data_consulta.strftime('%d/%m/%Y') if consulta.data_consulta else '',
                'queixa_principal': consulta.queixa_principal,
                'historia_molestia_atual': consulta.historia_molestia_atual,
                'antecedentes_pessoais': consulta.antecedentes_pessoais,
                'antecedentes_familiares': consulta.antecedentes_familiares,
                'exame_fisico': consulta.exame_fisico,
                'hipotese_diagnostica': consulta.hipotese_diagnostica,
                'plano_terapeutico': consulta.plano_terapeutico
            },
            'sinais_vitais': sinais.to_dict() if sinais else {},
            'diagnosticos': [d.to_dict() for d in diagnosticos],
            'exames': [e.to_dict() for e in exames]
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# PUT /api/prontuarios/:id
# Atualizar prontuário
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('/<int:id_consulta>', methods=['PUT'])
@jwt_required()
def atualizar_prontuario(id_consulta):
    try:
        dados = request.get_json()
        
        consulta = Consulta.query.get(id_consulta)
        if not consulta:
            return jsonify({'sucesso': False, 'erro': 'Consulta não encontrada'}), 404
        
        consulta.queixa_principal = dados.get('queixa_principal', consulta.queixa_principal)
        consulta.historia_molestia_atual = dados.get('historia_molestia_atual', consulta.historia_molestia_atual)
        consulta.antecedentes_pessoais = dados.get('antecedentes_pessoais', consulta.antecedentes_pessoais)
        consulta.antecedentes_familiares = dados.get('antecedentes_familiares', consulta.antecedentes_familiares)
        consulta.exame_fisico = dados.get('exame_fisico', consulta.exame_fisico)
        consulta.hipotese_diagnostica = dados.get('hipotese_diagnostica', consulta.hipotese_diagnostica)
        consulta.plano_terapeutico = dados.get('plano_terapeutico', consulta.plano_terapeutico)
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Prontuário atualizado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
