# 🔐 Sistema de Login e Integração com Plataformas de Venda

## 📋 Visão Geral

O PetControl agora possui um sistema completo de autenticação com controle de acesso baseado em compras externas (Kiwify, Hotmart, etc).

### Como Funciona

1. **Cliente compra** um plano na Kiwify/Hotmart
2. **Webhook** envia dados para o Supabase
3. **Email é autorizado** na tabela `profiles`
4. **Cliente cria conta** no PetControl
5. **Acesso liberado** com limite baseado no plano adquirido

## 🗄️ Estrutura do Banco de Dados

### Tabela `profiles`

Armazena informações dos usuários autorizados:

```sql
- id: UUID (referência ao auth.users)
- email: TEXT (email do usuário)
- plano: TEXT ('Essencial', 'Plus', 'Elite')
- status: TEXT ('ativo', 'inativo', 'cancelado')
- data_compra: TIMESTAMP
- data_expiracao: TIMESTAMP
- webhook_source: TEXT ('kiwify', 'hotmart', 'manual')
- webhook_data: JSONB (dados completos do webhook)
```

## 🚀 Configuração Inicial

### 1. Executar SQL no Supabase

No SQL Editor do Supabase, execute:
```bash
supabase_auth_setup.sql
```

Este script:
- Cria a tabela `profiles`
- Adiciona campo `user_id` em todas as tabelas
- Configura políticas RLS (Row Level Security)
- Cria triggers automáticos

### 2. Habilitar Email Authentication

No Supabase Dashboard:
1. Vá em **Authentication** > **Providers**
2. Habilite **Email**
3. Desabilite "Confirm Email" se quiser acesso imediato
4. Configure email templates (opcional)

### 3. Configurar URL de Redirecionamento

Em **Authentication** > **URL Configuration**:
```
Site URL: http://localhost:8501
Redirect URLs: http://localhost:8501
```

## 💳 Integrando com Plataformas de Venda

### Opção 1: Kiwify (Recomendado)

#### Passo 1: Criar Produto na Kiwify

1. Acesse [Kiwify](https://dashboard.kiwify.com.br)
2. Crie 3 produtos (Essencial, Plus, Elite)
3. Configure preços e descrições

#### Passo 2: Configurar Webhook

Na Kiwify, configure webhook para:
```
URL: https://SEU-PROJETO.supabase.co/functions/v1/kiwify-webhook
```

#### Passo 3: Criar Edge Function no Supabase

Crie uma Edge Function (`supabase/functions/kiwify-webhook/index.ts`):

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const payload = await req.json()

    // Mapear produto para plano
    const planMap = {
      'PROD_ID_ESSENCIAL': 'Essencial',
      'PROD_ID_PLUS': 'Plus',
      'PROD_ID_ELITE': 'Elite'
    }

    const plano = planMap[payload.Product.id] || 'Essencial'
    const email = payload.Customer.email
    const status = payload.order_status === 'paid' ? 'ativo' : 'inativo'

    // Buscar ou criar usuário
    const { data: user } = await supabase.auth.admin.getUserByEmail(email)

    let userId = user?.id

    if (!userId) {
      // Criar usuário se não existe
      const { data: newUser } = await supabase.auth.admin.createUser({
        email: email,
        email_confirm: true
      })
      userId = newUser?.user?.id
    }

    if (userId) {
      // Inserir ou atualizar profile
      const { error } = await supabase
        .from('profiles')
        .upsert({
          id: userId,
          email: email,
          plano: plano,
          status: status,
          webhook_source: 'kiwify',
          webhook_data: payload
        })

      if (error) throw error
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' }
    })

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    })
  }
})
```

#### Passo 4: Deploy da Edge Function

```bash
supabase functions deploy kiwify-webhook
```

### Opção 2: Hotmart

Similar à Kiwify, mas ajuste o payload conforme documentação da Hotmart.

### Opção 3: Manual (Para Testes)

Adicionar usuários manualmente via SQL:

```sql
-- 1. Criar usuário no auth
INSERT INTO auth.users (email, encrypted_password, email_confirmed_at)
VALUES ('teste@exemplo.com', crypt('senha123', gen_salt('bf')), NOW());

