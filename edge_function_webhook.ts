// ==================== EDGE FUNCTION PARA WEBHOOK ====================
// Arquivo: supabase/functions/webhook/index.ts
// Deploy: supabase functions deploy webhook

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  // Permitir CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    })
  }

  try {
    // Inicializar cliente Supabase com service role
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    const payload = await req.json()
    console.log('Webhook recebido:', JSON.stringify(payload))

    // ==================== KIWIFY ====================
    if (payload.Product) {
      return await handleKiwify(supabase, payload)
    }

    // ==================== HOTMART ====================
    if (payload.event) {
      return await handleHotmart(supabase, payload)
    }

    // ==================== OUTRO FORMATO ====================
    return new Response(
      JSON.stringify({ error: 'Formato de webhook não reconhecido' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Erro no webhook:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})

// ==================== HANDLER KIWIFY ====================
async function handleKiwify(supabase, payload) {
  // Mapear IDs de produtos para planos
  // IMPORTANTE: Substitua pelos IDs reais dos seus produtos na Kiwify
  const planMap = {
    'prod_xxxxxxxxx': 'Essencial',  // ID do produto Essencial
    'prod_yyyyyyyyy': 'Plus',       // ID do produto Plus
    'prod_zzzzzzzzz': 'Elite'       // ID do produto Elite
  }

  const productId = payload.Product?.id
  const plano = planMap[productId] || 'Essencial'
  const email = payload.Customer?.email
  const orderStatus = payload.order_status
  const status = orderStatus === 'paid' ? 'ativo' : 'inativo'

  if (!email) {
    throw new Error('Email não encontrado no payload')
  }

  console.log(`Processando Kiwify: ${email} - Plano: ${plano} - Status: ${status}`)

  // Buscar usuário existente
  const { data: existingUser } = await supabase.auth.admin.getUserByEmail(email)

  let userId = existingUser?.id

  // Se usuário não existe, criar
  if (!userId) {
    console.log(`Criando novo usuário: ${email}`)
    const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
      email: email,
      email_confirm: true, // Confirmar email automaticamente
      user_metadata: {
        source: 'kiwify',
        plano: plano
      }
    })

    if (createError) throw createError
    userId = newUser?.user?.id
  }

  if (!userId) {
    throw new Error('Falha ao obter ID do usuário')
  }

  // Upsert no profile
  const { error: profileError } = await supabase
    .from('profiles')
    .upsert({
      id: userId,
      email: email,
      plano: plano,
      status: status,
      webhook_source: 'kiwify',
      webhook_data: payload,
      updated_at: new Date().toISOString()
    }, {
      onConflict: 'id'
    })

  if (profileError) throw profileError

  console.log(`✅ Profile atualizado: ${email}`)

  return new Response(
    JSON.stringify({
      success: true,
      message: 'Webhook processado com sucesso',
      user_id: userId,
      plano: plano,
      status: status
    }),
    { headers: { 'Content-Type': 'application/json' } }
  )
}

// ==================== HANDLER HOTMART ====================
async function handleHotmart(supabase, payload) {
  // Mapear produtos da Hotmart
  const planMap = {
    'PROD_XXXXX': 'Essencial',
    'PROD_YYYYY': 'Plus',
    'PROD_ZZZZZ': 'Elite'
  }

  const event = payload.event
  const productId = payload.data?.product?.id
  const email = payload.data?.buyer?.email
  const plano = planMap[productId] || 'Essencial'

  // Status baseado no evento
  let status = 'inativo'
  if (event === 'PURCHASE_APPROVED') {
    status = 'ativo'
  } else if (event === 'PURCHASE_CANCELED' || event === 'PURCHASE_REFUNDED') {
    status = 'cancelado'
  }

  if (!email) {
    throw new Error('Email não encontrado no payload')
  }

  console.log(`Processando Hotmart: ${email} - Evento: ${event} - Plano: ${plano}`)

  // Mesmo fluxo da Kiwify
  const { data: existingUser } = await supabase.auth.admin.getUserByEmail(email)
  let userId = existingUser?.id

  if (!userId) {
    const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
      email: email,
      email_confirm: true,
      user_metadata: {
        source: 'hotmart',
        plano: plano
      }
    })

    if (createError) throw createError
    userId = newUser?.user?.id
  }

  if (!userId) throw new Error('Falha ao obter ID do usuário')

  const { error: profileError } = await supabase
    .from('profiles')
    .upsert({
      id: userId,
      email: email,
      plano: plano,
      status: status,
      webhook_source: 'hotmart',
      webhook_data: payload,
      updated_at: new Date().toISOString()
    }, {
      onConflict: 'id'
    })

  if (profileError) throw profileError

  return new Response(
    JSON.stringify({
      success: true,
      message: 'Webhook Hotmart processado',
      user_id: userId,
      plano: plano,
      status: status
    }),
    { headers: { 'Content-Type': 'application/json' } }
  )
}

// ==================== INSTRUÇÕES DE USO ====================
/*

1. CRIAR A FUNÇÃO NO SUPABASE:

   supabase functions new webhook

2. COPIAR ESTE CÓDIGO para supabase/functions/webhook/index.ts

3. ATUALIZAR OS IDs DOS PRODUTOS:
   - Substitua 'prod_xxxxxxxxx' pelos IDs reais da Kiwify/Hotmart

4. DEPLOY:

   supabase functions deploy webhook --no-verify-jwt

5. CONFIGURAR WEBHOOK NA PLATAFORMA:

   URL: https://SEU-PROJETO.supabase.co/functions/v1/webhook

6. TESTAR:

   curl -X POST https://SEU-PROJETO.supabase.co/functions/v1/webhook \
     -H "Content-Type: application/json" \
     -d '{"Product":{"id":"prod_xxxxxxxxx"},"Customer":{"email":"teste@exemplo.com"},"order_status":"paid"}'

*/
