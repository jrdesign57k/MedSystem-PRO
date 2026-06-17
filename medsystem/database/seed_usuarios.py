"""
Usuários de demonstração — um médico por especialidade + 2 recepcionistas.
Idempotente: cria contas faltantes e corrige vínculo médico ↔ especialidade por nome.
"""
from extensions import db
from models import Usuario, Medico, Especialidade

SENHA_DEMO = 'MedSystem12#'

# (nome da especialidade no banco, e-mail, nome completo, CRM)
MEDICOS_POR_ESPECIALIDADE = [
    ('Clínica Geral', 'drcarlos@medsystem.com', 'Dr. Carlos Mendonça', 'SP123456'),
    ('Cardiologia', 'drcardio@medsystem.com', 'Dr. Roberto Cardoso', 'SP111111'),
    ('Dermatologia', 'drderma@medsystem.com', 'Dra. Juliana Costa', 'SP222221'),
    ('Pediatria', 'drpediatria@medsystem.com', 'Dra. Fernanda Lima', 'SP222222'),
    ('Ginecologia', 'drgineco@medsystem.com', 'Dra. Patrícia Souza', 'SP333333'),
    ('Ortopedia', 'drortopedia@medsystem.com', 'Dr. Marcos Alves', 'SP444444'),
    ('Neurologia', 'drneuro@medsystem.com', 'Dr. André Vieira', 'SP555555'),
    ('Oftalmologia', 'droftalmo@medsystem.com', 'Dra. Laura Martins', 'SP666666'),
    ('Psiquiatria', 'drpsiquiatria@medsystem.com', 'Dr. Rafael Mendes', 'SP888888'),
]

RECEPCAO_DEMO = [
    {'email': 'recepcao@medsystem.com', 'nome': 'Ana Recepção'},
    {'email': 'recepcao2@medsystem.com', 'nome': 'Bruno Recepção'},
]

# Conta criada com mapeamento antigo por ID — reaproveita para Psiquiatria se ainda existir.
LEGADO_EMAIL_PSQ = 'drcirurgia@medsystem.com'


def _especialidade_por_nome(nome):
    esp = Especialidade.query.filter_by(nome=nome).first()
    if esp:
        return esp
    return Especialidade.query.filter(Especialidade.nome.ilike(nome)).first()


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


def _migrar_legado_psiquiatria():
    """Move drcirurgia@ (seed antigo) para Psiquiatria ou remove duplicata."""
    legado = Usuario.query.filter_by(email=LEGADO_EMAIL_PSQ).first()
    if not legado:
        return

    psiq = _especialidade_por_nome('Psiquiatria')
    novo = Usuario.query.filter_by(email='drpsiquiatria@medsystem.com').first()
    if novo or not psiq:
        med = Medico.query.filter_by(id_usuario=legado.id).first()
        if med:
            db.session.delete(med)
        db.session.delete(legado)
        return

    legado.nome = 'Dr. Rafael Mendes'
    legado.email = 'drpsiquiatria@medsystem.com'
    med = Medico.query.filter_by(id_usuario=legado.id).first()
    if med:
        med.id_especialidade = psiq.id
        med.crm = 'SP888888'


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

    _migrar_legado_psiquiatria()

    for dados in RECEPCAO_DEMO:
        if _criar_recepcao(dados):
            criados += 1

    db.session.commit()
    if criados:
        print(f'[OK] {criados} usuario(s) demo criado(s)')
    return criados
