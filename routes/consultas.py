"""
MedSystem Consultas Routes - Fluxo completo de consultas
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
# CORREÇÃO 1: Adicionado os modelos que faltavam na importação
from models import Consulta, Paciente, Medico, Exame, LogAuditoria, SinalVital, Diagnostico, Prescricao
from datetime import datetime

consultas_bp = Blueprint('consultas', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/consultas
# Listar todas as consultas
# ════════════════════════════════════════════════════════════
@consultas_bp.route('', methods=['GET'])
@jwt_required()
def listar_consultas():
    try:
        status = request.args.get('status', None)
        pagina = request.args.get('pagina', 1, type=int)
        
        query = Consulta.query
        
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        consultas = query.order_by(Consulta.data_consulta.desc()).paginate(page=pagina, per_page=10)
        
        return jsonify({
            'sucesso': True,
            'total': total,
            'dados': [c.to_dict() for c in consultas.items]
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# GET /api/consultas/<id>
# Buscar consulta específica com todos os detalhes
# ════════════════════════════════════════════════════════════
@consultas_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def buscar_consulta(id):
    try:
        consulta = Consulta.query.get(id)
        
        if not consulta:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Consulta não encontrada'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'dados': consulta.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# GET /api/consultas/paciente/<id_paciente>
# Listar todas as consultas de um paciente
# ════════════════════════════════════════════════════════════
@consultas_bp.route('/paciente/<int:id_paciente>', methods=['GET'])
@jwt_required()
def consultas_paciente(id_paciente):
    try:
        paciente = Paciente.query.get(id_paciente)
        
        if not paciente:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado'
            }), 404
        
        consultas = Consulta.query.filter_by(id_paciente=id_paciente).order_by(Consulta.data_consulta.desc()).all()
        
        return jsonify({
            'sucesso': True,
            'total': len(consultas),
            'dados': [c.to_dict() for c in consultas]
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# POST /api/consultas
# Agendar nova consulta (INSERT + COMMIT)
# ════════════════════════════════════════════════════════════
@consultas_bp.route('', methods=['POST'])
@jwt_required()
def agendar_consulta():
    try:
        dados = request.get_json()
        
        if not dados.get('id_paciente') or not dados.get('id_medico'):
            return jsonify({
                'sucesso': False,
                'mensagem': 'ID do paciente e médico são obrigatórios'
            }), 400
        
        paciente = Paciente.query.get(dados['id_paciente'])
        medico = Medico.query.get(dados['id_medico'])
        
        if not paciente or not paciente.ativo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado ou inativo'
            }), 404
        
        # CORREÇÃO 2: Verificação do status ativo alterada para o relacionamento usuario.ativo
        if not medico or not medico.usuario.ativo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Médico não encontrado ou inativo'
            }), 404
        
        # START TRANSACTION
        try:
            consulta = Consulta(
                id_paciente=dados['id_paciente'],
                id_medico=dados['id_medico'],
                data_consulta=datetime.fromisoformat(dados['data_consulta']),
                status='AGENDADA'
            )
            
            db.session.add(consulta)
            db.session.flush()  # Gera o ID antes do commit definitivo
            
            # CORREÇÃO 3: Atualizado de consulta.id para consulta.id_consulta
            log = LogAuditoria(
                tabela='consulta',
                operacao='INSERT',
                id_registro=consulta.id_consulta, 
                detalhe=f'Consulta agendada: {paciente.nome} com {medico.usuario.nome}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Consulta agendada com sucesso',
                'dados': consulta.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao agendar consulta: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# POST /api/consultas/<id>/sinais-vitais
# Registrar sinais vitais da consulta
# ════════════════════════════════════════════════════════════
@consultas_bp.route('/<int:id>/sinais-vitais', methods=['POST'])
@jwt_required()
def registrar_sinais_vitais(id):
    try:
        consulta = Consulta.query.get(id)
        
        if not consulta:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Consulta não encontrada'
            }), 404
        
        dados = request.get_json()
        
        # START TRANSACTION
        try:
            # CORREÇÃO 4: Adaptação dos campos recebidos para o formato estruturado do models.py (Calculando IMC)
            peso = dados.get('peso_kg')
            altura_cm = dados.get('altura_cm')
            imc_calculado = None
            if peso and altura_cm:
                altura_m = altura_cm / 100
                imc_calculado = round(peso / (altura_m ** 2), 2)

            sinal = SinalVital(
                id_consulta=id,
                pressao_arterial=f"{dados.get('pressao_sistolica', 12)}/{dados.get('pressao_diastolica', 8)}",
                frequencia_cardiaca=dados.get('frequencia_cardiaca'),
                temperatura=dados.get('temperatura'),
                saturacao_oxigenio=dados.get('saturacao_o2'),
                peso=peso,
                altura=int(altura_cm) if altura_cm else None,
                imc=imc_calculado
            )
            
            db.session.add(sinal)
            
            # Marcar consulta como em andamento
            consulta.status = 'EM_ANDAMENTO'
            db.session.flush()
            
            # Log auditoria
            log = LogAuditoria(
                tabela='sinais_vitais',
                operacao='INSERT',
                id_registro=sinal.id,
                detalhe=f'Sinais vitais registrados para consulta ID {id}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Sinais vitais registrados com sucesso',
                'dados': consulta.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao registrar sinais vitais: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# POST /api/consultas/<id>/finalizar
# Finalizar consulta com diagnóstico e prescrições
# ════════════════════════════════════════════════════════════
@consultas_bp.route('/<int:id>/finalizar', methods=['POST'])
@jwt_required()
def finalizar_consulta(id):
    try:
        consulta = Consulta.query.get(id)
        
        if not consulta:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Consulta não encontrada'
            }), 404
        
        dados = request.get_json()
        
        # START TRANSACTION
        try:
            # Registrar diagnóstico
            if 'diagnostico' in dados:
                diag_dados = dados['diagnostico']
                # CORREÇÃO 5: Alterado 'cid10' para 'cid' para corresponder ao models.py
                diagnostico = Diagnostico(
                    id_consulta=id,
                    cid=diag_dados.get('cid10'), 
                    descricao=diag_dados.get('descricao'),
                    gravidade=diag_dados.get('gravidade', 'LEVE')
                )
                db.session.add(diagnostico)
            
            # Registrar prescrições
            if 'prescricoes' in dados:
                for presc_dados in dados['prescricoes']:
                    # CORREÇÃO 6: Concatenação estruturada dos campos extras para a coluna única 'posologia' do models.py
                    posologia_completa = f"Dosagem: {presc_dados.get('dosagem', '')} | Freq: {presc_dados.get('frequencia', '')} | Duracao: {presc_dados.get('duracao', '')}"
                    if presc_dados.get('instrucoes'):
                        posologia_completa += f" | Obs: {presc_dados.get('instrucoes')}"

                    prescricao = Prescricao(
                        id_consulta=id,
                        medicamento=presc_dados.get('medicamento'),
                        posologia=posologia_completa
                    )
                    db.session.add(prescricao)
            
            # Marcar consulta como concluída
            consulta.status = 'CONCLUIDA'
            
            # Log auditoria
            log = LogAuditoria(
                tabela='consulta',
                operacao='UPDATE',
                id_registro=id,
                detalhe=f'Consulta finalizada com diagnóstico e tratamento clínico'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Consulta finalizada com sucesso',
                'dados': consulta.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao finalizar consulta: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# PUT /api/consultas/<id>/status
# Atualizar status da consulta
# ════════════════════════════════════════════════════════════
@consultas_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
def atualizar_status_consulta(id):
    try:
        consulta = Consulta.query.get(id)
        
        if not consulta:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Consulta não encontrada'
            }), 404
        
        dados = request.get_json()
        novo_status = dados.get('status', '').upper()
        
        if novo_status not in ['AGENDADA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA']:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Status inválido'
            }), 400
        
        # START TRANSACTION
        try:
            status_antigo = consulta.status
            consulta.status = novo_status
            
            # Log auditoria
            log = LogAuditoria(
                tabela='consulta',
                operacao='UPDATE',
                id_registro=id,
                detalhe=f'Status alterado de {status_antigo} para {novo_status}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Status atualizado com sucesso',
                'dados': consulta.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar status: {str(e)}'
        }), 500