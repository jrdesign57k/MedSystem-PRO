"""
MedSystem Relatórios Routes - Indicadores clínicos e operacionais
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models import Consulta, Diagnostico, Medico, Paciente, Exame
from datetime import datetime, timedelta
from sqlalchemy import func

relatorios_bp = Blueprint('relatorios', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/relatorios
# Indicadores principais
# ════════════════════════════════════════════════════════════
@relatorios_bp.route('', methods=['GET'])
@jwt_required()
def obter_relatorios():
    try:
        mes_anterior = datetime.utcnow().replace(day=1) - timedelta(days=1)
        mes_atual = datetime.utcnow().replace(day=1)
        
        # Métricas do mês atual
        consultas_mes = Consulta.query.filter(
            Consulta.data_consulta >= mes_atual
        ).count()
        
        novos_pacientes = Paciente.query.filter(
            Paciente.data_cadastro >= mes_atual
        ).count()
        
        retornos = Consulta.query.filter(
            Consulta.data_consulta >= mes_atual,
            Consulta.tipo_consulta == 'Retorno'
        ).count()
        
        exames_solicitados = Exame.query.filter(
            Exame.data_solicitacao >= mes_atual
        ).count()
        
        # Top 5 diagnósticos
        top_diagnosticos = db.session.query(
            Diagnostico.cid,
            Diagnostico.descricao,
            func.count(Diagnostico.id).label('total')
        ).filter(
            Diagnostico.data_diagnostico >= mes_atual
        ).group_by(Diagnostico.cid, Diagnostico.descricao).order_by(
            func.count(Diagnostico.id).desc()
        ).limit(5).all()
        
        diagnosticos_list = []
        for cid, desc, total in top_diagnosticos:
            diagnosticos_list.append({
                'cid': cid,
                'descricao': desc,
                'casos': total
            })
        
        # Consultas por médico
        consultas_por_medico = db.session.query(
            Medico.id,
            Medico.crm,
            func.count(Consulta.id_consulta).label('total')
        ).join(
            Consulta, Medico.id == Consulta.id_medico
        ).filter(
            Consulta.data_consulta >= mes_atual
        ).group_by(Medico.id, Medico.crm).all()
        
        medicos_list = []
        for medico_id, crm, total in consultas_por_medico:
            medico = Medico.query.get(medico_id)
            medicos_list.append({
                'id': medico_id,
                'nome': medico.usuario.nome if medico and medico.usuario else 'Desconhecido',
                'crm': crm,
                'consultas': total
            })
        
        # Comparação com mês anterior
        consultas_mes_ant = Consulta.query.filter(
            Consulta.data_consulta >= mes_anterior.replace(day=1),
            Consulta.data_consulta < mes_atual
        ).count()
        
        variacao_consultas = ((consultas_mes - consultas_mes_ant) / max(consultas_mes_ant, 1)) * 100 if consultas_mes_ant else 0
        
        return jsonify({
            'sucesso': True,
            'periodo': {
                'mes': datetime.utcnow().strftime('%B/%Y'),
                'inicio': mes_atual.strftime('%d/%m/%Y'),
                'fim': (datetime.utcnow() + timedelta(days=1)).strftime('%d/%m/%Y')
            },
            'indicadores': {
                'consultas_mes': consultas_mes,
                'variacao_consultas': round(variacao_consultas, 2),
                'novos_pacientes': novos_pacientes,
                'retornos': retornos,
                'exames_solicitados': exames_solicitados,
                'taxa_retorno': round((retornos / max(consultas_mes, 1)) * 100, 2) if consultas_mes else 0
            },
            'top_diagnosticos': diagnosticos_list,
            'consultas_por_medico': sorted(medicos_list, key=lambda x: x['consultas'], reverse=True)
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/relatorios/diario
# Relatório diário
# ════════════════════════════════════════════════════════════
@relatorios_bp.route('/diario', methods=['GET'])
@jwt_required()
def relatorio_diario():
    try:
        data = request.args.get('data', datetime.utcnow().strftime('%Y-%m-%d'))
        data_obj = datetime.strptime(data, '%Y-%m-%d')
        
        # Consultas do dia
        consultas = Consulta.query.filter(
            db.func.date(Consulta.data_consulta) == data_obj.date()
        ).all()
        
        # Estatísticas do dia
        concluidas = len([c for c in consultas if c.status == 'CONCLUÍDA'])
        agendadas = len([c for c in consultas if c.status == 'AGENDADA'])
        canceladas = len([c for c in consultas if c.status == 'CANCELADA'])
        
        return jsonify({
            'sucesso': True,
            'data': data,
            'consultas': [c.to_dict() for c in consultas],
            'estatisticas': {
                'total': len(consultas),
                'concluidas': concluidas,
                'agendadas': agendadas,
                'canceladas': canceladas
            }
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/relatorios/semanal
# Relatório semanal
# ════════════════════════════════════════════════════════════
@relatorios_bp.route('/semanal', methods=['GET'])
@jwt_required()
def relatorio_semanal():
    try:
        today = datetime.utcnow()
        inicio_semana = today - timedelta(days=today.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        # Consultas da semana
        consultas = Consulta.query.filter(
            Consulta.data_consulta >= inicio_semana,
            Consulta.data_consulta <= fim_semana
        ).all()
        
        # Estatísticas por dia
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        stats_por_dia = {}
        
        for i in range(7):
            dia = inicio_semana + timedelta(days=i)
            stats_por_dia[dias_semana[i]] = {
                'data': dia.strftime('%d/%m'),
                'total': 0,
                'concluidas': 0
            }
            
            for c in consultas:
                if c.data_consulta.date() == dia.date():
                    stats_por_dia[dias_semana[i]]['total'] += 1
                    if c.status == 'CONCLUÍDA':
                        stats_por_dia[dias_semana[i]]['concluidas'] += 1
        
        return jsonify({
            'sucesso': True,
            'periodo': {
                'inicio': inicio_semana.strftime('%d/%m/%Y'),
                'fim': fim_semana.strftime('%d/%m/%Y')
            },
            'consultas': [c.to_dict() for c in consultas],
            'por_dia': stats_por_dia,
            'totais': {
                'total': len(consultas),
                'concluidas': len([c for c in consultas if c.status == 'CONCLUÍDA'])
            }
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/relatorios/mensal
# Relatório mensal
# ════════════════════════════════════════════════════════════
@relatorios_bp.route('/mensal', methods=['GET'])
@jwt_required()
def relatorio_mensal():
    try:
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        if not mes or not ano:
            today = datetime.utcnow()
            mes = today.month
            ano = today.year
        else:
            mes = int(mes)
            ano = int(ano)
        
        inicio_mes = datetime(ano, mes, 1)
        if mes == 12:
            fim_mes = datetime(ano + 1, 1, 1) - timedelta(days=1)
        else:
            fim_mes = datetime(ano, mes + 1, 1) - timedelta(days=1)
        
        consultas = Consulta.query.filter(
            Consulta.data_consulta >= inicio_mes,
            Consulta.data_consulta <= fim_mes.replace(hour=23, minute=59, second=59)
        ).all()
        
        # Novos pacientes do mês
        novos = Paciente.query.filter(
            Paciente.data_cadastro >= inicio_mes,
            Paciente.data_cadastro <= fim_mes
        ).count()
        
        return jsonify({
            'sucesso': True,
            'mes': mes,
            'ano': ano,
            'periodo': {
                'inicio': inicio_mes.strftime('%d/%m/%Y'),
                'fim': fim_mes.strftime('%d/%m/%Y')
            },
            'totais': {
                'consultas': len(consultas),
                'concluidas': len([c for c in consultas if c.status == 'CONCLUÍDA']),
                'novos_pacientes': novos
            }
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
