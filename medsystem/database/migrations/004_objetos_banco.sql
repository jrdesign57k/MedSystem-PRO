-- ============================================================
-- 004 - OBJETOS DE BANCO (Views, Procedures com transacao, Triggers)
-- Aplicado automaticamente pelo app (medsystem/database/db_objects.py).
-- IMPORTANTE: cada statement e separado por uma linha sentinela propria.
-- Nao usar DELIMITER aqui (a execucao e feita statement a statement via driver).
-- ============================================================

-- ===================== VIEWS =====================

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
-- @@SPLIT@@
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
-- @@SPLIT@@
CREATE OR REPLACE VIEW vw_financeiro_mensal AS
SELECT
    YEAR(data_receita)  AS ano,
    MONTH(data_receita) AS mes,
    SUM(CASE WHEN status = 'PAGO'      THEN valor ELSE 0 END) AS total_recebido,
    SUM(CASE WHEN status = 'PENDENTE'  THEN valor ELSE 0 END) AS total_pendente,
    COUNT(*)                                                  AS total_registros
FROM receitas
GROUP BY YEAR(data_receita), MONTH(data_receita)
ORDER BY ano DESC, mes DESC;
-- @@SPLIT@@
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
-- @@SPLIT@@

-- ===================== PROCEDURES =====================

DROP PROCEDURE IF EXISTS sp_cadastrar_paciente;
-- @@SPLIT@@
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
        SET p_msg = 'Erro ao cadastrar paciente. Operacao revertida.';
    END;

    IF p_cpf IS NULL OR TRIM(p_cpf) = '' THEN
        SET p_id  = -1;
        SET p_msg = 'CPF e obrigatorio.';
        LEAVE sp_cadastrar_paciente;
    END IF;

    IF EXISTS (SELECT 1 FROM paciente WHERE cpf = p_cpf) THEN
        SET p_id  = -1;
        SET p_msg = CONCAT('CPF ', p_cpf, ' ja cadastrado.');
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
END;
-- @@SPLIT@@
DROP PROCEDURE IF EXISTS sp_agendar_consulta;
-- @@SPLIT@@
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
        SET p_msg = 'Erro ao agendar consulta. Operacao revertida.';
    END;

    IF NOT EXISTS (SELECT 1 FROM paciente WHERE id_paciente = p_id_paciente AND ativo = 1) THEN
        SET p_id_consulta = -1;
        SET p_msg = 'Paciente nao encontrado ou inativo.';
        LEAVE sp_agendar_consulta;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM medicos WHERE id = p_id_medico) THEN
        SET p_id_consulta = -1;
        SET p_msg = 'Medico nao encontrado.';
        LEAVE sp_agendar_consulta;
    END IF;

    IF EXISTS (
        SELECT 1 FROM consulta
        WHERE id_medico = p_id_medico
          AND status NOT IN ('CANCELADA','CONCLUIDA')
          AND ABS(TIMESTAMPDIFF(MINUTE, data_consulta, p_data_consulta)) < 30
    ) THEN
        SET p_id_consulta = -1;
        SET p_msg = 'Medico ja possui consulta agendada neste horario.';
        LEAVE sp_agendar_consulta;
    END IF;

    START TRANSACTION;
        INSERT INTO consulta (id_paciente, id_medico, data_consulta, hora_consulta, motivo, tipo_consulta)
        VALUES (p_id_paciente, p_id_medico, p_data_consulta, DATE_FORMAT(p_data_consulta,'%H:%i'), p_motivo, p_tipo_consulta);
        SET p_id_consulta = LAST_INSERT_ID();
        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'INSERT', p_id_consulta,
                CONCAT('Consulta agendada para paciente_id=', p_id_paciente,
                       ' medico_id=', p_id_medico, ' data=', p_data_consulta));
    COMMIT;

    SET p_msg = 'Consulta agendada com sucesso.';
END;
-- @@SPLIT@@
DROP PROCEDURE IF EXISTS sp_cancelar_consulta;
-- @@SPLIT@@
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
        SET p_msg = 'Erro ao cancelar consulta. Operacao revertida.';
    END;

    SELECT status INTO v_status FROM consulta WHERE id_consulta = p_id_consulta;

    IF v_status IS NULL THEN
        SET p_msg = 'Consulta nao encontrada.';
        LEAVE sp_cancelar_consulta;
    END IF;

    IF v_status = 'CONCLUIDA' THEN
        SET p_msg = 'Nao e possivel cancelar uma consulta ja concluida.';
        LEAVE sp_cancelar_consulta;
    END IF;

    IF v_status = 'CANCELADA' THEN
        SET p_msg = 'Consulta ja esta cancelada.';
        LEAVE sp_cancelar_consulta;
    END IF;

    START TRANSACTION;
        UPDATE consulta
        SET status = 'CANCELADA',
            observacoes_consulta = CONCAT(IFNULL(observacoes_consulta,''), ' | CANCELADA: ', p_motivo)
        WHERE id_consulta = p_id_consulta;
        UPDATE exames
        SET status = 'DISPONIVEL'
        WHERE id_consulta = p_id_consulta AND status = 'SOLICITADO';
        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'UPDATE', p_id_consulta, CONCAT('Consulta cancelada. Motivo: ', p_motivo));
    COMMIT;

    SET p_msg = 'Consulta cancelada com sucesso.';
