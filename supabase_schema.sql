-- ==================== SCHEMA DO PETCONTROL NO SUPABASE ====================
-- Execute estes comandos no SQL Editor do Supabase

-- Tabela de Pets
CREATE TABLE IF NOT EXISTS pets (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    especie TEXT NOT NULL,
    raca TEXT,
    data_nascimento DATE NOT NULL,
    peso DECIMAL(10,2),
    cor TEXT,
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Vacinas
CREATE TABLE IF NOT EXISTS vacinas (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    nome_vacina TEXT NOT NULL,
    data_aplicacao DATE NOT NULL,
    lote TEXT,
    veterinario TEXT,
    proxima_dose DATE,
    observacoes TEXT,
    concluido BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Alimentação
CREATE TABLE IF NOT EXISTS alimentacao (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    tipo_alimento TEXT NOT NULL,
    marca_nome TEXT NOT NULL,
    quantidade DECIMAL(10,2),
    frequencia INTEGER,
    horarios TEXT,
    data_registro TIMESTAMP DEFAULT NOW(),
    concluido BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Veterinário
CREATE TABLE IF NOT EXISTS veterinario (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    nome_veterinario TEXT NOT NULL,
    motivo TEXT NOT NULL,
    data_consulta DATE NOT NULL,
    diagnostico TEXT,
    prescricoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Medicamentos
CREATE TABLE IF NOT EXISTS medicamentos (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    nome_remedio TEXT NOT NULL,
    dosagem TEXT NOT NULL,
    frequencia TEXT NOT NULL,
    horarios_admin TEXT,
    duracao INTEGER NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    concluido BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Preventivos
CREATE TABLE IF NOT EXISTS preventivos (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    nome_produto TEXT NOT NULL,
    tipo_preventivo TEXT NOT NULL,
    data_aplicacao DATE NOT NULL,
    proxima_dose DATE,
    concluido BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Peso
CREATE TABLE IF NOT EXISTS peso (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    data_pesagem DATE NOT NULL,
    peso DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Notas
CREATE TABLE IF NOT EXISTS notas (
    id BIGSERIAL PRIMARY KEY,
    pet TEXT NOT NULL,
    titulo TEXT NOT NULL,
    texto TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Habilitar Row Level Security (RLS) em todas as tabelas
ALTER TABLE pets ENABLE ROW LEVEL SECURITY;
ALTER TABLE vacinas ENABLE ROW LEVEL SECURITY;
ALTER TABLE alimentacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE veterinario ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE preventivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE peso ENABLE ROW LEVEL SECURITY;
ALTER TABLE notas ENABLE ROW LEVEL SECURITY;

-- Criar políticas para permitir todas as operações (ajustar conforme necessário)
-- Política para Pets
CREATE POLICY "Permitir tudo em pets" ON pets FOR ALL USING (true) WITH CHECK (true);

-- Política para Vacinas
CREATE POLICY "Permitir tudo em vacinas" ON vacinas FOR ALL USING (true) WITH CHECK (true);

-- Política para Alimentação
CREATE POLICY "Permitir tudo em alimentacao" ON alimentacao FOR ALL USING (true) WITH CHECK (true);

-- Política para Veterinário
CREATE POLICY "Permitir tudo em veterinario" ON veterinario FOR ALL USING (true) WITH CHECK (true);

-- Política para Medicamentos
CREATE POLICY "Permitir tudo em medicamentos" ON medicamentos FOR ALL USING (true) WITH CHECK (true);

-- Política para Preventivos
CREATE POLICY "Permitir tudo em preventivos" ON preventivos FOR ALL USING (true) WITH CHECK (true);

-- Política para Peso
CREATE POLICY "Permitir tudo em peso" ON peso FOR ALL USING (true) WITH CHECK (true);

-- Política para Notas
CREATE POLICY "Permitir tudo em notas" ON notas FOR ALL USING (true) WITH CHECK (true);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_pets_nome ON pets(nome);
CREATE INDEX IF NOT EXISTS idx_vacinas_pet ON vacinas(pet);
CREATE INDEX IF NOT EXISTS idx_alimentacao_pet ON alimentacao(pet);
CREATE INDEX IF NOT EXISTS idx_veterinario_pet ON veterinario(pet);
CREATE INDEX IF NOT EXISTS idx_medicamentos_pet ON medicamentos(pet);
CREATE INDEX IF NOT EXISTS idx_preventivos_pet ON preventivos(pet);
CREATE INDEX IF NOT EXISTS idx_peso_pet ON peso(pet);
CREATE INDEX IF NOT EXISTS idx_notas_pet ON notas(pet);
