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

    def to_dict(self):
        return {
            'id': self.id_paciente,  # O frontend consome como 'id'
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
    
    id_consulta = db.Column(db.Integer, primary_key=True, autoincrement=True) # <-- CORRIGIDO AQUI
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    data_consulta = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='AGENDADA')

    def to_dict(self):
        return {
            'id': self.id_consulta,  # O JS continua lendo 'id' sem quebrar o front
            'id_paciente': self.id_paciente,
            'id_medico': self.id_medico,
            'data_consulta': self.data_consulta.isoformat() if self.data_consulta else None,
            'status': self.status
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