USE master;
GO

-- 1. RECRIAÇÃO DO BANCO
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'medSystem')
BEGIN
    ALTER DATABASE medSystem SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE medSystem;
END
GO
CREATE DATABASE medSystem;
GO
USE medSystem;
GO

-- 2. TABELAS (Estrutura do seu sistema novo adaptada para SQL Server)
CREATE TABLE especialidade (
    id_especialidade  INT IDENTITY(1,1) PRIMARY KEY,
    nome              VARCHAR(100) NOT NULL UNIQUE,
    descricao         VARCHAR(255)
);

CREATE TABLE medico (
    id_medico         INT IDENTITY(1,1) PRIMARY KEY,
    crm               VARCHAR(20) NOT NULL UNIQUE,
    nome              VARCHAR(150) NOT NULL,
    id_especialidade  INT NOT NULL REFERENCES especialidade(id_especialidade),
    telefone          VARCHAR(20),
    email             VARCHAR(150),
    ativo             BIT NOT NULL DEFAULT 1
);

CREATE TABLE paciente (
    id_paciente       INT IDENTITY(1,1) PRIMARY KEY,
    cpf               VARCHAR(14) NOT NULL UNIQUE,
    nome              VARCHAR(150) NOT NULL,
    data_nascimento   DATE NOT NULL,
    sexo              CHAR(1) CHECK (sexo IN ('M','F','O')),
    telefone          VARCHAR(20),
    email             VARCHAR(150),
    endereco          VARCHAR(255),
    tipo_sanguineo    VARCHAR(5),
    alergias          VARCHAR(MAX),
    observacoes       VARCHAR(MAX),
    data_cadastro     DATETIME DEFAULT GETDATE(),
    ativo             BIT NOT NULL DEFAULT 1
);

CREATE TABLE consulta (
    id_consulta       INT IDENTITY(1,1) PRIMARY KEY,
    id_paciente       INT NOT NULL REFERENCES paciente(id_paciente),
    id_medico         INT NOT NULL REFERENCES medico(id_medico),
    data_consulta     DATETIME NOT NULL,
    motivo            VARCHAR(MAX),
    status            VARCHAR(20) DEFAULT 'agendada' CHECK (status IN ('agendada','em_andamento','concluida','cancelada'))
);

CREATE TABLE tipo_exame (
    id_tipo_exame     INT IDENTITY(1,1) PRIMARY KEY,
    nome              VARCHAR(100) NOT NULL,
    descricao         VARCHAR(255),
    valor_referencia  VARCHAR(100)
);

CREATE TABLE exame (
    id_exame          INT IDENTITY(1,1) PRIMARY KEY,
    id_consulta       INT NOT NULL REFERENCES consulta(id_consulta),
    id_tipo_exame     INT NOT NULL REFERENCES tipo_exame(id_tipo_exame),
    data_solicitacao  DATE NOT NULL,
    data_resultado    DATE,
    resultado         VARCHAR(MAX),
    status            VARCHAR(20) DEFAULT 'solicitado' CHECK (status IN ('solicitado','em_analise','concluido')),
    laboratorio       VARCHAR(150)
);

CREATE TABLE diagnostico (
    id_diagnostico    INT IDENTITY(1,1) PRIMARY KEY,
    id_consulta       INT NOT NULL REFERENCES consulta(id_consulta),
    cid10             VARCHAR(10),
    descricao         VARCHAR(MAX) NOT NULL,
    gravidade         VARCHAR(20) DEFAULT 'leve' CHECK (gravidade IN ('leve','moderada','grave','critica')),
    data_diagnostico  DATETIME DEFAULT GETDATE()
);

CREATE TABLE prescricao (
    id_prescricao     INT IDENTITY(1,1) PRIMARY KEY,
    id_consulta       INT NOT NULL REFERENCES consulta(id_consulta),
    medicamento       VARCHAR(150) NOT NULL,
    dosagem           VARCHAR(100),
    frequencia        VARCHAR(100),
    duracao           VARCHAR(100),
    instrucoes        VARCHAR(MAX)
);

CREATE TABLE sinal_vital (
    id_sinal           INT IDENTITY(1,1) PRIMARY KEY,
    id_consulta        INT NOT NULL REFERENCES consulta(id_consulta),
    pressao_sistolica  INT,
    pressao_diastolica INT,
    frequencia_cardiaca INT,
    temperatura        DECIMAL(4,1),
    saturacao_o2       DECIMAL(5,2),
    peso_kg            DECIMAL(6,2),
    altura_cm          DECIMAL(6,2),
    glicemia           DECIMAL(6,2),
    data_registro      DATETIME DEFAULT GETDATE()
);

-- 3. ÍNDICES (Para Performance)
CREATE INDEX idx_paciente_cpf ON paciente(cpf);
CREATE INDEX idx_consulta_data ON consulta(data_consulta);
GO

-- 4. VIEW DASHBOARD (O "cérebro" do seu front-end)
CREATE OR ALTER VIEW vw_dashboard_consultas AS
SELECT 
    c.id_consulta, p.nome AS paciente, p.cpf, m.nome AS medico, 
    c.data_consulta, c.status, d.descricao AS diagnostico, sv.glicemia
FROM consulta c
JOIN paciente p ON p.id_paciente = c.id_paciente
JOIN medico m ON m.id_medico = c.id_medico
LEFT JOIN diagnostico d ON d.id_consulta = c.id_consulta
LEFT JOIN sinal_vital sv ON sv.id_consulta = c.id_consulta;
GO

-- 5. SEED (Dados de Teste)
INSERT INTO especialidade (nome) VALUES ('Cardiologia'), ('Clínica Geral');
INSERT INTO medico (crm, nome, id_especialidade) VALUES ('123-MG', 'Dr. Arnaldo', 1);
INSERT INTO paciente (cpf, nome, data_nascimento, sexo) VALUES ('111.111.111-11', 'Joao Silva', '1980-01-01', 'M');
INSERT INTO consulta (id_paciente, id_medico, data_consulta, motivo) VALUES (1, 1, GETDATE(), 'Dor no peito');
GO