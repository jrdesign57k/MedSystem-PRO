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
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False) # <-- CORRIGIDO AQUI
    id_tipo_exame = db.Column(db.Integer, db.ForeignKey('tipos_exame.id'), nullable=False)
    resultado = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='SOLICITADO')

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'id_tipo_exame': self.id_tipo_exame,
            'resultado': self.resultado,
            'status': self.status
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
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False) # <-- CORRIGIDO AQUI
    cid = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    gravidade = db.Column(db.String(20))

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'cid': self.cid,
            'descricao': self.descricao,
            'gravidade': self.gravidade
        }
    
    # ════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════
# PRESCRIÇÃO
# ════════════════════════════════════════════════════════════
class Prescricao(db.Model):
    __tablename__ = 'prescricoes'
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False)
    medicamento = db.Column(db.String(150), nullable=False)
    posologia = db.Column(db.Text, nullable=False)
    data_prescricao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'medicamento': self.medicamento,
            'posologia': self.posologia
        }