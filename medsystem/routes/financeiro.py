"""
MedSystem Financeiro Routes - Receitas, despesas, preços e faturamento
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Receita, Despesa, PrecoConsulta
from decorators import admin_required
from datetime import datetime
from sqlalchemy import func

financeiro_bp = Blueprint('financeiro', __name__)

TIPOS_CONSULTA = ['1ª Consulta', 'Retorno', 'Urgência']


def buscar_preco_consulta(tipo_consulta, convenio=None):
    return PrecoConsulta.buscar(tipo_consulta, convenio)


@financeiro_bp.route('', methods=['GET'])
@jwt_required()
def obter_financeiro():
    try:
        today = datetime.utcnow()
        primeiro_dia_mes = today.replace(day=1)

        total_receitas = db.session.query(func.sum(Receita.valor)).filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes
        ).scalar() or 0

        receitas_pagas = Receita.query.filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes,
            Receita.status == 'PAGO'
        ).count()

        a_receber = db.session.query(func.sum(Receita.valor)).filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes,
            Receita.status == 'PENDENTE'
        ).scalar() or 0

        total_despesas = db.session.query(func.sum(Despesa.valor)).filter(
            func.date(Despesa.data_despesa) >= primeiro_dia_mes
        ).scalar() or 0

        lancamentos = []
        for r in Receita.query.filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes
        ).order_by(Receita.data_receita.desc()).limit(5).all():
            lancamentos.append({
                'data': r.data_receita.strftime('%d/%m'),
                'descricao': r.descricao,
                'tipo': 'Entrada',
                'valor': r.valor,
                'status': r.status
            })

        for d in Despesa.query.filter(
            func.date(Despesa.data_despesa) >= primeiro_dia_mes
        ).order_by(Despesa.data_despesa.desc()).limit(5).all():
            lancamentos.append({
                'data': d.data_despesa.strftime('%d/%m'),
                'descricao': d.descricao,
                'tipo': 'Saída',
                'valor': -d.valor,
                'status': d.status
            })

        categorias = []
        for tipo, valor in db.session.query(
            Receita.tipo, func.sum(Receita.valor)
        ).filter(
            func.date(Receita.data_receita) >= primeiro_dia_mes
        ).group_by(Receita.tipo).all():
            categorias.append({'nome': tipo or 'Particular', 'valor': valor or 0})

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


@financeiro_bp.route('/precos', methods=['GET'])
@jwt_required()
def listar_precos():
    try:
        modalidade = request.args.get('modalidade')
        query = PrecoConsulta.query.filter_by(ativo=True)
        if modalidade:
            query = query.filter_by(modalidade=modalidade)
        precos = query.order_by(PrecoConsulta.modalidade, PrecoConsulta.tipo_consulta).all()
        return jsonify({
            'sucesso': True,
            'precos': [p.to_dict() for p in precos],
            'tipos_consulta': TIPOS_CONSULTA
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@financeiro_bp.route('/precos/consultar', methods=['GET'])
@jwt_required()
def consultar_preco():
    try:
        tipo = request.args.get('tipo_consulta', '1ª Consulta')
        convenio = request.args.get('convenio')
        preco = buscar_preco_consulta(tipo, convenio)
        if not preco:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Preço não cadastrado para esta combinação'
            }), 404
        return jsonify({'sucesso': True, 'preco': preco.to_dict()})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@financeiro_bp.route('/precos', methods=['POST'])
@jwt_required()
@admin_required
def criar_preco():
    try:
        dados = request.get_json() or {}
        tipo = dados.get('tipo_consulta')
        modalidade = dados.get('modalidade')
        valor = dados.get('valor')
        nome_convenio = PrecoConsulta.normalizar_convenio(dados.get('nome_convenio'))

        if not tipo or tipo not in TIPOS_CONSULTA:
            return jsonify({'sucesso': False, 'mensagem': 'Tipo de consulta inválido'}), 400
        if modalidade not in ('Particular', 'Convenio'):
            return jsonify({'sucesso': False, 'mensagem': 'Modalidade deve ser Particular ou Convenio'}), 400
        if valor is None or float(valor) <= 0:
            return jsonify({'sucesso': False, 'mensagem': 'Informe um valor maior que zero'}), 400
        if modalidade == 'Convenio' and not nome_convenio:
            return jsonify({'sucesso': False, 'mensagem': 'Nome do convênio é obrigatório'}), 400
        if modalidade == 'Particular':
            nome_convenio = None

        existente = PrecoConsulta.query.filter_by(
            tipo_consulta=tipo, modalidade=modalidade, nome_convenio=nome_convenio
        ).first()
        if existente:
            existente.valor = float(valor)
            existente.ativo = True
            db.session.commit()
            return jsonify({'sucesso': True, 'mensagem': 'Preço atualizado', 'preco': existente.to_dict()})

        preco = PrecoConsulta(
            tipo_consulta=tipo,
            modalidade=modalidade,
            nome_convenio=nome_convenio,
            valor=float(valor)
        )
        db.session.add(preco)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Preço cadastrado', 'preco': preco.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@financeiro_bp.route('/precos/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def atualizar_preco(id):
    try:
        preco = PrecoConsulta.query.get(id)
        if not preco:
            return jsonify({'sucesso': False, 'mensagem': 'Preço não encontrado'}), 404

        dados = request.get_json() or {}
        if 'valor' in dados:
            if float(dados['valor']) <= 0:
                return jsonify({'sucesso': False, 'mensagem': 'Valor inválido'}), 400
            preco.valor = float(dados['valor'])
        if 'tipo_consulta' in dados and dados['tipo_consulta'] in TIPOS_CONSULTA:
            preco.tipo_consulta = dados['tipo_consulta']
        if 'modalidade' in dados:
            preco.modalidade = dados['modalidade']
            if preco.modalidade == 'Particular':
                preco.nome_convenio = None
        if 'nome_convenio' in dados and preco.modalidade == 'Convenio':
            preco.nome_convenio = PrecoConsulta.normalizar_convenio(dados['nome_convenio'])
        if 'ativo' in dados:
            preco.ativo = bool(dados['ativo'])

        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Preço atualizado', 'preco': preco.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@financeiro_bp.route('/precos/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def excluir_preco(id):
    try:
        preco = PrecoConsulta.query.get(id)
        if not preco:
            return jsonify({'sucesso': False, 'mensagem': 'Preço não encontrado'}), 404
        preco.ativo = False
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Preço removido da tabela'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


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

        return jsonify({
            'sucesso': True,
            'receitas': [r.to_dict() for r in query.order_by(Receita.data_receita.desc()).all()]
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@financeiro_bp.route('/receitas', methods=['POST'])
@jwt_required()
def criar_receita():
    try:
        dados = request.get_json() or {}
        valor = dados.get('valor')

        if valor is None and dados.get('tipo_consulta'):
            preco = buscar_preco_consulta(dados['tipo_consulta'], dados.get('convenio'))
            if preco:
                valor = preco.valor

        receita = Receita(
            id_consulta=dados.get('id_consulta'),
            id_paciente=dados.get('id_paciente'),
            id_medico=dados.get('id_medico'),
            descricao=dados.get('descricao'),
            valor=valor,
            tipo=dados.get('tipo', 'Particular'),
            convenio=dados.get('convenio'),
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

        return jsonify({
            'sucesso': True,
            'despesas': [d.to_dict() for d in query.order_by(Despesa.data_despesa.desc()).all()]
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@financeiro_bp.route('/despesas', methods=['POST'])
@jwt_required()
def criar_despesa():
    try:
        dados = request.get_json() or {}

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
