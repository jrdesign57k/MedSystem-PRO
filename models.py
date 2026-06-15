from datetime import datetime
from extensions import db, bcrypt

# ════════════════════════════════════════════════════════════
# USUÁRIO
# ════════════════════════════════════════════════════════════
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'medico', 'admin', etc.
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    medico = db.relationship('Medico', backref='usuario', uselist=False)

    def set_senha(self, senha):
        self.senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

    def verificar_senha(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

# ════════════════════════════════════════════════════════════
# MÉDICO E ESPECIALIDADE
# ════════════════════════════════════════════════════════════
class Especialidade(db.Model):
    __tablename__ = 'especialidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    medicos = db.relationship('Medico', backref='especialidade', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class Medico(db.Model):
    __tablename__ = 'medicos'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    crm = db.Column(db.String(20), unique=True, nullable=False)
    id_especialidade = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'crm': self.crm,
            'id_usuario': self.id_usuario,
            'id_especialidade': self.id_especialidade,
            'nome': self.usuario.nome if self.usuario else "Desconhecido"
        }

# ════════════════════════════════════════════════════════════
# LOG DE AUDITORIA
# ════════════════════════════════════════════════════════════
class LogAuditoria(db.Model):
    __tablename__ = 'logs_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    tabela = db.Column(db.String(100))
    operacao = db.Column(db.String(20))
    id_registro = db.Column(db.Integer)
    detalhe = db.Column(db.Text)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

# ════════════════════════════════════════════════════════════
# PACIENTE (Alinhado perfeitamente com a estrutura do MySQL)
# ════════════════════════════════════════════════════════════
class Paciente(db.Model):
    __tablename__ = 'paciente'  # No singular
    
    id_paciente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    tipo_sanguineo = db.Column(db.String(5), nullable=True)
    alergias = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Novos campos - Dados Pessoais
    naturalidade = db.Column(db.String(100), nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    profissao = db.Column(db.String(100), nullable=True)
    empresa = db.Column(db.String(100), nullable=True)
    rg = db.Column(db.String(20), nullable=True)
    mae = db.Column(db.String(150), nullable=True)
    responsavel = db.Column(db.String(150), nullable=True)
    
    # Novos campos - Endereço Detalhado
    logradouro = db.Column(db.String(150), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    uf = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(9), nullable=True)
    
    # Novos campos - Contato de Emergência
    emergencia_nome = db.Column(db.String(150), nullable=True)
    emergencia_telefone = db.Column(db.String(20), nullable=True)
    
    # Novos campos - Informações Médicas Vitais
    peso = db.Column(db.Float, nullable=True)
    altura = db.Column(db.Integer, nullable=True)
    pressao = db.Column(db.String(10), nullable=True)
    frequencia_cardiaca = db.Column(db.Integer, nullable=True)
    
    # Novos campos - Histórico Médico
    historico_familiar = db.Column(db.Text, nullable=True)
    medicamentos = db.Column(db.Text, nullable=True)
    cirurgias = db.Column(db.Text, nullable=True)
    
    # Novos campos - Hábitos
    tabagismo = db.Column(db.String(50), nullable=True)
    alcoolismo = db.Column(db.String(50), nullable=True)
    atividade_fisica = db.Column(db.String(50), nullable=True)
    
    # Observações clínicas (renomeado de observacoes)
    observacoes_clinicas = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id_paciente,
            'cpf': self.cpf,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'sexo': self.sexo,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'tipo_sanguineo': self.tipo_sanguineo,
            'alergias': self.alergias,
            'observacoes': self.observacoes,
            'naturalidade': self.naturalidade,
            'estado_civil': self.estado_civil,
            'profissao': self.profissao,
            'empresa': self.empresa,
            'rg': self.rg,
            'mae': self.mae,
            'responsavel': self.responsavel,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf,
            'cep': self.cep,
            'emergencia_nome': self.emergencia_nome,
            'emergencia_telefone': self.emergencia_telefone,
            'peso': self.peso,
            'altura': self.altura,
            'pressao': self.pressao,
            'frequencia_cardiaca': self.frequencia_cardiaca,
            'historico_familiar': self.historico_familiar,
            'medicamentos': self.medicamentos,
            'cirurgias': self.cirurgias,
            'tabagismo': self.tabagismo,
            'alcoolismo': self.alcoolismo,
            'atividade_fisica': self.atividade_fisica,
            'observacoes_clinicas': self.observacoes_clinicas,
            'ativo': self.ativo
        }

