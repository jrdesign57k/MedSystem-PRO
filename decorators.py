"""
MedSystem Decorators - Verificação de Roles e Permissões
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import Usuario

def role_required(*roles):
    """
    Decorator para verificar se o usuário tem um dos roles permitidos
    
    Uso:
    @role_required('admin', 'medico')
    def funcao():
        pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                user_id = get_jwt_identity()
                usuario = Usuario.query.get(user_id)
                
                if not usuario:
                    return jsonify({
                        'sucesso': False,
                        'mensagem': 'Usuário não encontrado'
                    }), 404
                
                if usuario.tipo not in roles:
                    return jsonify({
                        'sucesso': False,
                        'mensagem': f'Acesso negado. Roles permitidos: {", ".join(roles)}'
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'sucesso': False,
                    'mensagem': f'Erro na verificação de permissão: {str(e)}'
                }), 500
        
        return wrapper
    return decorator

def admin_required(fn):
    """Requer que o usuário seja admin"""
    return role_required('admin')(fn)

def medico_required(fn):
    """Requer que o usuário seja médico"""
    return role_required('medico')(fn)

def recepcao_required(fn):
    """Requer que o usuário seja da recepção"""
    return role_required('recepcao')(fn)
