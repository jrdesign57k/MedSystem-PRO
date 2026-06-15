"""
MedSystem Consultas Routes - Fluxo completo de consultas
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Consulta, Paciente, Medico, Exame, LogAuditoria, SinalVital, Diagnostico, Prescricao, Receita, PrecoConsulta
from datetime import datetime, timedelta

consultas_bp = Blueprint('consultas', __name__)

TIPOS_COM_PRECO = ['1ª Consulta', 'Retorno', 'Urgência']
HORARIOS_AGENDA = ['08:00', '09:30', '11:00', '14:00', '15:30', '17:00']
STATUS_ATIVOS = ['AGENDADA', 'EM_ATENDIMENTO', 'EM_ANDAMENTO', 'CONCLUIDA']


def _normalizar_hora(hora):
    if not hora:
        return None
    h = str(hora).strip()[:5]
    if len(h) == 5 and h[2] == ':':
        return h
    return None


def _inicio_fim_dia(data_dt):
    inicio = data_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio, inicio + timedelta(days=1)


def _consulta_no_horario(id_medico, data_dt, hora):
    """Retorna consulta ativa no mesmo médico/data/hora, ou None."""
    hora_norm = _normalizar_hora(hora)
    if not hora_norm:
        return None
    inicio, fim = _inicio_fim_dia(data_dt)
    consultas = Consulta.query.filter(
        Consulta.id_medico == id_medico,
        Consulta.data_consulta >= inicio,
        Consulta.data_consulta < fim,
        Consulta.status.in_(STATUS_ATIVOS)
    ).all()
    for c in consultas:
        c_hora = _normalizar_hora(c.hora_consulta) or _normalizar_hora(
            c.data_consulta.strftime('%H:%M') if c.data_consulta else None
        )
        if c_hora == hora_norm:
            return c
    return None


def _criar_receita_agendamento(consulta, paciente, tipo_consulta, convenio):
    """Gera receita pendente com valor da tabela de preços."""
    if tipo_consulta not in TIPOS_COM_PRECO:
        return None, 'Tipo de consulta sem tabela de preços — receita não gerada'

    existente = Receita.query.filter_by(id_consulta=consulta.id_consulta).first()
    if existente:
        return existente, None

    preco = PrecoConsulta.buscar(tipo_consulta, convenio)
    if not preco:
        return None, f'Preço não cadastrado para {tipo_consulta} / {convenio or "Particular"}'

    convenio_norm = PrecoConsulta.normalizar_convenio(convenio)
    receita = Receita(
        id_consulta=consulta.id_consulta,
        id_paciente=consulta.id_paciente,
        id_medico=consulta.id_medico,
        descricao=f'{tipo_consulta} — {paciente.nome}',
        valor=preco.valor,
        tipo='Particular' if convenio_norm is None else 'Convênio',
        convenio=convenio if convenio_norm else 'Particular',
        status='PENDENTE'
    )
    db.session.add(receita)
    return receita, None

# ════════════════════════════════════════════════════════════
# GET /api/consultas
# Listar todas as consultas (COM PAGINAÇÃO PARA O FRONTEND)
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
        
        lista_formatada = []
        for c in consultas.items:
            dados = c.to_dict()
            # Injeta os nomes para o Frontend não se perder
            nome_paciente = c.paciente.nome if c.paciente else 'Desconhecido'
            nome_medico = c.medico.usuario.nome if (c.medico and c.medico.usuario) else 'Desconhecido'
            
            dados['paciente_nome'] = nome_paciente
            dados['medico_nome'] = nome_medico
            
            # Formato aninhado (caso o JS use consulta.paciente.nome)
            dados['paciente'] = {'nome': nome_paciente}
            dados['medico'] = {'usuario': {'nome': nome_medico}}
            
            lista_formatada.append(dados)
        
        return jsonify({
            'sucesso': True,
            'total': total,
            'dados': lista_formatada
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
# GET /api/consultas/horarios-disponiveis
# Horários do médico em uma data (livres x reservados)
# ════════════════════════════════════════════════════════════
@consultas_bp.route('/horarios-disponiveis', methods=['GET'])
@jwt_required()
def horarios_disponiveis():
    try:
        id_medico = request.args.get('id_medico', type=int)
        data_str = request.args.get('data')
        if not id_medico or not data_str:
            return jsonify({'sucesso': False, 'mensagem': 'Informe id_medico e data (YYYY-MM-DD)'}), 400

        medico = Medico.query.get(id_medico)
        if not medico:
            return jsonify({'sucesso': False, 'mensagem': 'Médico não encontrado'}), 404

        data_dt = datetime.fromisoformat(data_str + 'T00:00:00')
        inicio, fim = _inicio_fim_dia(data_dt)
        consultas = Consulta.query.filter(
            Consulta.id_medico == id_medico,
            Consulta.data_consulta >= inicio,
            Consulta.data_consulta < fim,
            Consulta.status.in_(STATUS_ATIVOS)
        ).all()

        ocupados = {}
        for c in consultas:
            h = _normalizar_hora(c.hora_consulta) or _normalizar_hora(
                c.data_consulta.strftime('%H:%M') if c.data_consulta else None
            )
            if h:
                ocupados[h] = {
                    'paciente': c.paciente.nome if c.paciente else 'Paciente',
                    'status': c.status
                }

        horarios = []
        for h in HORARIOS_AGENDA:
            if h in ocupados:
                horarios.append({
                    'hora': h,
                    'disponivel': False,
                    'paciente': ocupados[h]['paciente'],
                    'status': ocupados[h]['status']
                })
            else:
                horarios.append({'hora': h, 'disponivel': True})

        return jsonify({
            'sucesso': True,
            'horarios': horarios,
            'data': data_str,
            'id_medico': id_medico
        }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

# ════════════════════════════════════════════════════════════
# POST /api/consultas
# Agendar nova consulta 
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
        
        if not medico or not medico.usuario.ativo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Médico não encontrado ou inativo'
            }), 404
        
        # START TRANSACTION
        try:
            tipo_consulta = dados.get('tipo_consulta', '1ª Consulta')
            convenio = dados.get('convenio', 'Particular')
            hora_consulta = _normalizar_hora(dados.get('hora_consulta'))
            data_consulta = datetime.fromisoformat(dados['data_consulta'])

            if not hora_consulta:
                return jsonify({'sucesso': False, 'mensagem': 'Horário inválido'}), 400
            if hora_consulta not in HORARIOS_AGENDA:
                return jsonify({'sucesso': False, 'mensagem': 'Horário fora da grade de atendimento'}), 400

            conflito = _consulta_no_horario(dados['id_medico'], data_consulta, hora_consulta)
            if conflito:
                pac = conflito.paciente.nome if conflito.paciente else 'outro paciente'
                return jsonify({
                    'sucesso': False,
                    'mensagem': f'Horário {hora_consulta} já reservado para {pac}'
                }), 409

            consulta = Consulta(
                id_paciente=dados['id_paciente'],
                id_medico=dados['id_medico'],
                data_consulta=data_consulta,
                hora_consulta=hora_consulta,
                motivo=dados.get('motivo'),
                tipo_consulta=tipo_consulta,
                convenio=convenio,
                observacoes_consulta=dados.get('observacoes'),
                status='AGENDADA'
            )
            
            db.session.add(consulta)
            db.session.flush()

            receita, aviso_preco = _criar_receita_agendamento(
                consulta, paciente, tipo_consulta, convenio
            )
            
            log = LogAuditoria(
                tabela='consulta',
                operacao='INSERT',
                id_registro=consulta.id_consulta, 
                detalhe=f'Consulta agendada: {paciente.nome} com {medico.usuario.nome}'
            )
            db.session.add(log)
            db.session.commit()
            
            resposta = {
                'sucesso': True,
                'mensagem': 'Consulta agendada com sucesso',
                'dados': consulta.to_dict()
            }
            if receita:
                resposta['receita'] = receita.to_dict()
                resposta['mensagem'] += f' — Receita de R$ {receita.valor:.2f} gerada'
            elif aviso_preco:
                resposta['aviso_preco'] = aviso_preco

            return jsonify(resposta), 201
            
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
            consulta.status = 'EM_ATENDIMENTO'
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
        
        if novo_status not in ['AGENDADA', 'EM_ATENDIMENTO', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA']:
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