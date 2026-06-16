-- Colunas usadas pelo model Diagnostico (bancos criados antes de 2026)
ALTER TABLE diagnosticos ADD COLUMN IF NOT EXISTS id_paciente INT NULL;
ALTER TABLE diagnosticos ADD COLUMN IF NOT EXISTS id_medico INT NULL;

UPDATE diagnosticos d
INNER JOIN consulta c ON d.id_consulta = c.id_consulta
SET d.id_paciente = c.id_paciente, d.id_medico = c.id_medico
WHERE d.id_paciente IS NULL OR d.id_medico IS NULL;
