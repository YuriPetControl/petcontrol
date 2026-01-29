# 🐾 PetControl - Sistema de Gerenciamento de Pets

Sistema completo para gerenciar a saúde e bem-estar dos seus pets, com controle de vacinas, medicamentos, alimentação e muito mais.

## 🚀 Funcionalidades

- ✅ **Sistema de Autenticação** - Login seguro com integração Supabase
- 🚦 **Alerta de Saúde** - Semáforo visual indicando status de vacinas e preventivos
- 💊 **Controle de Medicamentos** - Sistema de doses com progresso visual
- 💉 **Controle de Vacinas** - Histórico completo de vacinação
- 🍎 **Gestão de Alimentação** - Planejamento alimentar
- 🏥 **Histórico Veterinário** - Registro de consultas e diagnósticos
- 🛡️ **Preventivos** - Controle de antipulgas e vermífugos
- ⚖️ **Controle de Peso** - Acompanhamento com gráficos
- 📝 **Notas** - Observações personalizadas
- 📊 **Planos Flexíveis** - Essencial (1 pet), Plus (4 pets), Elite (15 pets)

## 🛠️ Tecnologias

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth
- **Segurança**: Row Level Security (RLS)
- **Webhooks**: Integração com Kiwify/Hotmart

## 📦 Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/SEU-USUARIO/PetControl_V2.git
cd PetControl_V2
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo de secrets:
```bash
# Renomeie o arquivo de exemplo
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edite com suas credenciais do Supabase
# .streamlit/secrets.toml
```

4. Execute o Supabase Setup:
- Acesse seu projeto no [Supabase](https://supabase.com)
- Execute os scripts SQL na ordem:
  1. `supabase_auth_setup.sql`
  2. `supabase_updates.sql`

5. Execute o aplicativo:
```bash
streamlit run app.py
```

## ☁️ Deploy no Streamlit Community Cloud

1. Faça fork/clone deste repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório GitHub
4. Configure os **Secrets** no painel:
   ```toml
   [supabase]
   url = "https://SEU-PROJETO.supabase.co"
   key = "SUA-CHAVE-ANON-AQUI"
   ```
5. Deploy automático!

## 🔐 Configuração do Supabase

### 1. Criar Projeto
- Acesse [supabase.com](https://supabase.com)
- Crie um novo projeto
- Anote a URL e a chave `anon/public`

### 2. Executar Scripts SQL
No SQL Editor do Supabase, execute na ordem:

1. **supabase_auth_setup.sql** - Cria tabelas e políticas RLS
2. **supabase_updates.sql** - Adiciona sistema de doses de medicamentos

### 3. Habilitar Email Auth
- Authentication > Providers > Email
- Desabilite "Confirm Email" (opcional)

### 4. Configurar Webhooks (Opcional)
Para integração com plataformas de venda:
- Deploy a Edge Function: `edge_function_webhook.ts`
- Configure webhook na Kiwify/Hotmart
- Veja instruções em `SISTEMA_LOGIN_WEBHOOKS.md`

## 📚 Documentação

- [**SISTEMA_LOGIN_WEBHOOKS.md**](SISTEMA_LOGIN_WEBHOOKS.md) - Guia completo de autenticação e webhooks
- [**ATUALIZACOES_V2.md**](ATUALIZACOES_V2.md) - Novidades da versão 2.0
- [**edge_function_webhook.ts**](edge_function_webhook.ts) - Código da Edge Function

## 🔒 Segurança

- ✅ Row Level Security (RLS) habilitado em todas as tabelas
- ✅ Credenciais via `st.secrets` (nunca hardcoded)
- ✅ Autenticação JWT com Supabase Auth
- ✅ Dados isolados por usuário (`user_id`)

## 💳 Sistema de Planos

| Plano | Pets | Recursos |
|-------|------|----------|
| Essencial | 1 | Completos |
| Plus | 4 | Completos |
| Elite | 15 | Completos |

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma [issue](https://github.com/SEU-USUARIO/PetControl_V2/issues)
- Entre em contato via WhatsApp (configurado no sistema)

## 🎉 Créditos

Desenvolvido com ❤️ usando Streamlit e Supabase.

---

**PetControl v2.0** - Gerencie a saúde dos seus pets com facilidade! 🐾
