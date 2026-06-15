"""
MedSystem Financeiro Routes - Receitas, despesas e faturamento
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models import Receita, Despesa, Consulta
from datetime import datetime, timedelta
from sqlalchemy import func

financeiro_bp = Blueprint('financeiro', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/financeiro
# Dashboard financeiro com resumo
# ════════════════════════════════════════════════════════════
@financeiro_bp.route('', methods=['GET'])
@jwt_required()
def obter_financeiro():
    try:
        today = datetime.utcnow()
        primeiro_dia_mes = today.replace(day=1)
        
        # Receitas do mês
        total_receitas = db.session.query(func.sum(Receita.valor)).filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes
        ).scalar() or 0
        
        # Receitas pagas
        receitas_pagas = Receita.query.filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes,
            Receita.status == 'PAGO'
        ).count()
        
        # A receber
        a_receber = db.session.query(func.sum(Receita.valor)).filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes,
            Receita.status == 'PENDENTE'
        ).scalar() or 0
        
        # Despesas do mês
        total_despesas = db.session.query(func.sum(Despesa.valor)).filter(
            func.date(Despesa.data_despesa) >= primeiro_dia_mes
        ).scalar() or 0
        
        # Lançamentos recentes
        lancamentos = []
        
        receitas_recentes = Receita.query.filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes
        ).order_by(Receita.data_receita.desc()).limit(5).all()
        
        for r in receitas_recentes:
            lancamentos.append({
                'data': r.data_receita.strftime('%d/%m'),
                'descricao': r.descricao,
                'tipo': 'Entrada',
                'valor': r.valor,
                'status': r.status
            })
        
        despesas_recentes = Despesa.query.filter(
            func.date(Despesa.data_despesa) >= primeiro_dia_mes
        ).order_by(Despesa.data_despesa.desc()).limit(5).all()
        
        for d in despesas_recentes:
            lancamentos.append({
                'data': d.data_despesa.strftime('%d/%m'),
                'descricao': d.descricao,
                'tipo': 'Saída',
                'valor': -d.valor,
                'status': d.status
            })
        
        # Receita por categoria/convênio
        receita_por_tipo = db.session.query(
            Receita.tipo,
            func.sum(Receita.valor)
        ).filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes
        ).group_by(Receita.tipo).all()
        
        categorias = []
        for tipo, valor in receita_por_tipo:
            categorias.append({
                'nome': tipo or 'Particular',
                'valor': valor or 0
            })
        
        return jsonify({
            'sucesso': True,
            'metricas': {
                'receita_mensal': total_receitas,
                'consultas_pagas': receitas_pagas,
                'a_receber': a_receber,
                'despesas': total_despesas,
                'lucro': total_receitas - total_despesas
            },
            'lancamentos': sorted(lancamentos, key=lambda x: x['data'], reverse=True),
            'categorias': categorias,
            'periodo': {
                'inicio': primeiro_dia_mes.strftime('%d/%m/%Y'),
                'fim': today.strftime('%d/%m/%Y')
            }
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/financeiro/receitas
# Listar receitas
# ════════════════════════════════════════════════════════════
@financeiro_bp.route('/receitas', methods=['GET'])
@jwt_required()
def listar_receitas():
    try:
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Receita.query
        
        if status:
            query = query.filter_by(status=status)
        
        if data_inicio and data_fim:
            query = query.filter(
                Receita.data_receita >= datetime.fromisoformat(data_inicio),
                Receita.data_receita <= datetime.fromisoformat(data_fim)
            )
        
        receitas = query.order_by(Receita.data_receita.desc()).all()
        
        return jsonify({
            'sucesso': True,
            'receitas': [r.to_dict() for r in receitas]
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# POST /api/financeiro/receitas
# Criar receita
# ════════════════════════════════════════════════════════════
@financeiro_bp.route('/receitas', methods=['POST'])
@jwt_required()
def criar_receita():
    try:
        dados = request.get_json()
        
        receita = Receita(
            id_consulta=dados.get('id_consulta'),
            id_paciente=dados.get('id_paciente'),
            id_medico=dados.get('id_medico'),
            descricao=dados.get('descricao'),
            valor=dados.get('valor'),
            tipo=dados.get('tipo', 'Particular'),
            conveniio=dados.get('conveniio'),
            status=dados.get('status', 'PENDENTE')
        )
        
        db.session.add(receita)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Receita criada com sucesso',
            'id': receita.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/financeiro/despesas
# Listar despesas
# ════════════════════════════════════════════════════════════
@financeiro_bp.route('/despesas', methods=['GET'])
@jwt_required()
def listar_despesas():
    try:
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Despesa.query
        
        if status:
            query = query.filter_by(status=status)
        
        if data_inicio and data_fim:
            query = query.filter(
                Despesa.data_despesa >= datetime.fromisoformat(data_inicio),
                Despesa.data_despesa <= datetime.fromisoformat(data_fim)
            )
        
        despesas = query.order_by(Despesa.data_despesa.desc()).all()
        
        return jsonify({
            'sucesso': True,
            'despesas': [d.to_dict() for d in despesas]
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# POST /api/financeiro/despesas
# Criar despesa
# ════════════════════════════════════════════════════════════
@financeiro_bp.route('/despesas', methods=['POST'])
@jwt_required()
def criar_despesa():
    try:
        dados = request.get_json()
        
        despesa = Despesa(
            descricao=dados.get('descricao'),
            valor=dados.get('valor'),
            categoria=dados.get('categoria'),
            tipo=dados.get('tipo', 'FIXA'),
            status=dados.get('status', 'PENDENTE')
        )
        
        db.session.add(despesa)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Despesa criada com sucesso',
            'id': despesa.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
