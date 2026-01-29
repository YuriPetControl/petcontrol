# 🚀 Guia de Deploy - PetControl no Streamlit Community Cloud

## 📋 Pré-requisitos

- Conta no [GitHub](https://github.com)
- Conta no [Streamlit Community Cloud](https://share.streamlit.io)
- Projeto Supabase configurado

## 🔧 Passo 1: Preparar Repositório Local

Todos os arquivos já estão prontos:
- ✅ `requirements.txt` - Dependências do projeto
- ✅ `app.py` - Usando `st.secrets` (seguro)
- ✅ `.gitignore` - Protege seus secrets
- ✅ `.streamlit/secrets.toml` - Secrets locais (NÃO vai pro GitHub)
- ✅ `README.md` - Documentação do projeto

## 💻 Passo 2: Subir para GitHub (Terminal do Cursor)

Abra o terminal integrado no Cursor (Ctrl + `) e execute:

### 2.1 - Inicializar Git
```bash
cd c:\Users\Thalis\Desktop\PetControl_V2
git init
```

### 2.2 - Adicionar Arquivos
```bash
git add .
```

**Verificar o que vai ser commitado:**
```bash
git status
```

Você deve ver:
- ✅ Arquivos em verde (vão ser commitados)
- ❌ `.streamlit/secrets.toml` NÃO deve aparecer (está no .gitignore)

### 2.3 - Fazer Primeiro Commit
```bash
git commit -m "Initial commit: PetControl V2 com autenticação e controle de saúde"
```

### 2.4 - Criar Repositório no GitHub

**Opção A: Pela Interface Web (Recomendado)**
1. Acesse https://github.com/new
2. Nome do repositório: `PetControl_V2`
3. Descrição: `Sistema de gerenciamento de pets com Streamlit e Supabase`
4. Deixe como **Público** ou **Privado** (sua escolha)
5. ❌ NÃO marque "Add a README file"
6. Clique em "Create repository"

**Opção B: Via GitHub CLI (se tiver instalado)**
```bash
gh repo create PetControl_V2 --public --source=. --remote=origin
```

### 2.5 - Conectar ao Repositório Remoto

Copie os comandos que o GitHub mostrou, algo como:

```bash
git remote add origin https://github.com/SEU-USUARIO/PetControl_V2.git
git branch -M main
git push -u origin main
```

**Ou se já tiver remote configurado:**
```bash
git push -u origin main
```

### 2.6 - Verificar Upload
```bash
git remote -v
```

Acesse seu repositório no GitHub para confirmar que os arquivos foram enviados.

## ☁️ Passo 3: Deploy no Streamlit Community Cloud

### 3.1 - Acessar Streamlit Cloud
1. Vá para https://share.streamlit.io
2. Faça login com sua conta GitHub
3. Clique em "New app"

### 3.2 - Configurar App
- **Repository**: Selecione `SEU-USUARIO/PetControl_V2`
- **Branch**: `main`
- **Main file path**: `app.py`
- **App URL (custom)**: `petcontrol` (ou o nome que preferir)

### 3.3 - Configurar Secrets

Clique em **"Advanced settings"** > **"Secrets"**

Cole o seguinte conteúdo (substitua com suas credenciais reais do Supabase):

```toml
[supabase]
url = "https://yxrlxgvikzxuybvzxkmv.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4cmx4Z3Zpa3p4dXlidnp4a212Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MDMyMjMsImV4cCI6MjA4NTI3OTIyM30.JTe2z8j6helV04LTQjfKmKcVuN1QUHv0g22yrO-9ZNg"
```

### 3.4 - Deploy!
1. Clique em **"Deploy!"**
2. Aguarde alguns minutos (o Streamlit vai instalar as dependências)
3. Seu app estará disponível em: `https://SEU-APP.streamlit.app`

## 🔄 Atualizações Futuras

Sempre que fizer mudanças no código:

```bash
# 1. Adicionar arquivos modificados
git add .

# 2. Commitar
git commit -m "Descrição das mudanças"

# 3. Enviar para GitHub
git push
```

O Streamlit Cloud detecta automaticamente e faz **redeploy automático**!

## ✅ Verificações Pós-Deploy

### Testar Login
1. Acesse seu app no Streamlit Cloud
2. Tente criar uma conta (deve falhar se email não autorizado)
3. Use um email que está na tabela `profiles` com status `ativo`
4. Faça login com sucesso

### Verificar Logs
- No Streamlit Cloud, clique em "Manage app" > "Logs"
- Veja se há erros de conexão com Supabase

### Testar RLS
1. Faça login com dois usuários diferentes
2. Cadastre pets em cada conta
3. Verifique que cada usuário vê apenas seus próprios dados

## 🚨 Troubleshooting

### Erro: "No module named 'httpx'"
- Verifique se `requirements.txt` foi commitado corretamente
- Force rebuild no Streamlit Cloud

### Erro: "KeyError: 'supabase'"
- Secrets não foram configurados corretamente
- Vá em "Manage app" > "Settings" > "Secrets"
- Reconfigure os secrets do Supabase

### Erro: "Failed to connect to Supabase"
- Verifique se a URL e KEY estão corretas
- Confirme que o projeto Supabase está ativo
- Verifique se RLS está habilitado (pode estar bloqueando)

### App não atualiza após push
- Vá em "Manage app" > "Reboot app"
- Ou faça commit vazio: `git commit --allow-empty -m "Trigger rebuild"`

## 📱 Compartilhar App

Seu app está disponível publicamente em:
```
https://SEU-APP.streamlit.app
```

Compartilhe esse link com seus clientes!

## 🔐 Segurança

✅ **O que está seguro:**
- Secrets do Supabase (não estão no GitHub)
- Código fonte (público, mas sem credenciais)
- Autenticação JWT (tokens não expostos)

❌ **NÃO commite:**
- `.streamlit/secrets.toml`
- Arquivos `.env`
- Qualquer credencial ou token

## 🎉 Pronto!

Seu PetControl está no ar! 🚀

Para dúvidas ou problemas:
- [Documentação Streamlit](https://docs.streamlit.io/streamlit-community-cloud)
- [Documentação Supabase](https://supabase.com/docs)