# ════════════════════════════════════════════════════════════
# CONSULTA
# ════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════
# CONSULTA (Corrigido para id_consulta para casar com seu MySQL)
# ════════════════════════════════════════════════════════════
class Consulta(db.Model):
    __tablename__ = 'consulta'  # No singular, como está no banco
    
    id_consulta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    data_consulta = db.Column(db.DateTime, nullable=False)
    hora_consulta = db.Column(db.String(5), nullable=True)  # Formato HH:MM
    status = db.Column(db.String(20), default='AGENDADA')
    motivo = db.Column(db.String(255), nullable=True)
    
    # Campos de Prontuário expandido
    queixa_principal = db.Column(db.Text, nullable=True)
    historia_molestia_atual = db.Column(db.Text, nullable=True)
    antecedentes_pessoais = db.Column(db.Text, nullable=True)
    antecedentes_familiares = db.Column(db.Text, nullable=True)
    exame_fisico = db.Column(db.Text, nullable=True)
    hipotese_diagnostica = db.Column(db.Text, nullable=True)
    plano_terapeutico = db.Column(db.Text, nullable=True)
    observacoes_consulta = db.Column(db.Text, nullable=True)
    tipo_consulta = db.Column(db.String(50), nullable=True)  # '1ª Consulta', 'Retorno', 'Urgência'
    convenio = db.Column(db.String(100), nullable=True)
    
    # Relações
    paciente = db.relationship('Paciente', backref='consultas')
    medico = db.relationship('Medico', backref='consultas')

    def to_dict(self):
        return {
            'id': self.id_consulta,
            'id_paciente': self.id_paciente,
            'id_medico': self.id_medico,
            'data_consulta': self.data_consulta.isoformat() if self.data_consulta else None,
            'hora_consulta': self.hora_consulta,
            'status': self.status,
            'motivo': self.motivo,
            'paciente': {
                'id': self.paciente.id_paciente,
                'nome': self.paciente.nome
            } if self.paciente else {},
            'medico': {
                'id': self.medico.id,
                'nome': self.medico.usuario.nome if self.medico and self.medico.usuario else 'Desconhecido'
            } if self.medico else {}
        }

# ════════════════════════════════════════════════════════════
# EXAMES E TIPOS DE EXAME (Apontando para consulta.id_consulta)
# ════════════════════════════════════════════════════════════
class TipoExame(db.Model):
    __tablename__ = 'tipos_exame'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Caso seu MySQL use 'nome', mude para nome

class Exame(db.Model):
    __tablename__ = 'exames'
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    id_tipo_exame = db.Column(db.Integer, db.ForeignKey('tipos_exame.id'), nullable=False)
    nome_exame = db.Column(db.String(200), nullable=True)
    resultado = db.Column(db.Text, nullable=True)
    laudo = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='SOLICITADO')  # SOLICITADO, AGUARDANDO, EM_ANÁLISE, DISPONÍVEL
    prioridade = db.Column(db.String(20), default='NORMAL')  # URGENTE, NORMAL, BAIXA
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_resultado = db.Column(db.DateTime, nullable=True)
    
    # Relações
    consulta = db.relationship('Consulta')
    paciente = db.relationship('Paciente')
    medico = db.relationship('Medico')

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'id_paciente': self.id_paciente,
            'id_medico': self.id_medico,
            'id_tipo_exame': self.id_tipo_exame,
            'nome_exame': self.nome_exame,
            'resultado': self.resultado,
            'laudo': self.laudo,
            'status': self.status,
            'prioridade': self.prioridade,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'data_resultado': self.data_resultado.isoformat() if self.data_resultado else None
        }

# ════════════════════════════════════════════════════════════
# SINAIS VITAIS (Apontando para consulta.id_consulta)
# ════════════════════════════════════════════════════════════
class SinalVital(db.Model):
    __tablename__ = 'sinais_vitais'
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False) # <-- CORRIGIDO AQUI
    pressao_arterial = db.Column(db.String(20))
    frequencia_cardiaca = db.Column(db.Integer)
    saturacao_oxigenio = db.Column(db.Integer)
    temperatura = db.Column(db.Float)
    imc = db.Column(db.Float)
    peso = db.Column(db.Float)
    altura = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'pressao_arterial': self.pressao_arterial,
            'frequencia_cardiaca': self.frequencia_cardiaca,
            'saturacao_oxigenio': self.saturacao_oxigenio,
            'temperatura': self.temperatura,
            'imc': self.imc,
            'peso': self.peso,
            'altura': self.altura
        }

# ════════════════════════════════════════════════════════════
# DIAGNÓSTICOS (Apontando para consulta.id_consulta)
# ════════════════════════════════════════════════════════════
class Diagnostico(db.Model):
    __tablename__ = 'diagnosticos'
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    cid = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    gravidade = db.Column(db.String(20), nullable=True)  # Leve, Moderada, Grave
    status = db.Column(db.String(20), default='ATIVO')
    data_diagnostico = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    consulta = db.relationship('Consulta')
    paciente = db.relationship('Paciente')
    medico = db.relationship('Medico')

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'id_paciente': self.id_paciente,
            'id_medico': self.id_medico,
            'cid': self.cid,
            'descricao': self.descricao,
            'gravidade': self.gravidade,
            'status': self.status,
            'data_diagnostico': self.data_diagnostico.isoformat() if self.data_diagnostico else None
        }
