-- ==================== SISTEMA DE AUTENTICAÇÃO E CONTROLE DE PLANOS ====================
-- Execute estes comandos no SQL Editor do Supabase

-- ========================================
-- 1. CRIAR TABELA DE PROFILES (USUÁRIOS)
-- ========================================

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    plano TEXT NOT NULL CHECK (plano IN ('Essencial', 'Plus', 'Elite')),
    status TEXT NOT NULL CHECK (status IN ('ativo', 'inativo', 'cancelado')) DEFAULT 'ativo',
    data_compra TIMESTAMP DEFAULT NOW(),
    data_expiracao TIMESTAMP,
    webhook_source TEXT, -- 'kiwify', 'hotmart', 'manual', etc
    webhook_data JSONB, -- Dados completos do webhook para referência
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Habilitar RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Política: Usuários podem ver apenas seu próprio perfil
CREATE POLICY "Usuários veem apenas seu próprio perfil"
ON profiles FOR SELECT
USING (auth.uid() = id);

-- Política: Sistema pode inserir novos perfis (para webhooks)
CREATE POLICY "Sistema pode inserir perfis"
ON profiles FOR INSERT
WITH CHECK (true);

-- Política: Sistema pode atualizar perfis
CREATE POLICY "Sistema pode atualizar perfis"
ON profiles FOR UPDATE
USING (true);

-- Índices
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);

-- ========================================
-- 2. ADICIONAR CAMPO user_id EM TODAS AS TABELAS
-- ========================================

-- Adicionar user_id em pets
ALTER TABLE pets ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_pets_user_id ON pets(user_id);

-- Adicionar user_id em vacinas
ALTER TABLE vacinas ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_vacinas_user_id ON vacinas(user_id);

-- Adicionar user_id em alimentacao
ALTER TABLE alimentacao ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_alimentacao_user_id ON alimentacao(user_id);

-- Adicionar user_id em veterinario
ALTER TABLE veterinario ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_veterinario_user_id ON veterinario(user_id);

-- Adicionar user_id em medicamentos
ALTER TABLE medicamentos ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_medicamentos_user_id ON medicamentos(user_id);

-- Adicionar user_id em medicamentos_log
ALTER TABLE medicamentos_log ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_medicamentos_log_user_id ON medicamentos_log(user_id);

-- Adicionar user_id em preventivos
ALTER TABLE preventivos ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_preventivos_user_id ON preventivos(user_id);

-- Adicionar user_id em peso
ALTER TABLE peso ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_peso_user_id ON peso(user_id);

-- Adicionar user_id em notas
ALTER TABLE notas ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_notas_user_id ON notas(user_id);

-- ========================================
-- 3. ATUALIZAR POLÍTICAS RLS DE TODAS AS TABELAS
-- ========================================

-- Remover políticas antigas (permissivas demais)
DROP POLICY IF EXISTS "Permitir tudo em pets" ON pets;
DROP POLICY IF EXISTS "Permitir tudo em vacinas" ON vacinas;
DROP POLICY IF EXISTS "Permitir tudo em alimentacao" ON alimentacao;
DROP POLICY IF EXISTS "Permitir tudo em veterinario" ON veterinario;
DROP POLICY IF EXISTS "Permitir tudo em medicamentos" ON medicamentos;
DROP POLICY IF EXISTS "Permitir tudo em medicamentos_log" ON medicamentos_log;
DROP POLICY IF EXISTS "Permitir tudo em preventivos" ON preventivos;
DROP POLICY IF EXISTS "Permitir tudo em peso" ON peso;
DROP POLICY IF EXISTS "Permitir tudo em notas" ON notas;

-- === PETS ===
CREATE POLICY "Usuários veem apenas seus pets"
ON pets FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas seus pets"
ON pets FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas seus pets"
ON pets FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas seus pets"
ON pets FOR DELETE
USING (auth.uid() = user_id);

-- === VACINAS ===
CREATE POLICY "Usuários veem apenas suas vacinas"
ON vacinas FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas suas vacinas"
ON vacinas FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas suas vacinas"
ON vacinas FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas suas vacinas"
ON vacinas FOR DELETE
USING (auth.uid() = user_id);

