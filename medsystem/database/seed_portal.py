"""
Portal do paciente — contas de login vinculadas a pacientes demo + notificações.
Idempotente.
"""
from datetime import datetime, timedelta
from extensions import db
from models import Usuario, Paciente, Exame, NotificacaoPaciente
from medsystem.utils.notificacoes_paciente import criar_notificacao_paciente

SENHA_DEMO = 'MedSystem12#'

# (CPF do paciente no seed, e-mail de login portal, nome exibido no usuário)
PACIENTES_PORTAL = [
    ('52998224725', 'paciente.carlos@medsystem.com', 'Carlos Alberto Silva'),
    ('39053344705', 'paciente.maria@medsystem.com', 'Maria Oliveira'),
]


def _vincular_paciente(cpf, email, nome):
    pac = Paciente.query.filter_by(cpf=cpf).first()
    if not pac:
        return False

    user = Usuario.query.filter_by(email=email).first()
    if not user:
        user = Usuario(nome=nome, email=email, tipo='paciente', ativo=True)
        user.set_senha(SENHA_DEMO)
        db.session.add(user)
        db.session.flush()

    if pac.id_usuario != user.id:
        pac.id_usuario = user.id
    return True


def seed_portal_pacientes():
    """Cria logins de paciente, vincula ao cadastro e insere notificações demo."""
    criados = 0
    for cpf, email, nome in PACIENTES_PORTAL:
        if _vincular_paciente(cpf, email, nome):
            criados += 1

    if criados:
        db.session.commit()
        print(f'[OK] {criados} login(s) de paciente (portal) vinculado(s)')

    _seed_notificacoes_demo()
    return criados


def _seed_notificacoes_demo():
    if NotificacaoPaciente.query.first():
        return False

    carlos = Paciente.query.filter_by(cpf='52998224725').first()
    if not carlos:
        return False

    medico = Usuario.query.filter_by(email='drcarlos@medsystem.com').first()
    medico_nome = medico.nome if medico else 'Dr. Carlos Mendonça'

    exame = Exame.query.filter_by(id_paciente=carlos.id_paciente, nome_exame='Hemograma completo').first()
    if exame:
        exame.status = 'DISPONÍVEL'
        exame.resultado = 'Hemoglobina 14,2 g/dL · Leucócitos 7.800/mm³ · Plaquetas 245.000/mm³'
        exame.laudo = 'Hemograma dentro dos limites de referência para o perfil do paciente.'
        exame.data_resultado = datetime.utcnow() - timedelta(hours=1)

    criar_notificacao_paciente(
        carlos.id_paciente,
        'exame',
        'Resultado disponível: Hemograma completo',
        'Seu hemograma já está disponível para consulta em Meus Exames.',
        id_referencia=exame.id if exame else None,
    )
    criar_notificacao_paciente(
        carlos.id_paciente,
        'recado',
        f'Recado do {medico_nome}',
        'Carlos, compareça na recepção após a consulta para retirar a orientação sobre repouso e medicação.',
    )
    criar_notificacao_paciente(
        carlos.id_paciente,
        'consulta',
        'Consulta em andamento',
        'Sua consulta de hoje foi registrada. O prontuário será atualizado pelo médico responsável.',
    )

    db.session.commit()
    print('[OK] Notificacoes demo do portal do paciente inseridas')
    return True
