"""
MedSystem Additional Routes - Exames e Dashboard
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Exame, TipoExame, Consulta, Paciente, LogAuditoria, Diagnostico, Medico
from datetime import datetime, timedelta

exames_bp = Blueprint('exames', __name__)
dashboard_bp = Blueprint('dashboard', __name__)

# ════════════════════════════════════════════════════════════
# EXAMES
# ════════════════════════════════════════════════════════════

@exames_bp.route('', methods=['GET'])
@jwt_required()
def listar_exames():
    """Lista todos os exames"""
    try:
        status = request.args.get('status', None)
        query = Exame.query
        
        if status:
            query = query.filter_by(status=status)
        
        # Como data_solicitacao não existe no modelo atual, ordenamos pelo ID
        exames = query.order_by(Exame.id.desc()).all()
        
        return jsonify({
            'sucesso': True,
            'total': len(exames),
            'dados': [e.to_dict() for e in exames]
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@exames_bp.route('/pendentes', methods=['GET'])
@jwt_required()
def listar_exames_pendentes():
    """Lista exames pendentes (CURSOR - simulado com query)"""
    try:
        exames = Exame.query.filter(
            Exame.status.in_(['SOLICITADO', 'EM_ANALISE'])
        ).order_by(Exame.id).all()
        
        # Agrupar por paciente
        exames_por_paciente = {}
        for exame in exames:
            # Busca a consulta associada para achar o paciente
            consulta = Consulta.query.get(exame.id_consulta)
            if not consulta:
                continue
                
            paciente = Paciente.query.get(consulta.id_paciente)
            if not paciente:
                continue
                
            paciente_nome = paciente.nome
            if paciente_nome not in exames_por_paciente:
                exames_por_paciente[paciente_nome] = {
                    'id_paciente': paciente.id_paciente,
                    'quantidade': 0,
                    'exames': []
                }
            exames_por_paciente[paciente_nome]['quantidade'] += 1
            exames_por_paciente[paciente_nome]['exames'].append(exame.to_dict())
        
        return jsonify({
            'sucesso': True,
            'total': len(exames_por_paciente),
            'dados': exames_por_paciente
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@exames_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def buscar_exame(id):
    """Busca um exame específico"""
    try:
        exame = Exame.query.get(id)
        
        if not exame:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Exame não encontrado'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'dados': exame.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@exames_bp.route('/<int:id>/resultado', methods=['PUT'])
@jwt_required()
def registrar_resultado_exame(id):
    """Registra resultado do exame"""
    try:
        exame = Exame.query.get(id)
        
        if not exame:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Exame não encontrado'
            }), 404
        
        dados = request.get_json()
        
        try:
            exame.resultado = dados.get('resultado')
            exame.status = dados.get('status', 'CONCLUIDO')
            
            db.session.flush()
            
            log = LogAuditoria(
                tabela='exames',
                operacao='UPDATE',
                id_registro=exame.id,
                detalhe=f'Resultado registrado para o exame ID: {exame.id}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Resultado registrado com sucesso',
                'dados': exame.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════

@dashboard_bp.route('/estatisticas', methods=['GET'])
@jwt_required()
def obter_estatisticas():
    """Retorna estatísticas do dashboard"""
    try:
        hoje = datetime.now().date()
        
        # Consultas de hoje
        consultas_hoje = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta < datetime(hoje.year, hoje.month, hoje.day) + timedelta(days=1)
        ).count()
        
        # Pacientes ativos
        pacientes_ativos = Paciente.query.filter_by(ativo=True).count()
        
        # Exames pendentes
        exames_pendentes = Exame.query.filter(
            Exame.status.in_(['SOLICITADO', 'EM_ANALISE'])
        ).count()
        
        # Consultas próximas (próximos 7 dias)
        data_futura = hoje + timedelta(days=7)
        consultas_proximas = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta <= datetime(data_futura.year, data_futura.month, data_futura.day)
        ).count()
        
        # Últimas consultas de hoje
        ultimas_consultas = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta < datetime(hoje.year, hoje.month, hoje.day) + timedelta(days=1)
        ).order_by(Consulta.data_consulta.desc()).limit(5).all()
        
        ultimas_list = []
        for c in ultimas_consultas:
            ultimas_list.append({
                'id_consulta': c.id_consulta,
                'id_paciente': c.id_paciente,
                'paciente_nome': c.paciente.nome if c.paciente else 'N/A',
                'data': c.data_consulta.isoformat() if c.data_consulta else None,
                'hora': c.hora_consulta or '—',
                'status': c.status or 'AGENDADA'
            })
        
        return jsonify({
            'sucesso': True,
            'dados': {
                'consultas_hoje': consultas_hoje,
                'pacientes_ativos': pacientes_ativos,
                'exames_pendentes': exames_pendentes,
                'consultas_proximas': consultas_proximas,
                'ultimas_consultas': ultimas_list
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@dashboard_bp.route('/alertas', methods=['GET'])
@jwt_required()
def obter_alertas():
    """Alertas clínicos por classificação de risco (baixo, médio, alto, crítico)."""
    try:
        ordem = {'CRITICA': 0, 'GRAVE': 1, 'MODERADA': 2, 'LEVE': 3}
        rotulos = {
            'LEVE': 'RISCO BAIXO',
            'MODERADA': 'RISCO MÉDIO',
            'GRAVE': 'RISCO ALTO',
            'CRITICA': 'RISCO CRÍTICO',
        }

        diagnosticos = Diagnostico.query.filter(
            Diagnostico.status == 'ATIVO',
            Diagnostico.gravidade.in_(['LEVE', 'MODERADA', 'GRAVE', 'CRITICA'])
        ).all()

        alertas = []
        for diag in diagnosticos:
            consulta = Consulta.query.get(diag.id_consulta)
            if not consulta:
                continue
            paciente = Paciente.query.get(diag.id_paciente)
            if not paciente or not paciente.ativo:
                continue

            grav = (diag.gravidade or 'LEVE').upper()
            if grav not in rotulos:
                grav = 'LEVE'

            alertas.append({
                'paciente': paciente.nome,
                'id_paciente': paciente.id_paciente,
                'id_consulta': diag.id_consulta,
                'tipo': rotulos[grav],
                'descricao': f'{diag.cid} — {diag.descricao}',
                'gravidade': grav,
                'cid': diag.cid,
                'data': consulta.data_consulta.isoformat() if consulta.data_consulta else None,
            })

        alertas.sort(key=lambda a: (ordem.get(a['gravidade'], 9), a['paciente']))

        return jsonify({
            'sucesso': True,
            'total': len(alertas),
            'dados': alertas,
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@dashboard_bp.route('/agenda/semana', methods=['GET'])
@jwt_required()
def agenda_semanal():
    """Agenda semanal para a interface PRO"""
    try:
        hoje = datetime.now().date()
        dias_pt = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        horarios = ['08:00', '09:30', '11:00', '14:00', '15:30', '17:00']
        dias = []

        for i in range(7):
            dia = hoje + timedelta(days=i)
            inicio = datetime(dia.year, dia.month, dia.day)
            fim = inicio + timedelta(days=1)

            consultas = Consulta.query.filter(
                Consulta.data_consulta >= inicio,
                Consulta.data_consulta < fim,
                Consulta.status != 'CANCELADA'
            ).all()

            consultas_list = []
            for c in consultas:
                hora = (c.hora_consulta or
                        (c.data_consulta.strftime('%H:%M') if c.data_consulta else '08:00'))[:5]
                consultas_list.append({
                    'hora': hora,
                    'paciente': c.paciente.nome if c.paciente else 'Paciente',
                    'motivo': c.motivo or c.tipo_consulta or 'Consulta',
                    'status': c.status or 'AGENDADA'
                })

            dias.append({
                'label': dias_pt[dia.weekday()],
                'dia': dia.strftime('%d/%m'),
                'hoje': i == 0,
                'consultas': consultas_list
            })

        return jsonify({
            'sucesso': True,
            'dados': {
                'dias': dias,
                'horarios': horarios
            }
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@dashboard_bp.route('/proximas-consultas', methods=['GET'])
@jwt_required()
def proximas_consultas():
    """Retorna próximas consultas agendadas"""
    try:
        hoje = datetime.now().date()
        proximas = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta <= datetime(hoje.year, hoje.month, hoje.day) + timedelta(days=30)
        ).order_by(Consulta.data_consulta).all()
        
        consultas_list = []
        for c in proximas:
            consultas_list.append({
                'id': c.id,
                'paciente': c.paciente.nome if c.paciente else 'N/A',
                'medico': c.medico.usuario.nome if c.medico and c.medico.usuario else 'N/A',
                'data': c.data_consulta.isoformat() if c.data_consulta else None,
                'motivo': c.motivo or 'Consulta',
                'status': c.status or 'Agendada'
            })
        
        return jsonify({
            'sucesso': True,
            'total': len(consultas_list),
            'dados': consultas_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# GRÁFICOS - ATENDIMENTOS E CLASSIFICAÇÃO DE RISCO
# ════════════════════════════════════════════════════════════

@dashboard_bp.route('/grafico/atendimentos', methods=['GET'])
@jwt_required()
def grafico_atendimentos():
    """Retorna dados para gráfico de atendimentos por período"""
    try:
        periodo = request.args.get('periodo', 'mes')  # dia, semana, mes, ano
        
        # Análise por período
        if periodo == 'dia':
            inicio = datetime.now().date()
            dias = 1
        elif periodo == 'semana':
            inicio = (datetime.now() - timedelta(days=7)).date()
            dias = 7
        elif periodo == 'ano':
            inicio = (datetime.now() - timedelta(days=365)).date()
            dias = 365
        else:  # mes (default)
            inicio = (datetime.now() - timedelta(days=30)).date()
            dias = 30
        
        # Agrupa consultas por data
        consultas = Consulta.query.filter(
            Consulta.data_consulta >= inicio
        ).all()
        
        # Contagem por data
        atendimentos_por_dia = {}
        for i in range(dias):
            data = (datetime.combine(inicio, datetime.min.time()) + timedelta(days=i)).date()
            atendimentos_por_dia[data.isoformat()] = 0
        
        for consulta in consultas:
            if consulta.data_consulta:
                data_key = consulta.data_consulta.date().isoformat()
                if data_key in atendimentos_por_dia:
                    atendimentos_por_dia[data_key] += 1
        
        # Contagem por médico (últimos 30 dias)
        medicos_count = {}
        medicos = db.session.query(
            Medico.id,
            db.func.count(Consulta.id).label('total')
        ).join(Consulta, Medico.id == Consulta.id_medico).filter(
            Consulta.data_consulta >= (datetime.now() - timedelta(days=30))
        ).group_by(Medico.id).all()
        
        for medico in medicos:
            med = Medico.query.get(medico[0])
            if med and med.usuario:
                medicos_count[med.usuario.nome] = medico[1]
        
        # Contagem por status (últimas consultas)
        status_count = {}
        estatuses = db.session.query(
            Consulta.status,
            db.func.count(Consulta.id).label('total')
        ).filter(
            Consulta.data_consulta >= (datetime.now() - timedelta(days=30))
        ).group_by(Consulta.status).all()
        
        for status, count in estatuses:
            status_count[status or 'Não definido'] = count
        
        return jsonify({
            'sucesso': True,
            'periodo': periodo,
            'atendimentos_por_dia': atendimentos_por_dia,
            'atendimentos_por_medico': medicos_count,
            'atendimentos_por_status': status_count,
            'total_atendimentos': len(consultas)
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@dashboard_bp.route('/grafico/classificacao-risco', methods=['GET'])
@jwt_required()
def grafico_classificacao_risco():
    """Retorna dados para gráfico de classificação de risco"""
    try:
        # Análise de diagnósticos por gravidade
        diagnosticos = Diagnostico.query.all()
        
        gravidade_count = {
            'LEVE': 0,
            'MODERADA': 0,
            'GRAVE': 0,
            'CRITICA': 0
        }
        
        for diag in diagnosticos:
            gravidade = (diag.gravidade or 'LEVE').upper()
            if gravidade == 'CRÍTICA':
                gravidade = 'CRITICA'
            if gravidade in gravidade_count:
                gravidade_count[gravidade] += 1
        
        # Cores para cada nível
        cores = {
            'LEVE': '#38a169',
            'MODERADA': '#d69e2e',
            'GRAVE': '#ed8936',
            'CRITICA': '#e53e3e'
        }
        
        # Pacientes por nível de risco (simulado baseado em diagnósticos críticos)
        consultas_criticas = db.session.query(
            Paciente.id_paciente,
            Paciente.nome,
            db.func.count(Diagnostico.id).label('total_diagnosticos_criticos')
        ).join(
            Consulta, Paciente.id_paciente == Consulta.id_paciente
        ).join(
            Diagnostico, Consulta.id_consulta == Diagnostico.id_consulta
        ).filter(
            Diagnostico.gravidade.in_(['GRAVE', 'CRITICA'])
        ).group_by(Paciente.id_paciente).all()
        
        risco_pacientes = []
        for pac in consultas_criticas:
            risco_pacientes.append({
                'paciente': pac[1],
                'diagnosticos_criticos': pac[2]
            })
        
        # Tendência de risco (últimos 7 dias)
        tendencia_diaria = {}
        for i in range(7):
            data = (datetime.now() - timedelta(days=6-i)).date()
            data_key = data.isoformat()
            tendencia_diaria[data_key] = 0
        
        diags_recentes = Diagnostico.query.join(
            Consulta, Diagnostico.id_consulta == Consulta.id_consulta
        ).filter(
            Diagnostico.gravidade.in_(['GRAVE', 'CRITICA']),
            Consulta.data_consulta >= (datetime.now() - timedelta(days=7))
        ).all()
        
        for diag in diags_recentes:
            if diag.consulta and diag.consulta.data_consulta:
                data_key = diag.consulta.data_consulta.date().isoformat()
                if data_key in tendencia_diaria:
                    tendencia_diaria[data_key] += 1
        
        return jsonify({
            'sucesso': True,
            'classificacao_risco': gravidade_count,
            'cores_risco': cores,
            'pacientes_risco_alto': risco_pacientes,
            'tendencia_7_dias': tendencia_diaria
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500