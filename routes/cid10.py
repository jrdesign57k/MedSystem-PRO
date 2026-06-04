"""
MedSystem CID-10 Routes - Búsqueda de diagnósticos ICD-10
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models import CID10

cid10_bp = Blueprint('cid10', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/cid10/busca
# Buscar CID-10 por código ou descrição
# ════════════════════════════════════════════════════════════
@cid10_bp.route('/busca', methods=['GET'])
@jwt_required()
def buscar_cid10():
    try:
        query = request.args.get('q', '').lower()
        
        if not query or len(query) < 2:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Digite pelo menos 2 caracteres para buscar'
            }), 400
        
        # Buscar por código ou descrição
        resultados = CID10.query.filter(
            db.or_(
                CID10.codigo.ilike(f'%{query}%'),
                CID10.descricao.ilike(f'%{query}%')
            )
        ).limit(20).all()
        
        return jsonify({
            'sucesso': True,
            'total': len(resultados),
            'cids': [r.to_dict() for r in resultados]
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/cid10/:codigo
# Obter detalhes de um CID-10
# ════════════════════════════════════════════════════════════
@cid10_bp.route('/<codigo>', methods=['GET'])
@jwt_required()
def obter_cid10(codigo):
    try:
        cid = CID10.query.filter_by(codigo=codigo).first()
        
        if not cid:
            return jsonify({
                'sucesso': False,
                'erro': 'CID-10 não encontrado'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'cid': cid.to_dict()
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/cid10
# Listar todos os CID-10
# ════════════════════════════════════════════════════════════
@cid10_bp.route('', methods=['GET'])
@jwt_required()
def listar_cid10():
    try:
        categoria = request.args.get('categoria')
        pagina = request.args.get('pagina', 1, type=int)
        
        query = CID10.query
        
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        cids = query.paginate(page=pagina, per_page=50)
        
        return jsonify({
            'sucesso': True,
            'total': cids.total,
            'pagina': pagina,
            'paginas': cids.pages,
            'cids': [c.to_dict() for c in cids.items]
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
