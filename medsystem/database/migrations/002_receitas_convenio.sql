-- Coluna usada ao gerar receita no agendamento (bancos criados antes de 2026)
ALTER TABLE receitas ADD COLUMN IF NOT EXISTS convenio VARCHAR(100) NULL;