# ════════════════════════════════════════════════════════════
# PRESCRIÇÃO
# ════════════════════════════════════════════════════════════
class Prescricao(db.Model):
    __tablename__ = 'prescricoes'
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    medicamento = db.Column(db.String(150), nullable=False)
    dosagem = db.Column(db.String(100), nullable=True)
    posologia = db.Column(db.Text, nullable=False)
    frequencia = db.Column(db.String(100), nullable=True)
    duracao = db.Column(db.String(100), nullable=True)
    quantidade = db.Column(db.Integer, nullable=True)
    tipo_receita = db.Column(db.String(50), nullable=True)  # 'Simples', 'Controlada Azul', 'Controlada Amarela'
    orientacoes = db.Column(db.Text, nullable=True)
    data_prescricao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='ATIVA')
    
    # Relações
    consulta = db.relationship('Consulta')
    medico = db.relationship('Medico')
    paciente = db.relationship('Paciente')

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'id_medico': self.id_medico,
            'id_paciente': self.id_paciente,
            'medicamento': self.medicamento,
            'dosagem': self.dosagem,
            'posologia': self.posologia,
            'frequencia': self.frequencia,
            'duracao': self.duracao,
            'quantidade': self.quantidade,
            'tipo_receita': self.tipo_receita,
            'orientacoes': self.orientacoes,
            'data_prescricao': self.data_prescricao.isoformat() if self.data_prescricao else None,
            'status': self.status
        }

# ════════════════════════════════════════════════════════════
# CID-10 (Referência de Diagnósticos)
# ════════════════════════════════════════════════════════════
class CID10(db.Model):
    __tablename__ = 'cid10'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(100), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'categoria': self.categoria
        }

# ════════════════════════════════════════════════════════════
# GESTÃO FINANCEIRA - RECEITAS
# ════════════════════════════════════════════════════════════
class Receita(db.Model):
    __tablename__ = 'receitas'
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'Particular', 'Convênio', etc
    convenio = db.Column(db.String(100), nullable=True)
    data_receita = db.Column(db.DateTime, default=datetime.utcnow)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, PAGO, CANCELADO
    
    # Relações
    consulta = db.relationship('Consulta')
    paciente = db.relationship('Paciente')
    medico = db.relationship('Medico')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'id_paciente': self.id_paciente,
            'id_medico': self.id_medico,
            'descricao': self.descricao,
            'valor': self.valor,
            'tipo': self.tipo,
            'convenio': self.convenio,
            'data_receita': self.data_receita.isoformat() if self.data_receita else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'status': self.status
        }

# ════════════════════════════════════════════════════════════
# GESTÃO FINANCEIRA - DESPESAS
# ════════════════════════════════════════════════════════════
class Despesa(db.Model):
    __tablename__ = 'despesas'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100), nullable=True)  # Aluguel, Material, Salário, etc
    tipo = db.Column(db.String(50), default='FIXA')  # FIXA, VARIÁVEL
    data_despesa = db.Column(db.DateTime, default=datetime.utcnow)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, PAGO, CANCELADO
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'categoria': self.categoria,
            'tipo': self.tipo,
            'data_despesa': self.data_despesa.isoformat() if self.data_despesa else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'status': self.status
        }

# ════════════════════════════════════════════════════════════
# MENSAGENS INTERNAS
# ════════════════════════════════════════════════════════════
class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, primary_key=True)
    id_remetente = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_destinatario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    assunto = db.Column(db.String(255), nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    lida = db.Column(db.Boolean, default=False)
    
    # Relações
    remetente = db.relationship('Usuario', foreign_keys=[id_remetente])
    destinatario = db.relationship('Usuario', foreign_keys=[id_destinatario])
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_remetente': self.id_remetente,
            'id_destinatario': self.id_destinatario,
            'assunto': self.assunto,
            'conteudo': self.conteudo,
            'data_envio': self.data_envio.isoformat() if self.data_envio else None,
            'lida': self.lida,
            'remetente': self.remetente.nome if self.remetente else None,
            'destinatario': self.destinatario.nome if self.destinatario else None
        }

# ════════════════════════════════════════════════════════════
# CONTATO DE EMERGÊNCIA
# ════════════════════════════════════════════════════════════
class ContatoEmergencia(db.Model):
    __tablename__ = 'contatos_emergencia'
    id = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    parentesco = db.Column(db.String(50), nullable=True)
    
    # Relação
    paciente = db.relationship('Paciente')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_paciente': self.id_paciente,
            'nome': self.nome,
            'telefone': self.telefone,
            'parentesco': self.parentesco
        }