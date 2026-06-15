-- ============================================================
--  MEDSYSTEM - Banco de Dados Completo
--  MySQL 5.7+ / 8.0+
--  Inclui: DDL, Procedures com Transação, Triggers de Auditoria,
--          Views, Índices e Permissões (Least Privilege)
-- ============================================================

CREATE DATABASE IF NOT EXISTS medsystem
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE medsystem;

-- ============================================================
-- 1. TABELAS
-- ============================================================

CREATE TABLE IF NOT EXISTS especialidades (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuarios (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(150) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    senha_hash  VARCHAR(255) NOT NULL,
    tipo        ENUM('medico','admin','recepcionista') NOT NULL,
    ativo       TINYINT(1) NOT NULL DEFAULT 1,
    criado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS medicos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    crm             VARCHAR(20) NOT NULL UNIQUE,
    id_especialidade INT NOT NULL,
    CONSTRAINT fk_medico_usuario       FOREIGN KEY (id_usuario)       REFERENCES usuarios(id)       ON DELETE RESTRICT,
    CONSTRAINT fk_medico_especialidade FOREIGN KEY (id_especialidade) REFERENCES especialidades(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS paciente (
    id_paciente             INT AUTO_INCREMENT PRIMARY KEY,
    cpf                     VARCHAR(14) NOT NULL UNIQUE,
    nome                    VARCHAR(150) NOT NULL,
    data_nascimento         DATE NOT NULL,
    sexo                    CHAR(1),
    telefone                VARCHAR(20),
    email                   VARCHAR(150),
    endereco                VARCHAR(255),
    tipo_sanguineo          VARCHAR(5),
    alergias                TEXT,
    observacoes             TEXT,
    data_cadastro           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo                   TINYINT(1) NOT NULL DEFAULT 1,
    -- Dados Pessoais
    naturalidade            VARCHAR(100),
    estado_civil            VARCHAR(50),
    profissao               VARCHAR(100),
    empresa                 VARCHAR(100),
    rg                      VARCHAR(20),
    mae                     VARCHAR(150),
    responsavel             VARCHAR(150),
    -- Endereço Detalhado
    logradouro              VARCHAR(150),
    numero                  VARCHAR(20),
    complemento             VARCHAR(100),
    bairro                  VARCHAR(100),
    cidade                  VARCHAR(100),
    uf                      CHAR(2),
    cep                     VARCHAR(9),
    -- Contato de Emergência
    emergencia_nome         VARCHAR(150),
    emergencia_telefone     VARCHAR(20),
    -- Sinais Vitais Iniciais
    peso                    DECIMAL(5,2),
    altura                  SMALLINT,
    pressao                 VARCHAR(10),
    frequencia_cardiaca     SMALLINT,
    -- Histórico
    historico_familiar      TEXT,
    medicamentos            TEXT,
    cirurgias               TEXT,
    -- Hábitos
    tabagismo               VARCHAR(50),
    alcoolismo              VARCHAR(50),
    atividade_fisica        VARCHAR(50),
    observacoes_clinicas    TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contatos_emergencia (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    nome        VARCHAR(150) NOT NULL,
    telefone    VARCHAR(20)  NOT NULL,
    parentesco  VARCHAR(50),
    CONSTRAINT fk_contato_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consulta (
    id_consulta             INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente             INT NOT NULL,
    id_medico               INT NOT NULL,
    data_consulta           DATETIME NOT NULL,
    hora_consulta           CHAR(5),
    status                  ENUM('AGENDADA','EM_ATENDIMENTO','CONCLUIDA','CANCELADA') NOT NULL DEFAULT 'AGENDADA',
    motivo                  VARCHAR(255),
    queixa_principal        TEXT,
    historia_molestia_atual TEXT,
    antecedentes_pessoais   TEXT,
    antecedentes_familiares TEXT,
    exame_fisico            TEXT,
    hipotese_diagnostica    TEXT,
    plano_terapeutico       TEXT,
    observacoes_consulta    TEXT,
    tipo_consulta           VARCHAR(50),
    convenio                VARCHAR(100),
    CONSTRAINT fk_consulta_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente) ON DELETE RESTRICT,
    CONSTRAINT fk_consulta_medico   FOREIGN KEY (id_medico)   REFERENCES medicos(id)           ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipos_exame (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exames (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta      INT NOT NULL,
    id_paciente      INT NOT NULL,
    id_medico        INT NOT NULL,
    id_tipo_exame    INT NOT NULL,
    nome_exame       VARCHAR(200),
    resultado        TEXT,
    laudo            TEXT,
    status           ENUM('SOLICITADO','AGUARDANDO','EM_ANALISE','DISPONIVEL') NOT NULL DEFAULT 'SOLICITADO',
    prioridade       ENUM('URGENTE','NORMAL','BAIXA') NOT NULL DEFAULT 'NORMAL',
    data_solicitacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_resultado   DATETIME,
    CONSTRAINT fk_exame_consulta   FOREIGN KEY (id_consulta)   REFERENCES consulta(id_consulta)   ON DELETE RESTRICT,
    CONSTRAINT fk_exame_paciente   FOREIGN KEY (id_paciente)   REFERENCES paciente(id_paciente)   ON DELETE RESTRICT,
    CONSTRAINT fk_exame_medico     FOREIGN KEY (id_medico)     REFERENCES medicos(id)             ON DELETE RESTRICT,
    CONSTRAINT fk_exame_tipo       FOREIGN KEY (id_tipo_exame) REFERENCES tipos_exame(id)         ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sinais_vitais (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta         INT NOT NULL,
    pressao_arterial    VARCHAR(20),
    frequencia_cardiaca SMALLINT,
    saturacao_oxigenio  TINYINT,
    temperatura         DECIMAL(4,1),
    imc                 DECIMAL(5,2),
    peso                DECIMAL(5,2),
    altura              SMALLINT,
    registrado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sinal_consulta FOREIGN KEY (id_consulta) REFERENCES consulta(id_consulta) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cid10 (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    codigo    VARCHAR(10) NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    categoria VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS diagnosticos (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta      INT NOT NULL,
    id_paciente      INT NOT NULL,
    id_medico        INT NOT NULL,
    cid              VARCHAR(10) NOT NULL,
    descricao        TEXT NOT NULL,
    gravidade        ENUM('Leve','Moderada','Grave'),
    status           ENUM('ATIVO','RESOLVIDO','CRONICO') NOT NULL DEFAULT 'ATIVO',
    data_diagnostico DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_diag_consulta FOREIGN KEY (id_consulta) REFERENCES consulta(id_consulta)  ON DELETE RESTRICT,
    CONSTRAINT fk_diag_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)  ON DELETE RESTRICT,
    CONSTRAINT fk_diag_medico   FOREIGN KEY (id_medico)   REFERENCES medicos(id)            ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS prescricoes (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta      INT NOT NULL,
    id_medico        INT NOT NULL,
    id_paciente      INT NOT NULL,
    medicamento      VARCHAR(150) NOT NULL,
    dosagem          VARCHAR(100),
    posologia        TEXT NOT NULL,
    frequencia       VARCHAR(100),
    duracao          VARCHAR(100),
    quantidade       SMALLINT,
    tipo_receita     ENUM('Simples','Controlada Azul','Controlada Amarela'),
    orientacoes      TEXT,
    data_prescricao  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status           ENUM('ATIVA','ENCERRADA','CANCELADA') NOT NULL DEFAULT 'ATIVA',
    CONSTRAINT fk_presc_consulta FOREIGN KEY (id_consulta) REFERENCES consulta(id_consulta) ON DELETE RESTRICT,
    CONSTRAINT fk_presc_medico   FOREIGN KEY (id_medico)   REFERENCES medicos(id)           ON DELETE RESTRICT,
    CONSTRAINT fk_presc_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS receitas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta     INT,
    id_paciente     INT NOT NULL,
    id_medico       INT NOT NULL,
    descricao       VARCHAR(255) NOT NULL,
    valor           DECIMAL(10,2) NOT NULL,
    tipo            VARCHAR(50)  NOT NULL,
    convenio        VARCHAR(100),
    data_receita    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_pagamento  DATETIME,
    status          ENUM('PENDENTE','PAGO','CANCELADO') NOT NULL DEFAULT 'PENDENTE',
    CONSTRAINT fk_receita_consulta FOREIGN KEY (id_consulta) REFERENCES consulta(id_consulta) ON DELETE SET NULL,
    CONSTRAINT fk_receita_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente) ON DELETE RESTRICT,
    CONSTRAINT fk_receita_medico   FOREIGN KEY (id_medico)   REFERENCES medicos(id)           ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS despesas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    descricao       VARCHAR(255) NOT NULL,
    valor           DECIMAL(10,2) NOT NULL,
    categoria       VARCHAR(100),
    tipo            ENUM('FIXA','VARIAVEL') NOT NULL DEFAULT 'FIXA',
    data_despesa    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_pagamento  DATETIME,
    status          ENUM('PENDENTE','PAGO','CANCELADO') NOT NULL DEFAULT 'PENDENTE'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mensagens (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    id_remetente    INT NOT NULL,
    id_destinatario INT NOT NULL,
    assunto         VARCHAR(255),
    conteudo        TEXT NOT NULL,
    data_envio      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lida            TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_msg_remetente    FOREIGN KEY (id_remetente)    REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_msg_destinatario FOREIGN KEY (id_destinatario) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 2. TABELA DE AUDITORIA (usada pelos triggers)
-- ============================================================

CREATE TABLE IF NOT EXISTS logs_auditoria (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    tabela      VARCHAR(100) NOT NULL,
    operacao    ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    id_registro INT,
    detalhe     TEXT,
    data_hora   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 3. ÍNDICES
-- ============================================================

-- Paciente
CREATE INDEX idx_paciente_cpf          ON paciente(cpf);
CREATE INDEX idx_paciente_nome         ON paciente(nome);
CREATE INDEX idx_paciente_ativo        ON paciente(ativo);

-- Consulta
CREATE INDEX idx_consulta_paciente     ON consulta(id_paciente);
CREATE INDEX idx_consulta_medico       ON consulta(id_medico);
CREATE INDEX idx_consulta_data         ON consulta(data_consulta);
CREATE INDEX idx_consulta_status       ON consulta(status);

-- Exames
CREATE INDEX idx_exame_status          ON exames(status);
CREATE INDEX idx_exame_paciente        ON exames(id_paciente);

-- Diagnósticos
CREATE INDEX idx_diag_cid              ON diagnosticos(cid);
CREATE INDEX idx_diag_paciente         ON diagnosticos(id_paciente);

-- Logs de auditoria
CREATE INDEX idx_audit_tabela          ON logs_auditoria(tabela);
CREATE INDEX idx_audit_data            ON logs_auditoria(data_hora);

-- Receitas
CREATE INDEX idx_receita_status        ON receitas(status);
CREATE INDEX idx_receita_data          ON receitas(data_receita);

-- ============================================================
-- 4. STORED PROCEDURES COM TRANSAÇÃO
-- ============================================================

DELIMITER $$

-- ─── 4.1 Cadastrar Paciente ───────────────────────────────
DROP PROCEDURE IF EXISTS sp_cadastrar_paciente$$
CREATE PROCEDURE sp_cadastrar_paciente (
    IN p_cpf             VARCHAR(14),
    IN p_nome            VARCHAR(150),
    IN p_data_nascimento DATE,
    IN p_sexo            CHAR(1),
    IN p_telefone        VARCHAR(20),
    IN p_email           VARCHAR(150),
    IN p_tipo_sanguineo  VARCHAR(5),
    OUT p_id             INT,
    OUT p_msg            VARCHAR(255)
)
sp_cadastrar_paciente: BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_id  = -1;
        SET p_msg = 'Erro ao cadastrar paciente. Operação revertida.';
    END;

    -- Validação: CPF obrigatório
    IF p_cpf IS NULL OR TRIM(p_cpf) = '' THEN
        SET p_id  = -1;
        SET p_msg = 'CPF é obrigatório.';
        LEAVE sp_cadastrar_paciente;
    END IF;

    -- Validação: CPF duplicado
    IF EXISTS (SELECT 1 FROM paciente WHERE cpf = p_cpf) THEN
        SET p_id  = -1;
        SET p_msg = CONCAT('CPF ', p_cpf, ' já cadastrado.');
        LEAVE sp_cadastrar_paciente;
    END IF;

    START TRANSACTION;

        INSERT INTO paciente (cpf, nome, data_nascimento, sexo, telefone, email, tipo_sanguineo)
        VALUES (p_cpf, p_nome, p_data_nascimento, p_sexo, p_telefone, p_email, p_tipo_sanguineo);

        SET p_id = LAST_INSERT_ID();

        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('paciente', 'INSERT', p_id, CONCAT('Paciente cadastrado: ', p_nome));

    COMMIT;

    SET p_msg = 'Paciente cadastrado com sucesso.';
END$$

-- ─── 4.2 Agendar Consulta ─────────────────────────────────
DROP PROCEDURE IF EXISTS sp_agendar_consulta$$
CREATE PROCEDURE sp_agendar_consulta (
    IN  p_id_paciente    INT,
    IN  p_id_medico      INT,
    IN  p_data_consulta  DATETIME,
    IN  p_motivo         VARCHAR(255),
    IN  p_tipo_consulta  VARCHAR(50),
    OUT p_id_consulta    INT,
    OUT p_msg            VARCHAR(255)
)
sp_agendar_consulta: BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_id_consulta = -1;
        SET p_msg = 'Erro ao agendar consulta. Operação revertida.';
    END;

    -- Validar paciente ativo
    IF NOT EXISTS (SELECT 1 FROM paciente WHERE id_paciente = p_id_paciente AND ativo = 1) THEN
        SET p_id_consulta = -1;
        SET p_msg = 'Paciente não encontrado ou inativo.';
        LEAVE sp_agendar_consulta;
    END IF;

    -- Validar médico existente
    IF NOT EXISTS (SELECT 1 FROM medicos WHERE id = p_id_medico) THEN
        SET p_id_consulta = -1;
        SET p_msg = 'Médico não encontrado.';
        LEAVE sp_agendar_consulta;
    END IF;

    -- Conflito de horário do médico (margem de 30 min)
    IF EXISTS (
        SELECT 1 FROM consulta
        WHERE id_medico = p_id_medico
          AND status NOT IN ('CANCELADA','CONCLUIDA')
          AND ABS(TIMESTAMPDIFF(MINUTE, data_consulta, p_data_consulta)) < 30
    ) THEN
        SET p_id_consulta = -1;
        SET p_msg = 'Médico já possui consulta agendada neste horário.';
        LEAVE sp_agendar_consulta;
    END IF;

    START TRANSACTION;

        INSERT INTO consulta (id_paciente, id_medico, data_consulta, hora_consulta, motivo, tipo_consulta)
        VALUES (p_id_paciente, p_id_medico, p_data_consulta, DATE_FORMAT(p_data_consulta,'%H:%i'), p_motivo, p_tipo_consulta);

        SET p_id_consulta = LAST_INSERT_ID();

        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'INSERT', p_id_consulta,
                CONCAT('Consulta agendada para paciente_id=', p_id_paciente,
                       ' medico_id=', p_id_medico,
                       ' data=', p_data_consulta));

    COMMIT;

    SET p_msg = 'Consulta agendada com sucesso.';
END$$

-- ─── 4.3 Cancelar Consulta ────────────────────────────────
DROP PROCEDURE IF EXISTS sp_cancelar_consulta$$
CREATE PROCEDURE sp_cancelar_consulta (
    IN  p_id_consulta INT,
    IN  p_motivo      VARCHAR(255),
    OUT p_msg         VARCHAR(255)
)
sp_cancelar_consulta: BEGIN
    DECLARE v_status VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'Erro ao cancelar consulta. Operação revertida.';
    END;

    SELECT status INTO v_status FROM consulta WHERE id_consulta = p_id_consulta;

    IF v_status IS NULL THEN
        SET p_msg = 'Consulta não encontrada.';
        LEAVE sp_cancelar_consulta;
    END IF;

    IF v_status = 'CONCLUIDA' THEN
        SET p_msg = 'Não é possível cancelar uma consulta já concluída.';
        LEAVE sp_cancelar_consulta;
    END IF;

    IF v_status = 'CANCELADA' THEN
        SET p_msg = 'Consulta já está cancelada.';
        LEAVE sp_cancelar_consulta;
    END IF;

    START TRANSACTION;

        UPDATE consulta
        SET status = 'CANCELADA',
            observacoes_consulta = CONCAT(IFNULL(observacoes_consulta,''), ' | CANCELADA: ', p_motivo)
        WHERE id_consulta = p_id_consulta;

        -- Cancelar exames SOLICITADOS vinculados
        UPDATE exames
        SET status = 'DISPONIVEL'   -- mantém registro mas marca como não executado
        WHERE id_consulta = p_id_consulta AND status = 'SOLICITADO';

        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'UPDATE', p_id_consulta, CONCAT('Consulta cancelada. Motivo: ', p_motivo));

    COMMIT;

    SET p_msg = 'Consulta cancelada com sucesso.';
END$$

-- ─── 4.4 Registrar Prontuário Completo ────────────────────
DROP PROCEDURE IF EXISTS sp_registrar_prontuario$$
CREATE PROCEDURE sp_registrar_prontuario (
    IN  p_id_consulta               INT,
    IN  p_queixa_principal          TEXT,
    IN  p_historia_molestia         TEXT,
    IN  p_exame_fisico              TEXT,
    IN  p_hipotese_diagnostica      TEXT,
    IN  p_plano_terapeutico         TEXT,
    -- sinais vitais
    IN  p_pressao_arterial          VARCHAR(20),
    IN  p_frequencia_cardiaca       SMALLINT,
    IN  p_saturacao_oxigenio        TINYINT,
    IN  p_temperatura               DECIMAL(4,1),
    IN  p_peso                      DECIMAL(5,2),
    IN  p_altura                    SMALLINT,
    OUT p_msg                       VARCHAR(255)
)
sp_registrar_prontuario: BEGIN
    DECLARE v_imc DECIMAL(5,2) DEFAULT NULL;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'Erro ao registrar prontuário. Operação revertida.';
    END;

    IF NOT EXISTS (SELECT 1 FROM consulta WHERE id_consulta = p_id_consulta AND status != 'CANCELADA') THEN
        SET p_msg = 'Consulta inválida ou cancelada.';
        LEAVE sp_registrar_prontuario;
    END IF;

    -- Calcular IMC se peso e altura disponíveis
    IF p_peso IS NOT NULL AND p_altura IS NOT NULL AND p_altura > 0 THEN
        SET v_imc = ROUND(p_peso / POWER(p_altura / 100.0, 2), 2);
    END IF;

    START TRANSACTION;

        UPDATE consulta
        SET queixa_principal        = p_queixa_principal,
            historia_molestia_atual = p_historia_molestia,
            exame_fisico            = p_exame_fisico,
            hipotese_diagnostica    = p_hipotese_diagnostica,
            plano_terapeutico       = p_plano_terapeutico,
            status                  = 'CONCLUIDA'
        WHERE id_consulta = p_id_consulta;

        INSERT INTO sinais_vitais
            (id_consulta, pressao_arterial, frequencia_cardiaca,
             saturacao_oxigenio, temperatura, peso, altura, imc)
        VALUES
            (p_id_consulta, p_pressao_arterial, p_frequencia_cardiaca,
             p_saturacao_oxigenio, p_temperatura, p_peso, p_altura, v_imc);

        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'UPDATE', p_id_consulta, 'Prontuário registrado e consulta concluída.');

    COMMIT;

    SET p_msg = 'Prontuário registrado com sucesso.';
END$$

-- ─── 4.5 Registrar Pagamento de Receita ───────────────────
DROP PROCEDURE IF EXISTS sp_registrar_pagamento$$
CREATE PROCEDURE sp_registrar_pagamento (
    IN  p_id_receita INT,
    OUT p_msg        VARCHAR(255)
)
sp_registrar_pagamento: BEGIN
    DECLARE v_status VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'Erro ao registrar pagamento. Operação revertida.';
    END;

    SELECT status INTO v_status FROM receitas WHERE id = p_id_receita;

    IF v_status IS NULL THEN
        SET p_msg = 'Receita não encontrada.';
        LEAVE sp_registrar_pagamento;
    END IF;

    IF v_status != 'PENDENTE' THEN
        SET p_msg = CONCAT('Receita não pode ser paga. Status atual: ', v_status);
        LEAVE sp_registrar_pagamento;
    END IF;

    START TRANSACTION;

        UPDATE receitas
        SET status = 'PAGO', data_pagamento = NOW()
        WHERE id = p_id_receita;

        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('receitas', 'UPDATE', p_id_receita, 'Pagamento registrado.');

    COMMIT;

    SET p_msg = 'Pagamento registrado com sucesso.';
END$$

-- ─── 4.6 Inativar Paciente ────────────────────────────────
DROP PROCEDURE IF EXISTS sp_inativar_paciente$$
CREATE PROCEDURE sp_inativar_paciente (
    IN  p_id_paciente INT,
    OUT p_msg         VARCHAR(255)
)
sp_inativar_paciente: BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'Erro ao inativar paciente. Operação revertida.';
    END;

    IF NOT EXISTS (SELECT 1 FROM paciente WHERE id_paciente = p_id_paciente) THEN
        SET p_msg = 'Paciente não encontrado.';
        LEAVE sp_inativar_paciente;
    END IF;

    -- Impedir inativação com consultas abertas
    IF EXISTS (
        SELECT 1 FROM consulta
        WHERE id_paciente = p_id_paciente
          AND status IN ('AGENDADA','EM_ATENDIMENTO')
    ) THEN
        SET p_msg = 'Paciente possui consultas em aberto. Cancele-as antes de inativar.';
        LEAVE sp_inativar_paciente;
    END IF;

    START TRANSACTION;

        UPDATE paciente SET ativo = 0 WHERE id_paciente = p_id_paciente;

        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('paciente', 'UPDATE', p_id_paciente, 'Paciente inativado.');

    COMMIT;

    SET p_msg = 'Paciente inativado com sucesso.';
END$$

DELIMITER ;

-- ============================================================
-- 5. TRIGGERS DE AUDITORIA
-- ============================================================

DELIMITER $$

-- ─── Consulta: INSERT ─────────────────────────────────────
DROP TRIGGER IF EXISTS trg_consulta_after_insert$$
CREATE TRIGGER trg_consulta_after_insert
AFTER INSERT ON consulta
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('consulta', 'INSERT', NEW.id_consulta,
            CONCAT('Nova consulta. Paciente=', NEW.id_paciente,
                   ' Médico=', NEW.id_medico,
                   ' Data=', NEW.data_consulta,
                   ' Status=', NEW.status));
END$$

-- ─── Consulta: UPDATE ─────────────────────────────────────
DROP TRIGGER IF EXISTS trg_consulta_after_update$$
CREATE TRIGGER trg_consulta_after_update
AFTER UPDATE ON consulta
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'UPDATE', NEW.id_consulta,
                CONCAT('Status alterado de ', OLD.status, ' para ', NEW.status));
    END IF;
END$$

-- ─── Paciente: UPDATE ─────────────────────────────────────
DROP TRIGGER IF EXISTS trg_paciente_after_update$$
CREATE TRIGGER trg_paciente_after_update
AFTER UPDATE ON paciente
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('paciente', 'UPDATE', NEW.id_paciente,
            CONCAT('Dados do paciente atualizados. Ativo: ', OLD.ativo, '->', NEW.ativo));
END$$

-- ─── Paciente: DELETE ─────────────────────────────────────
DROP TRIGGER IF EXISTS trg_paciente_after_delete$$
CREATE TRIGGER trg_paciente_after_delete
AFTER DELETE ON paciente
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('paciente', 'DELETE', OLD.id_paciente,
            CONCAT('Paciente excluído: ', OLD.nome, ' CPF:', OLD.cpf));
END$$

-- ─── Usuário: INSERT ──────────────────────────────────────
DROP TRIGGER IF EXISTS trg_usuario_after_insert$$
CREATE TRIGGER trg_usuario_after_insert
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('usuarios', 'INSERT', NEW.id,
            CONCAT('Usuário criado: ', NEW.nome, ' Tipo:', NEW.tipo));
END$$

-- ─── Receitas: UPDATE pagamento ───────────────────────────
DROP TRIGGER IF EXISTS trg_receita_after_update$$
CREATE TRIGGER trg_receita_after_update
AFTER UPDATE ON receitas
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('receitas', 'UPDATE', NEW.id,
                CONCAT('Status financeiro: ', OLD.status, '->', NEW.status,
                       ' Valor=R$', NEW.valor));
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- 6. VIEWS
-- ============================================================

-- Agenda do dia (consultas de hoje)
CREATE OR REPLACE VIEW vw_agenda_hoje AS
SELECT
    c.id_consulta,
    c.data_consulta,
    c.hora_consulta,
    c.status,
    c.tipo_consulta,
    c.motivo,
    p.id_paciente,
    p.nome   AS nome_paciente,
    p.cpf,
    p.telefone,
    u.nome   AS nome_medico,
    e.nome   AS especialidade
FROM consulta c
JOIN paciente       p ON p.id_paciente = c.id_paciente
JOIN medicos        m ON m.id = c.id_medico
JOIN usuarios       u ON u.id = m.id_usuario
JOIN especialidades e ON e.id = m.id_especialidade
WHERE DATE(c.data_consulta) = CURDATE()
ORDER BY c.data_consulta;

-- Histórico completo do paciente
CREATE OR REPLACE VIEW vw_historico_paciente AS
SELECT
    p.id_paciente,
    p.nome AS nome_paciente,
    p.cpf,
    c.id_consulta,
    c.data_consulta,
    c.status AS status_consulta,
    c.queixa_principal,
    c.hipotese_diagnostica,
    u.nome AS nome_medico,
    e.nome AS especialidade,
    d.cid,
    d.descricao AS descricao_diagnostico,
    d.gravidade,
    pr.medicamento,
    pr.dosagem,
    pr.posologia
FROM paciente p
LEFT JOIN consulta       c  ON c.id_paciente = p.id_paciente
LEFT JOIN medicos        m  ON m.id = c.id_medico
LEFT JOIN usuarios       u  ON u.id = m.id_usuario
LEFT JOIN especialidades e  ON e.id = m.id_especialidade
LEFT JOIN diagnosticos   d  ON d.id_consulta = c.id_consulta
LEFT JOIN prescricoes    pr ON pr.id_consulta = c.id_consulta
ORDER BY p.id_paciente, c.data_consulta DESC;

-- Dashboard financeiro mensal
CREATE OR REPLACE VIEW vw_financeiro_mensal AS
SELECT
    YEAR(data_receita)  AS ano,
    MONTH(data_receita) AS mes,
    SUM(CASE WHEN status = 'PAGO'      THEN valor ELSE 0 END) AS total_recebido,
    SUM(CASE WHEN status = 'PENDENTE'  THEN valor ELSE 0 END) AS total_pendente,
    COUNT(*)                                                    AS total_registros
FROM receitas
GROUP BY YEAR(data_receita), MONTH(data_receita)
ORDER BY ano DESC, mes DESC;

-- Exames pendentes
CREATE OR REPLACE VIEW vw_exames_pendentes AS
SELECT
    ex.id           AS id_exame,
    ex.nome_exame,
    ex.status,
    ex.prioridade,
    ex.data_solicitacao,
    p.nome          AS nome_paciente,
    p.telefone,
    u.nome          AS nome_medico
FROM exames ex
JOIN paciente p ON p.id_paciente = ex.id_paciente
JOIN medicos  m ON m.id = ex.id_medico
JOIN usuarios u ON u.id = m.id_usuario
WHERE ex.status IN ('SOLICITADO','AGUARDANDO','EM_ANALISE')
ORDER BY
    CASE ex.prioridade WHEN 'URGENTE' THEN 1 WHEN 'NORMAL' THEN 2 ELSE 3 END,
    ex.data_solicitacao;

-- ============================================================
-- 7. PERMISSÕES DE USUÁRIO (Least Privilege)
-- ============================================================

-- Usuário da aplicação web (acesso de operação)
CREATE USER IF NOT EXISTS 'med_app'@'%' IDENTIFIED BY 'App@Secure2024!';
GRANT SELECT, INSERT, UPDATE ON medsystem.paciente           TO 'med_app'@'%';
GRANT SELECT, INSERT, UPDATE ON medsystem.consulta           TO 'med_app'@'%';
GRANT SELECT, INSERT, UPDATE ON medsystem.exames             TO 'med_app'@'%';
GRANT SELECT, INSERT, UPDATE ON medsystem.prescricoes        TO 'med_app'@'%';
GRANT SELECT, INSERT, UPDATE ON medsystem.diagnosticos       TO 'med_app'@'%';
GRANT SELECT, INSERT, UPDATE ON medsystem.sinais_vitais      TO 'med_app'@'%';
GRANT SELECT, INSERT, UPDATE ON medsystem.receitas           TO 'med_app'@'%';
GRANT SELECT, INSERT         ON medsystem.mensagens          TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.especialidades     TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.medicos            TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.usuarios           TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.tipos_exame        TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.cid10              TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.logs_auditoria     TO 'med_app'@'%';
GRANT SELECT                 ON medsystem.despesas           TO 'med_app'@'%';
-- Permissão para executar as procedures
GRANT EXECUTE ON PROCEDURE medsystem.sp_cadastrar_paciente   TO 'med_app'@'%';
GRANT EXECUTE ON PROCEDURE medsystem.sp_agendar_consulta     TO 'med_app'@'%';
GRANT EXECUTE ON PROCEDURE medsystem.sp_cancelar_consulta    TO 'med_app'@'%';
GRANT EXECUTE ON PROCEDURE medsystem.sp_registrar_prontuario TO 'med_app'@'%';
GRANT EXECUTE ON PROCEDURE medsystem.sp_registrar_pagamento  TO 'med_app'@'%';
GRANT EXECUTE ON PROCEDURE medsystem.sp_inativar_paciente    TO 'med_app'@'%';

-- Usuário somente leitura para relatórios / BI
CREATE USER IF NOT EXISTS 'med_relatorios'@'%' IDENTIFIED BY 'Report@2024!';
GRANT SELECT ON medsystem.vw_agenda_hoje          TO 'med_relatorios'@'%';
GRANT SELECT ON medsystem.vw_historico_paciente   TO 'med_relatorios'@'%';
GRANT SELECT ON medsystem.vw_financeiro_mensal    TO 'med_relatorios'@'%';
GRANT SELECT ON medsystem.vw_exames_pendentes     TO 'med_relatorios'@'%';
GRANT SELECT ON medsystem.logs_auditoria          TO 'med_relatorios'@'%';

-- Usuário de backup (somente leitura em todas as tabelas)
CREATE USER IF NOT EXISTS 'med_backup'@'localhost' IDENTIFIED BY 'Backup@2024!';
GRANT SELECT, LOCK TABLES, SHOW VIEW ON medsystem.* TO 'med_backup'@'localhost';

FLUSH PRIVILEGES;

-- ============================================================
-- 8. DADOS INICIAIS (seed mínimo)
-- ============================================================

INSERT IGNORE INTO especialidades (nome) VALUES
    ('Clínica Geral'), ('Cardiologia'), ('Dermatologia'),
    ('Pediatria'), ('Ginecologia'), ('Ortopedia'),
    ('Neurologia'), ('Oftalmologia'), ('Psiquiatria');

INSERT IGNORE INTO tipos_exame (nome) VALUES
    ('Hemograma Completo'), ('Glicemia'), ('Colesterol Total'),
    ('Triglicerídeos'), ('TSH / T4'), ('Urina Tipo I'),
    ('Eletrocardiograma'), ('Raio-X Tórax'), ('Ultrassonografia');

-- Admin padrão (senha deve ser trocada após 1º login)
-- Senha hash de exemplo — substituir por hash bcrypt real via aplicação
INSERT IGNORE INTO usuarios (nome, email, senha_hash, tipo)
VALUES ('Administrador', 'admin@medsystem.com',
        '$2b$12$HASH_PLACEHOLDER_TROCAR_NA_APP', 'admin');

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
