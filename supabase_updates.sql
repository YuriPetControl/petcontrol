-- ==================== ATUALIZAÇÕES DO PETCONTROL ====================
-- Execute estes comandos no SQL Editor do Supabase

-- 1. Adicionar campo doses_por_dia na tabela medicamentos
ALTER TABLE medicamentos ADD COLUMN IF NOT EXISTS doses_por_dia INTEGER DEFAULT 1;

-- 2. Criar tabela de log de medicamentos para controle de doses
CREATE TABLE IF NOT EXISTS medicamentos_log (
    id BIGSERIAL PRIMARY KEY,
    medicamento_id BIGINT NOT NULL,
    numero_dose INTEGER NOT NULL,
    data_dose DATE NOT NULL,
    realizado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(medicamento_id, numero_dose)
);

-- 3. Habilitar Row Level Security
ALTER TABLE medicamentos_log ENABLE ROW LEVEL SECURITY;

-- 4. Criar política para permitir todas as operações
CREATE POLICY "Permitir tudo em medicamentos_log" ON medicamentos_log FOR ALL USING (true) WITH CHECK (true);

-- 5. Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_medicamentos_log_medicamento_id ON medicamentos_log(medicamento_id);
CREATE INDEX IF NOT EXISTS idx_medicamentos_log_realizado ON medicamentos_log(realizado);

-- 6. Função para inicializar log de medicamento automaticamente
-- (Opcional - pode ser feito via app.py)
