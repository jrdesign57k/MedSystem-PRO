-- Execute no RDS/MySQL se a migração automática não rodar (banco criado antes de 2026)
-- mysql -u USER -p medsystem < 001_consulta_prontuario.sql

ALTER TABLE consulta ADD COLUMN IF NOT EXISTS hora_consulta CHAR(5) NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS queixa_principal TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS historia_molestia_atual TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS antecedentes_pessoais TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS antecedentes_familiares TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS exame_fisico TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS hipotese_diagnostica TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS plano_terapeutico TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS observacoes_consulta TEXT NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS tipo_consulta VARCHAR(50) NULL;
ALTER TABLE consulta ADD COLUMN IF NOT EXISTS convenio VARCHAR(100) NULL;