-- 2. Pegar o ID gerado
SELECT id FROM auth.users WHERE email = 'teste@exemplo.com';

-- 3. Criar profile
INSERT INTO profiles (id, email, plano, status)
VALUES ('ID-DO-USUARIO', 'teste@exemplo.com', 'Plus', 'ativo');
```

## 🔒 Segurança - Row Level Security (RLS)

### O que é RLS?

Row Level Security garante que cada usuário veja apenas seus próprios dados.

### Políticas Implementadas

Todas as tabelas possuem 4 políticas:

1. **SELECT**: `auth.uid() = user_id`
2. **INSERT**: `auth.uid() = user_id`
3. **UPDATE**: `auth.uid() = user_id`
4. **DELETE**: `auth.uid() = user_id`

### Como Funciona

```
Usuário A (id: abc-123) → Vê apenas registros com user_id = abc-123
Usuário B (id: def-456) → Vê apenas registros com user_id = def-456
```

## 🎯 Fluxo de Uso

### 1. Novo Cliente

```mermaid
Cliente → Compra na Kiwify
Kiwify → Webhook para Supabase
Supabase → Cria profile com plano 'Plus'
Cliente → Acessa PetControl
Cliente → Cria conta com mesmo email
PetControl → Valida email autorizado
PetControl → Libera acesso com limite de 4 pets
```

### 2. Cliente Existente

```
Cliente → Faz login
PetControl → Busca profile
PetControl → Aplica limite do plano
Cliente → Usa normalmente
```

### 3. Upgrade de Plano

```
Cliente → Compra novo plano na Kiwify
Webhook → Atualiza profile (Plus → Elite)
Cliente → Faz logout e login novamente
PetControl → Aplica novo limite (15 pets)
```

## 📱 Interface do Sistema

### Tela de Login

- **Tab "Login"**: Para usuários que já têm conta
- **Tab "Criar Conta"**: Para primeiro acesso

### Validações

1. ✅ Email deve estar na tabela `profiles`
2. ✅ Status deve ser `ativo`
3. ✅ Senha mínima de 6 caracteres

### Mensagens

- ✅ **Autorizado**: Acesso liberado
- ❌ **Não autorizado**: Direciona para WhatsApp
- ⚠️ **Inativo**: Pede contato para reativação

## 🔧 Troubleshooting

### Erro: "Email não autorizado"

**Causa**: Email não está na tabela `profiles`

**Solução**:
```sql
-- Verificar se profile existe
SELECT * FROM profiles WHERE email = 'email@exemplo.com';

-- Se não existe, criar manualmente
INSERT INTO profiles (id, email, plano, status)
VALUES ('USER-UUID', 'email@exemplo.com', 'Plus', 'ativo');
```

### Erro: "Sua conta está inativa"

**Causa**: Status não é `ativo`

**Solução**:
```sql
UPDATE profiles
SET status = 'ativo'
WHERE email = 'email@exemplo.com';
```

### Usuário não vê seus dados

**Causa**: RLS bloqueando acesso

**Solução**:
```sql
-- Verificar se user_id está preenchido
SELECT id, nome, user_id FROM pets WHERE user_id IS NULL;

-- Atualizar user_id manualmente se necessário
UPDATE pets SET user_id = 'USER-UUID' WHERE id = PET-ID;
```

## 🚨 Importante

### Antes de Colocar em Produção

1. ✅ Teste com usuários reais
2. ✅ Configure emails do Supabase Auth
3. ✅ Teste webhooks com compras reais
4. ✅ Backup do banco de dados
5. ✅ Configure domínio personalizado

### Manutenção

- Monitore webhooks no Supabase Functions
- Verifique logs de erro
- Atualize edge functions quando necessário

## 📞 Suporte

Para configurar webhooks ou dúvidas técnicas:
- WhatsApp configurado no sistema
- Documentação Supabase: https://supabase.com/docs
- Documentação Kiwify: https://docs.kiwify.com.br

## 🎉 Resultado Final

Com este sistema, você terá:

✅ Login seguro com email/senha
✅ Controle de acesso por plano
✅ Integração automática com vendas
✅ Dados isolados por usuário
✅ Escalável para milhares de usuários
✅ Zero manutenção manual de acessos
