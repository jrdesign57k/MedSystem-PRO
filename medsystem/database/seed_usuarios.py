"""
Usuários de demonstração — um médico por especialidade + 2 recepcionistas.
Idempotente: cria contas faltantes e corrige vínculo médico ↔ especialidade por nome.

Os nomes das especialidades devem coincidir com app.py (especialidades_padrao).
"""
from extensions import db
from models import Usuario, Medico, Especialidade

SENHA_DEMO = 'MedSystem12#'

# (nome exato da especialidade no banco, e-mail, nome completo, CRM)
MEDICOS_POR_ESPECIALIDADE = [
    ('Clínica Geral', 'drcarlos@medsystem.com', 'Dr. Carlos Mendonça', 'SP123456'),
    ('Cardiologia', 'drcardio@medsystem.com', 'Dr. Roberto Cardoso', 'SP111111'),
    ('Pediatria', 'drpediatria@medsystem.com', 'Dra. Fernanda Lima', 'SP222222'),
    ('Ginecologia e Obstetrícia', 'drgineco@medsystem.com', 'Dra. Patrícia Souza', 'SP333333'),
    ('Ortopedia', 'drortopedia@medsystem.com', 'Dr. Marcos Alves', 'SP444444'),
    ('Neurologia', 'drneuro@medsystem.com', 'Dr. André Vieira', 'SP555555'),
    ('Oftalmologia', 'droftalmo@medsystem.com', 'Dra. Laura Martins', 'SP666666'),
    ('Cirurgia Geral', 'drcirurgia@medsystem.com', 'Dr. Paulo Ribeiro', 'SP777777'),
]

RECEPCAO_DEMO = [
    {'email': 'recepcao@medsystem.com', 'nome': 'Ana Recepção'},
    {'email': 'recepcao2@medsystem.com', 'nome': 'Bruno Recepção'},
]


def _especialidade_por_nome(nome):
    esp = Especialidade.query.filter_by(nome=nome).first()
    if esp:
        return esp
    esp = Especialidade.query.filter(Especialidade.nome.ilike(nome)).first()
    if esp:
        return esp
    return Especialidade.query.filter(Especialidade.nome.ilike(f'%{nome}%')).first()


def _garantir_medico(nome_esp, email, nome, crm):
    esp = _especialidade_por_nome(nome_esp)
    if not esp:
        print(f'[AVISO] Especialidade "{nome_esp}" nao encontrada — pulando {email}')
        return False

    user = Usuario.query.filter_by(email=email).first()
    if user:
        med = Medico.query.filter_by(id_usuario=user.id).first()
        if med and med.id_especialidade != esp.id:
            med.id_especialidade = esp.id
        return False

    user = Usuario(nome=nome, email=email, tipo='medico', ativo=True)
    user.set_senha(SENHA_DEMO)
    db.session.add(user)
    db.session.flush()

    db.session.add(Medico(id_usuario=user.id, crm=crm, id_especialidade=esp.id))
    return True


def _criar_recepcao(dados):
    if Usuario.query.filter_by(email=dados['email']).first():
        return False

    user = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        tipo='recepcao',
        ativo=True,
    )
    user.set_senha(SENHA_DEMO)
    db.session.add(user)
    return True


def seed_usuarios_demo():
    """Garante 1 médico por especialidade cadastrada no banco + 2 recepcionistas."""
    criados = 0

    for nome_esp, email, nome, crm in MEDICOS_POR_ESPECIALIDADE:
        if _garantir_medico(nome_esp, email, nome, crm):
            criados += 1

    for dados in RECEPCAO_DEMO:
        if _criar_recepcao(dados):
            criados += 1

    db.session.commit()
    if criados:
        print(f'[OK] {criados} usuario(s) demo criado(s)')
    return criados
