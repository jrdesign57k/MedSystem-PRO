"""Helpers para notificações do portal do paciente."""
from extensions import db
from models import NotificacaoPaciente


def criar_notificacao_paciente(id_paciente, tipo, titulo, mensagem, id_referencia=None):
    notif = NotificacaoPaciente(
        id_paciente=id_paciente,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        id_referencia=id_referencia,
        lida=False,
    )
    db.session.add(notif)
    return notif