-- === ALIMENTAÇÃO ===
CREATE POLICY "Usuários veem apenas sua alimentação"
ON alimentacao FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas sua alimentação"
ON alimentacao FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas sua alimentação"
ON alimentacao FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas sua alimentação"
ON alimentacao FOR DELETE
USING (auth.uid() = user_id);

-- === VETERINÁRIO ===
CREATE POLICY "Usuários veem apenas suas consultas"
ON veterinario FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas suas consultas"
ON veterinario FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas suas consultas"
ON veterinario FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas suas consultas"
ON veterinario FOR DELETE
USING (auth.uid() = user_id);

-- === MEDICAMENTOS ===
CREATE POLICY "Usuários veem apenas seus medicamentos"
ON medicamentos FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas seus medicamentos"
ON medicamentos FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas seus medicamentos"
ON medicamentos FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas seus medicamentos"
ON medicamentos FOR DELETE
USING (auth.uid() = user_id);

-- === MEDICAMENTOS LOG ===
CREATE POLICY "Usuários veem apenas seus logs"
ON medicamentos_log FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas seus logs"
ON medicamentos_log FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas seus logs"
ON medicamentos_log FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas seus logs"
ON medicamentos_log FOR DELETE
USING (auth.uid() = user_id);

-- === PREVENTIVOS ===
CREATE POLICY "Usuários veem apenas seus preventivos"
ON preventivos FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas seus preventivos"
ON preventivos FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas seus preventivos"
ON preventivos FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas seus preventivos"
ON preventivos FOR DELETE
USING (auth.uid() = user_id);

-- === PESO ===
CREATE POLICY "Usuários veem apenas suas pesagens"
ON peso FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas suas pesagens"
ON peso FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas suas pesagens"
ON peso FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas suas pesagens"
ON peso FOR DELETE
USING (auth.uid() = user_id);

-- === NOTAS ===
CREATE POLICY "Usuários veem apenas suas notas"
ON notas FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários criam apenas suas notas"
ON notas FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários editam apenas suas notas"
ON notas FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários deletam apenas suas notas"
ON notas FOR DELETE
USING (auth.uid() = user_id);

-- ========================================
-- 4. FUNÇÃO PARA ATUALIZAR updated_at
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para profiles
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 5. FUNÇÃO PARA CRIAR PROFILE AUTOMATICAMENTE
-- ========================================

-- Esta função cria um profile quando um novo usuário é criado no auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, plano, status)
    VALUES (
        NEW.id,
        NEW.email,
        'Essencial', -- Plano padrão
        'inativo'    -- Status padrão (aguardando pagamento)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para criar profile automaticamente
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ========================================
-- 6. EXEMPLO DE INSERT PARA TESTE
-- ========================================

-- Para testar manualmente, você pode criar um usuário teste:
-- IMPORTANTE: Substitua o email e ID conforme necessário

-- INSERT INTO profiles (id, email, plano, status) VALUES
-- ('UUID-AQUI', 'teste@exemplo.com', 'Plus', 'ativo');

-- ========================================
-- 7. SCRIPT PARA WEBHOOKS (REFERÊNCIA)
-- ========================================

-- Exemplo de como processar webhook da Kiwify/Hotmart
-- Este é um exemplo de função que você pode chamar via Edge Function

/*
CREATE OR REPLACE FUNCTION process_webhook(
    webhook_email TEXT,
    webhook_plano TEXT,
    webhook_status TEXT,
    webhook_source TEXT,
    webhook_json JSONB
)
RETURNS VOID AS $$
DECLARE
    user_uuid UUID;
BEGIN
    -- Buscar usuário por email
    SELECT id INTO user_uuid FROM auth.users WHERE email = webhook_email;

    IF user_uuid IS NULL THEN
        -- Usuário não existe, não fazer nada ou criar
        RAISE NOTICE 'Usuário não encontrado: %', webhook_email;
        RETURN;
    END IF;

    -- Atualizar ou inserir profile
    INSERT INTO profiles (id, email, plano, status, webhook_source, webhook_data)
    VALUES (user_uuid, webhook_email, webhook_plano, webhook_status, webhook_source, webhook_json)
    ON CONFLICT (id) DO UPDATE
    SET plano = EXCLUDED.plano,
        status = EXCLUDED.status,
        webhook_source = EXCLUDED.webhook_source,
        webhook_data = EXCLUDED.webhook_data,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
*/