END;
-- @@SPLIT@@
DROP PROCEDURE IF EXISTS sp_registrar_prontuario;
-- @@SPLIT@@
CREATE PROCEDURE sp_registrar_prontuario (
    IN  p_id_consulta               INT,
    IN  p_queixa_principal          TEXT,
    IN  p_historia_molestia         TEXT,
    IN  p_exame_fisico              TEXT,
    IN  p_hipotese_diagnostica      TEXT,
    IN  p_plano_terapeutico         TEXT,
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
        SET p_msg = 'Erro ao registrar prontuario. Operacao revertida.';
    END;

    IF NOT EXISTS (SELECT 1 FROM consulta WHERE id_consulta = p_id_consulta AND status != 'CANCELADA') THEN
        SET p_msg = 'Consulta invalida ou cancelada.';
        LEAVE sp_registrar_prontuario;
    END IF;

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
        VALUES ('consulta', 'UPDATE', p_id_consulta, 'Prontuario registrado e consulta concluida.');
    COMMIT;

    SET p_msg = 'Prontuario registrado com sucesso.';
END;
-- @@SPLIT@@
DROP PROCEDURE IF EXISTS sp_registrar_pagamento;
-- @@SPLIT@@
CREATE PROCEDURE sp_registrar_pagamento (
    IN  p_id_receita INT,
    OUT p_msg        VARCHAR(255)
)
sp_registrar_pagamento: BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'Erro ao registrar pagamento. Operacao revertida.';
    END;

    SELECT status INTO v_status FROM receitas WHERE id = p_id_receita;

    IF v_status IS NULL THEN
        SET p_msg = 'Receita nao encontrada.';
        LEAVE sp_registrar_pagamento;
    END IF;

    IF v_status != 'PENDENTE' THEN
        SET p_msg = CONCAT('Receita nao pode ser paga. Status atual: ', v_status);
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
END;
-- @@SPLIT@@
DROP PROCEDURE IF EXISTS sp_inativar_paciente;
-- @@SPLIT@@
CREATE PROCEDURE sp_inativar_paciente (
    IN  p_id_paciente INT,
    OUT p_msg         VARCHAR(255)
)
sp_inativar_paciente: BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'Erro ao inativar paciente. Operacao revertida.';
    END;

    IF NOT EXISTS (SELECT 1 FROM paciente WHERE id_paciente = p_id_paciente) THEN
        SET p_msg = 'Paciente nao encontrado.';
        LEAVE sp_inativar_paciente;
    END IF;

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
END;
-- @@SPLIT@@

-- ===================== TRIGGERS (auditoria) =====================

DROP TRIGGER IF EXISTS trg_consulta_after_insert;
-- @@SPLIT@@
CREATE TRIGGER trg_consulta_after_insert
AFTER INSERT ON consulta
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('consulta', 'INSERT', NEW.id_consulta,
            CONCAT('Nova consulta. Paciente=', NEW.id_paciente,
                   ' Medico=', NEW.id_medico,
                   ' Data=', NEW.data_consulta,
                   ' Status=', NEW.status));
END;
-- @@SPLIT@@
DROP TRIGGER IF EXISTS trg_consulta_after_update;
-- @@SPLIT@@
CREATE TRIGGER trg_consulta_after_update
AFTER UPDATE ON consulta
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
        VALUES ('consulta', 'UPDATE', NEW.id_consulta,
                CONCAT('Status alterado de ', OLD.status, ' para ', NEW.status));
    END IF;
END;
-- @@SPLIT@@
DROP TRIGGER IF EXISTS trg_paciente_after_update;
-- @@SPLIT@@
CREATE TRIGGER trg_paciente_after_update
AFTER UPDATE ON paciente
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('paciente', 'UPDATE', NEW.id_paciente,
            CONCAT('Dados do paciente atualizados. Ativo: ', OLD.ativo, '->', NEW.ativo));
END;
-- @@SPLIT@@
DROP TRIGGER IF EXISTS trg_paciente_after_delete;
-- @@SPLIT@@
CREATE TRIGGER trg_paciente_after_delete
AFTER DELETE ON paciente
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('paciente', 'DELETE', OLD.id_paciente,
            CONCAT('Paciente excluido: ', OLD.nome, ' CPF:', OLD.cpf));
END;
-- @@SPLIT@@
DROP TRIGGER IF EXISTS trg_usuario_after_insert;
-- @@SPLIT@@
CREATE TRIGGER trg_usuario_after_insert
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO logs_auditoria (tabela, operacao, id_registro, detalhe)
    VALUES ('usuarios', 'INSERT', NEW.id,
            CONCAT('Usuario criado: ', NEW.nome, ' Tipo:', NEW.tipo));
END;
-- @@SPLIT@@
DROP TRIGGER IF EXISTS trg_receita_after_update;
-- @@SPLIT@@
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
END;
