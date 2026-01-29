import streamlit as st
from datetime import datetime, timedelta
import locale
import httpx
import json

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
# DEVE SER A PRIMEIRA LINHA EXECUTÁVEL DO STREAMLIT!
st.set_page_config(
    page_title="PetControl",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "PetControl - Sistema profissional de gerenciamento de pets"
    }
)

# ==================== CONFIGURAÇÃO DO SUPABASE ====================
# Buscar credenciais do st.secrets (APÓS set_page_config)
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
SUPABASE_API_URL = f'{SUPABASE_URL}/rest/v1'
SUPABASE_AUTH_URL = f'{SUPABASE_URL}/auth/v1'

# Headers para requisições ao Supabase (sem auth)
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Função para obter headers com token do usuário
def get_auth_headers():
    """Retorna headers com token de autenticação do usuário"""
    if 'access_token' in st.session_state:
        return {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {st.session_state.access_token}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    return SUPABASE_HEADERS

# ==================== FUNÇÕES DE AUTENTICAÇÃO ====================
def auth_login(email, password):
    """Fazer login do usuário"""
    try:
        response = httpx.post(
            f'{SUPABASE_AUTH_URL}/token?grant_type=password',
            json={'email': email, 'password': password},
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao fazer login: {str(e)}")
        return None

def auth_signup(email, password):
    """Criar nova conta de usuário"""
    try:
        response = httpx.post(
            f'{SUPABASE_AUTH_URL}/signup',
            json={'email': email, 'password': password},
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao criar conta: {str(e)}")
        return None

def auth_logout():
    """Fazer logout do usuário"""
    if 'access_token' in st.session_state:
        del st.session_state.access_token
    if 'user' in st.session_state:
        del st.session_state.user
    if 'user_profile' in st.session_state:
        del st.session_state.user_profile
    st.session_state.data_loaded = False

def get_user_profile():
    """Buscar perfil do usuário logado"""
    if 'user' not in st.session_state:
        return None

    try:
        user_id = st.session_state.user['id']
        url = f'{SUPABASE_API_URL}/profiles?id=eq.{user_id}'
        response = httpx.get(url, headers=get_auth_headers(), timeout=10.0)
        if response.status_code == 200:
            profiles = response.json()
            if profiles and len(profiles) > 0:
                return profiles[0]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar perfil: {str(e)}")
        return None

def check_user_authorized(email):
    """Verificar se o email está autorizado (existe em profiles com status ativo)"""
    try:
        url = f'{SUPABASE_API_URL}/profiles?email=eq.{email}&status=eq.ativo'
        response = httpx.get(url, headers=SUPABASE_HEADERS, timeout=10.0)
        if response.status_code == 200:
            profiles = response.json()
            return len(profiles) > 0
        return False
    except Exception:
        return False

# ==================== CONFIGURAÇÃO DE PLANOS ====================
# Definir planos disponíveis
PLANOS = {
    'Essencial': 1,
    'Plus': 4,
    'Elite': 15
}

# WhatsApp para upgrade (formato: 5511999999999)
WHATSAPP_NUMERO = '5591980389225'

# ==================== FUNÇÕES DO SUPABASE ====================
def supabase_get(table, filters=None):
    """Buscar dados de uma tabela do Supabase"""
    try:
        url = f'{SUPABASE_API_URL}/{table}'
        if filters:
            url += f'?{filters}'
        response = httpx.get(url, headers=get_auth_headers(), timeout=10.0)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return []

def supabase_post(table, data):
    """Inserir dados em uma tabela do Supabase"""
    try:
        # Adicionar user_id automaticamente
        if 'user' in st.session_state and 'user_id' not in data:
            data['user_id'] = st.session_state.user['id']

        url = f'{SUPABASE_API_URL}/{table}'
        response = httpx.post(url, headers=get_auth_headers(), json=data, timeout=10.0)
        if response.status_code in [200, 201]:
            return response.json()
        st.error(f"Erro ao salvar dados: {response.text}")
        return None
    except Exception as e:
        st.error(f"Erro ao salvar dados: {str(e)}")
        return None

def supabase_update(table, id_value, data):
    """Atualizar dados em uma tabela do Supabase"""
    try:
        url = f'{SUPABASE_API_URL}/{table}?id=eq.{id_value}'
        response = httpx.patch(url, headers=get_auth_headers(), json=data, timeout=10.0)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao atualizar dados: {str(e)}")
        return False

def supabase_delete(table, id_value):
    """Deletar dados de uma tabela do Supabase"""
    try:
        url = f'{SUPABASE_API_URL}/{table}?id=eq.{id_value}'
        response = httpx.delete(url, headers=get_auth_headers(), timeout=10.0)
        if response.status_code == 204:
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao deletar dados: {str(e)}")
        return False

def converter_data_para_string(obj):
    """Converter objetos date para string ISO"""
    if isinstance(obj, dict):
        return {k: converter_data_para_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [converter_data_para_string(item) for item in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj

def converter_string_para_data(obj):
    """Converter strings ISO de volta para objetos date/datetime"""
    from datetime import date as date_type
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if isinstance(v, str):
                # Tentar converter strings que parecem datas
                if k in ['data_nascimento', 'data_aplicacao', 'proxima_dose', 'data_consulta',
                         'data_inicio', 'data_fim', 'data_pesagem', 'data_dose']:
                    try:
                        result[k] = datetime.fromisoformat(v.replace('Z', '+00:00')).date()
                    except:
                        result[k] = v
                elif k in ['data_cadastro', 'data_registro', 'data_criacao', 'created_at']:
                    try:
                        result[k] = datetime.fromisoformat(v.replace('Z', '+00:00'))
                    except:
                        result[k] = v
                else:
                    result[k] = v
            else:
                result[k] = converter_string_para_data(v)
        return result
    elif isinstance(obj, list):
        return [converter_string_para_data(item) for item in obj]
    return obj

# Configurar locale para português brasileiro
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass  # Manter padrão se não conseguir configurar

# Configuração da página
st.set_page_config(
    page_title="PetControl",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado para o estilo visual
st.markdown("""
    <style>
    /* Fundo cinza claro */
    .stApp {
        background-color: #F5F5F5;
    }

    /* Header azul */
    header[data-testid="stHeader"] {
        background-color: #1E88E5;
        color: white;
    }

    /* Estilo das abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E88E5;
        padding: 10px;
        border-radius: 10px 10px 0 0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white;
        font-weight: 600;
        padding: 0 24px;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #1E88E5;
    }

    /* Botões arredondados */
    .stButton > button {
        border-radius: 25px;
        background-color: #1E88E5;
        color: white;
        font-weight: 600;
        padding: 12px 32px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #1976D2;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }

    /* Cards com sombra */
    .card {
        background-color: white;
        padding: 24px;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 16px 0;
    }

    /* Título principal */
    .main-title {
        color: #1E88E5;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: center;
    }

    /* Subtítulo */
    .subtitle {
        color: #666;
        font-size: 1.2em;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Input fields arredondados */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #E0E0E0;
        padding: 10px;
    }

    /* Remove padding padrão do Streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Alerta vermelho para preventivos vencidos */
    .alerta-vencido {
        color: #D32F2F;
        font-weight: 700;
        background-color: #FFEBEE;
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #D32F2F;
    }

    /* Selo de status concluído */
    .status-concluido {
        color: #2E7D32;
        font-weight: 700;
        background-color: #E8F5E9;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9em;
        border: 2px solid #2E7D32;
    }

    /* Selo de status pendente */
    .status-pendente {
        color: #F57C00;
        font-weight: 700;
        background-color: #FFF3E0;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9em;
        border: 2px solid #F57C00;
    }

    /* Aviso de limite de plano */
    .limite-aviso {
        color: #F57C00;
        font-weight: 600;
        background-color: #FFF8E1;
        padding: 12px 16px;
        border-radius: 10px;
        border-left: 4px solid #F57C00;
        margin: 16px 0;
    }

    /* Card de plano */
    .plano-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .plano-titulo {
        font-size: 1.5em;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .plano-info {
        font-size: 1.1em;
        margin: 8px 0;
    }

    /* Alertas de saúde - Semáforo */
    .pet-card-verde {
        border-left: 6px solid #4CAF50 !important;
        background: linear-gradient(to right, #E8F5E9 0%, white 10%);
    }

    .pet-card-amarelo {
        border-left: 6px solid #FFA726 !important;
        background: linear-gradient(to right, #FFF3E0 0%, white 10%);
    }

    .pet-card-vermelho {
        border-left: 6px solid #EF5350 !important;
        background: linear-gradient(to right, #FFEBEE 0%, white 10%);
    }

    .alerta-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 8px;
    }

    .badge-verde {
        background-color: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #4CAF50;
    }

    .badge-amarelo {
        background-color: #FFF3E0;
        color: #EF6C00;
        border: 1px solid #FFA726;
    }

    .badge-vermelho {
        background-color: #FFEBEE;
        color: #C62828;
        border: 1px solid #EF5350;
    }

    /* Barra de progresso de medicamentos */
    .progress-bar-container {
        width: 100%;
        height: 24px;
        background-color: #E0E0E0;
        border-radius: 12px;
        overflow: hidden;
        margin: 8px 0;
    }

    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50 0%, #66BB6A 100%);
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.85em;
    }

    .dose-checkbox-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0;
    }

    .dose-checkbox-item {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        background-color: #F5F5F5;
        border-radius: 6px;
        font-size: 0.9em;
    }

    /* Estilos para tela de login */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .login-logo {
        text-align: center;
        font-size: 3em;
        margin-bottom: 10px;
    }

    .login-title {
        text-align: center;
        color: #1E88E5;
        font-size: 2em;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .login-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }

    .logout-button {
        background-color: #EF5350 !important;
        color: white !important;
    }

    .logout-button:hover {
        background-color: #E53935 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Função para recarregar dados do Supabase
def recarregar_dados():
    """Recarregar todos os dados do Supabase"""
    st.session_state.pets = converter_string_para_data(supabase_get('pets') or [])
    st.session_state.vacinas = converter_string_para_data(supabase_get('vacinas') or [])
    st.session_state.alimentacao = converter_string_para_data(supabase_get('alimentacao') or [])
    st.session_state.veterinario = converter_string_para_data(supabase_get('veterinario') or [])
    st.session_state.medicamentos = converter_string_para_data(supabase_get('medicamentos') or [])
    st.session_state.preventivos = converter_string_para_data(supabase_get('preventivos') or [])
    st.session_state.peso = converter_string_para_data(supabase_get('peso') or [])
    st.session_state.notas = converter_string_para_data(supabase_get('notas') or [])
    st.session_state.medicamentos_log = converter_string_para_data(supabase_get('medicamentos_log') or [])

def calcular_status_saude(nome_pet):
    """Calcular status de saúde do pet baseado em vacinas e preventivos
    Retorna: ('vermelho', mensagem) | ('amarelo', mensagem) | ('verde', mensagem)
    """
    hoje = datetime.now().date()
    proximo_7_dias = hoje + timedelta(days=7)

    alertas = []
    nivel = 'verde'

    # Verificar vacinas
    vacinas_pet = [v for v in st.session_state.vacinas if v['pet'] == nome_pet]
    for vacina in vacinas_pet:
        if vacina.get('proxima_dose'):
            if vacina['proxima_dose'] < hoje:
                alertas.append(f"Vacina {vacina['nome_vacina']} vencida")
                nivel = 'vermelho'
            elif vacina['proxima_dose'] <= proximo_7_dias:
                if nivel != 'vermelho':
                    nivel = 'amarelo'
                alertas.append(f"Vacina {vacina['nome_vacina']} vence em breve")

    # Verificar preventivos
    preventivos_pet = [p for p in st.session_state.preventivos if p['pet'] == nome_pet]
    for preventivo in preventivos_pet:
        if preventivo.get('proxima_dose'):
            if preventivo['proxima_dose'] < hoje:
                alertas.append(f"{preventivo['tipo_preventivo']} vencido")
                nivel = 'vermelho'
            elif preventivo['proxima_dose'] <= proximo_7_dias:
                if nivel != 'vermelho':
                    nivel = 'amarelo'
                alertas.append(f"{preventivo['tipo_preventivo']} vence em breve")

    if nivel == 'verde':
        return ('verde', '✅ Tudo em dia')
    elif nivel == 'amarelo':
        return ('amarelo', f"⚠️ {', '.join(alertas[:2])}")
    else:
        return ('vermelho', f"🚨 {', '.join(alertas[:2])}")

# ==================== SISTEMA DE AUTENTICAÇÃO ====================
# Verificar se usuário está logado
if 'user' not in st.session_state:
    # Tela de Login
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">🐾</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">PetControl</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Gerencie a saúde dos seus pets com facilidade</p>', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Criar Conta"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="seu@email.com")
            password = st.text_input("Senha", type="password", placeholder="Sua senha")
            submit = st.form_submit_button("Entrar", use_container_width=True)

            if submit:
                if email and password:
                    # Tentar fazer login
                    result = auth_login(email, password)
                    if result:
                        st.session_state.user = result['user']
                        st.session_state.access_token = result['access_token']

                        # Buscar perfil do usuário
                        profile = get_user_profile()
                        if profile:
                            # Verificar se está ativo
                            if profile['status'] == 'ativo':
                                st.session_state.user_profile = profile
                                st.success("Login realizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("⚠️ Sua conta está inativa. Entre em contato para ativar seu plano.")
                                auth_logout()
                        else:
                            st.error("❌ Acesso negado. Seu email não está autorizado. Adquira um plano primeiro!")
                            auth_logout()
                    else:
                        st.error("Email ou senha incorretos")
                else:
                    st.warning("Preencha todos os campos")

    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Email", placeholder="seu@email.com", key="signup_email")
            new_password = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres", key="signup_password")
            confirm_password = st.text_input("Confirmar Senha", type="password", placeholder="Repita sua senha", key="signup_confirm")
            submit_signup = st.form_submit_button("Criar Conta", use_container_width=True)

            if submit_signup:
                if new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("As senhas não conferem")
                    elif len(new_password) < 6:
                        st.error("A senha deve ter no mínimo 6 caracteres")
                    else:
                        # Verificar se o email está autorizado
                        if check_user_authorized(new_email):
                            # Criar conta
                            result = auth_signup(new_email, new_password)
                            if result:
                                st.success("✅ Conta criada com sucesso! Faça login para continuar.")
                            else:
                                st.error("Erro ao criar conta. Tente novamente.")
                        else:
                            st.error("❌ Email não autorizado! Você precisa adquirir um plano primeiro.")
                            st.info("💡 Entre em contato via WhatsApp para adquirir seu plano e ter acesso ao PetControl!")

                            mensagem = "Olá! Gostaria de adquirir um plano do PetControl."
                            link_whatsapp = f"https://wa.me/{WHATSAPP_NUMERO}?text={mensagem.replace(' ', '%20')}"
                            st.markdown(
                                f'<a href="{link_whatsapp}" target="_blank"><button style="background-color: #25D366; color: white; padding: 12px 24px; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 10px;">📱 Falar no WhatsApp</button></a>',
                                unsafe_allow_html=True
                            )
                else:
                    st.warning("Preencha todos os campos")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()  # Parar execução aqui se não estiver logado

# Usuário está logado - carregar dados
# Buscar perfil e aplicar limite de plano
if 'user_profile' not in st.session_state:
    profile = get_user_profile()
    if profile and profile['status'] == 'ativo':
        st.session_state.user_profile = profile
    else:
        st.error("Sua conta está inativa. Faça login novamente.")
        auth_logout()
        st.rerun()

# Definir variáveis de plano baseadas no perfil do usuário
PLANO_USUARIO = st.session_state.user_profile['plano']
LIMITE_PETS = PLANOS[PLANO_USUARIO]

# Inicializar session state carregando dados do Supabase
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if not st.session_state.data_loaded:
    recarregar_dados()
    st.session_state.data_loaded = True

# Header com logo e botão de logout
col_header_1, col_header_2 = st.columns([4, 1])
with col_header_1:
    st.markdown('<h1 class="main-title">🐾 PetControl</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Gerencie a saúde dos seus pets com facilidade</p>', unsafe_allow_html=True)
with col_header_2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Sair", key="logout_btn"):
        auth_logout()
        st.rerun()

# Menu de abas
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🏠 Início",
    "💉 Vacinas",
    "🍎 Alimentação",
    "🏥 Veterinário",
    "💊 Medicamentos",
    "🛡️ Preventivos",
    "⚖️ Peso",
    "📝 Notas",
    "⚙️ Configurações"
])

# ==================== ABA INÍCIO ====================
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Bem-vindo ao PetControl!")
        st.write("Mantenha o controle completo da saúde dos seus pets.")

        # Botão de destaque para adicionar pet
        if st.button("➕ Adicionar Pet", use_container_width=True):
            # Verificar se atingiu o limite do plano ao clicar
            if len(st.session_state.pets) >= LIMITE_PETS:
                st.error(f"🚀 Seu plano {PLANO_USUARIO} permite até {LIMITE_PETS} pet{'s' if LIMITE_PETS > 1 else ''}. Para cadastrar mais, faça o upgrade!")
            else:
                st.session_state.show_add_pet_form = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Formulário para adicionar pet (aparece quando o botão é clicado)
    if st.session_state.get('show_add_pet_form', False):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Cadastrar Novo Pet")

        with st.form("add_pet_form"):
            col1, col2 = st.columns(2)

            with col1:
                nome_pet = st.text_input("Nome do Pet", placeholder="Ex: Rex")
                especie = st.selectbox("Espécie", ["Cão", "Gato", "Pássaro", "Outro"])
                raca = st.text_input("Raça", placeholder="Ex: Labrador")

            with col2:
                # Permitir datas desde 30 anos atrás até hoje
                data_minima = datetime.now().date() - timedelta(days=365*30)
                data_maxima = datetime.now().date()
                data_nascimento = st.date_input(
                    "Data de Nascimento",
                    value=datetime.now().date(),
                    min_value=data_minima,
                    max_value=data_maxima,
                    format="DD/MM/YYYY"
                )
                peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
                cor = st.text_input("Cor", placeholder="Ex: Marrom")

            observacoes = st.text_area("Observações", placeholder="Informações adicionais sobre o pet...")

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted = st.form_submit_button("Salvar Pet", use_container_width=True)

                if submitted:
                    novo_pet = {
                        'nome': nome_pet,
                        'especie': especie,
                        'raca': raca,
                        'data_nascimento': data_nascimento.isoformat(),
                        'peso': peso,
                        'cor': cor,
                        'observacoes': observacoes
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('pets', novo_pet)
                    if resultado:
                        st.session_state.show_add_pet_form = False
                        st.success(f"✅ Pet {nome_pet} cadastrado com sucesso!")
                        # Recarregar dados
                        recarregar_dados()
                        st.rerun()

        if st.button("Cancelar"):
            st.session_state.show_add_pet_form = False
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Exibir lista de pets cadastrados
    if st.session_state.pets:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🐾 Meus Pets")

        for pet in st.session_state.pets:
            # Calcular status de saúde
            nivel, mensagem = calcular_status_saude(pet['nome'])
            classe_card = f"pet-card-{nivel}"
            badge_classe = f"badge-{nivel}"

            # Container do pet com cor do semáforo
            st.markdown(f'<div style="padding: 12px; border-radius: 8px; margin: 12px 0;" class="{classe_card}">', unsafe_allow_html=True)

            with st.expander(f"**{pet['nome']}** - {pet['especie']}"):
                # Badge de status
                st.markdown(f'<span class="alerta-badge {badge_classe}">{mensagem}</span>', unsafe_allow_html=True)
                st.markdown("")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Raça:** {pet['raca']}")
                    st.write(f"**Cor:** {pet['cor']}")
                    st.write(f"**Peso:** {pet['peso']} kg")
                with col2:
                    st.write(f"**Data de Nascimento:** {pet['data_nascimento'].strftime('%d/%m/%Y')}")
                    idade_dias = (datetime.now().date() - pet['data_nascimento']).days
                    idade_anos = idade_dias // 365
                    st.write(f"**Idade:** {idade_anos} anos")

                if pet['observacoes']:
                    st.write(f"**Observações:** {pet['observacoes']}")

                st.markdown("---")
                if st.button(f"🗑️ Excluir Pet", key=f"del_pet_{pet['id']}"):
                    # Deletar pet do Supabase
                    if supabase_delete('pets', pet['id']):
                        # Deletar todos os registros relacionados a este pet
                        for v in st.session_state.vacinas:
                            if v['pet'] == pet['nome']:
                                supabase_delete('vacinas', v['id'])
                        for a in st.session_state.alimentacao:
                            if a['pet'] == pet['nome']:
                                supabase_delete('alimentacao', a['id'])
                        for v in st.session_state.veterinario:
                            if v['pet'] == pet['nome']:
                                supabase_delete('veterinario', v['id'])
                        for m in st.session_state.medicamentos:
                            if m['pet'] == pet['nome']:
                                supabase_delete('medicamentos', m['id'])
                        for p in st.session_state.preventivos:
                            if p['pet'] == pet['nome']:
                                supabase_delete('preventivos', p['id'])
                        for p in st.session_state.peso:
                            if p['pet'] == pet['nome']:
                                supabase_delete('peso', p['id'])
                        for n in st.session_state.notas:
                            if n['pet'] == pet['nome']:
                                supabase_delete('notas', n['id'])
                        # Recarregar dados
                        recarregar_dados()
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👋 Nenhum pet cadastrado ainda. Clique em 'Adicionar Pet' para começar!")

# ==================== ABA VACINAS ====================
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💉 Controle de Vacinas")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para registrar vacinas.")
    else:
        # Formulário para adicionar vacina
        with st.form("add_vacina_form"):
            st.markdown("#### Registrar Nova Vacina")

            col1, col2 = st.columns(2)

            with col1:
                pet_selecionado = st.selectbox(
                    "Selecione o Pet",
                    options=[pet['nome'] for pet in st.session_state.pets]
                )
                nome_vacina = st.text_input("Nome da Vacina", placeholder="Ex: V10, Antirrábica")
                data_aplicacao = st.date_input("Data de Aplicação", value=datetime.now(), format="DD/MM/YYYY")

            with col2:
                lote = st.text_input("Lote", placeholder="Número do lote")
                veterinario = st.text_input("Veterinário", placeholder="Nome do veterinário")
                proxima_dose = st.date_input("Próxima Dose", value=None, format="DD/MM/YYYY")

            observacoes_vacina = st.text_area("Observações", placeholder="Reações, informações adicionais...")

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_vacina = st.form_submit_button("Salvar Vacina", use_container_width=True)

                if submitted_vacina:
                    nova_vacina = {
                        'pet': pet_selecionado,
                        'nome_vacina': nome_vacina,
                        'data_aplicacao': data_aplicacao.isoformat(),
                        'lote': lote,
                        'veterinario': veterinario,
                        'proxima_dose': proxima_dose.isoformat() if proxima_dose else None,
                        'observacoes': observacoes_vacina,
                        'concluido': False
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('vacinas', nova_vacina)
                    if resultado:
                        st.success(f"✅ Vacina registrada para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir histórico de vacinas
        if st.session_state.vacinas:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Histórico de Vacinas")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets]
            )

            vacinas_filtradas = st.session_state.vacinas
            if pet_filtro != "Todos":
                vacinas_filtradas = [v for v in st.session_state.vacinas if v['pet'] == pet_filtro]

            for vacina in vacinas_filtradas:
                # Selo de status no título
                status_concluido = vacina.get('concluido', False)
                selo_status = "✅ CONCLUÍDO" if status_concluido else "⚠️ PENDENTE"
                classe_status = "status-concluido" if status_concluido else "status-pendente"

                with st.expander(f"**{vacina['pet']}** - {vacina['nome_vacina']} ({vacina['data_aplicacao'].strftime('%d/%m/%Y')})"):
                    # Exibir selo de status
                    st.markdown(f"<div class='{classe_status}'>{selo_status}</div>", unsafe_allow_html=True)
                    st.markdown("")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Lote:** {vacina['lote']}")
                        st.write(f"**Veterinário:** {vacina['veterinario']}")
                    with col2:
                        st.write(f"**Data de Aplicação:** {vacina['data_aplicacao'].strftime('%d/%m/%Y')}")
                        if vacina['proxima_dose']:
                            st.write(f"**Próxima Dose:** {vacina['proxima_dose'].strftime('%d/%m/%Y')}")

                    if vacina['observacoes']:
                        st.write(f"**Observações:** {vacina['observacoes']}")

                    st.markdown("---")

                    # Checkbox para marcar como concluído
                    novo_status = st.checkbox("Ação realizada?", value=status_concluido, key=f"status_vac_{vacina['id']}")
                    if novo_status != status_concluido:
                        # Atualizar no Supabase
                        if supabase_update('vacinas', vacina['id'], {'concluido': novo_status}):
                            recarregar_dados()
                            st.rerun()

                    if st.button(f"🗑️ Excluir", key=f"del_vac_{vacina['id']}"):
                        # Deletar do Supabase
                        if supabase_delete('vacinas', vacina['id']):
                            recarregar_dados()
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA ALIMENTAÇÃO ====================
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🍎 Controle de Alimentação")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para registrar a alimentação.")
    else:
        # Formulário para adicionar alimentação
        with st.form("add_alimentacao_form"):
            st.markdown("#### Registrar Plano Alimentar")

            col1, col2 = st.columns(2)

            with col1:
                pet_selecionado = st.selectbox(
                    "Selecione o Pet",
                    options=[pet['nome'] for pet in st.session_state.pets]
                )
                tipo_alimento = st.selectbox("Tipo de Alimento", ["Ração", "Úmida", "Natural", "Mista"])
                marca_nome = st.text_input("Marca/Nome", placeholder="Ex: Premier Golden")

            with col2:
                quantidade = st.number_input("Quantidade por Refeição (g)", min_value=0.0, step=10.0)
                frequencia = st.number_input("Frequência Diária", min_value=1, max_value=10, value=2)
                horarios = st.text_input("Horários", placeholder="Ex: 08:00, 18:00")

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_alimentacao = st.form_submit_button("Salvar Alimentação", use_container_width=True)

                if submitted_alimentacao:
                    nova_alimentacao = {
                        'pet': pet_selecionado,
                        'tipo_alimento': tipo_alimento,
                        'marca_nome': marca_nome,
                        'quantidade': quantidade,
                        'frequencia': frequencia,
                        'horarios': horarios,
                        'concluido': False
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('alimentacao', nova_alimentacao)
                    if resultado:
                        st.success(f"✅ Plano alimentar registrado para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir plano alimentar atual
        if st.session_state.alimentacao:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Plano Alimentar Atual")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets],
                key="filtro_alimentacao"
            )

            alimentacao_filtrada = st.session_state.alimentacao
            if pet_filtro != "Todos":
                alimentacao_filtrada = [a for a in st.session_state.alimentacao if a['pet'] == pet_filtro]

            for alimentacao in alimentacao_filtrada:
                # Selo de status
                status_concluido = alimentacao.get('concluido', False)
                selo_status = "✅ CONCLUÍDO" if status_concluido else "⚠️ PENDENTE"
                classe_status = "status-concluido" if status_concluido else "status-pendente"

                with st.expander(f"**{alimentacao['pet']}** - {alimentacao['tipo_alimento']} ({alimentacao['marca_nome']})"):
                    # Exibir selo de status
                    st.markdown(f"<div class='{classe_status}'>{selo_status}</div>", unsafe_allow_html=True)
                    st.markdown("")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {alimentacao['tipo_alimento']}")
                        st.write(f"**Marca/Nome:** {alimentacao['marca_nome']}")
                        st.write(f"**Quantidade por Refeição:** {alimentacao['quantidade']}g")
                    with col2:
                        st.write(f"**Frequência Diária:** {alimentacao['frequencia']}x")
                        st.write(f"**Horários:** {alimentacao['horarios']}")
                        st.write(f"**Registrado em:** {alimentacao['data_registro'].strftime('%d/%m/%Y')}")

                    st.markdown("---")

                    # Checkbox para marcar como concluído
                    novo_status = st.checkbox("Ação realizada?", value=status_concluido, key=f"status_alim_{alimentacao['id']}")
                    if novo_status != status_concluido:
                        # Atualizar no Supabase
                        if supabase_update('alimentacao', alimentacao['id'], {'concluido': novo_status}):
                            recarregar_dados()
                            st.rerun()

                    if st.button(f"🗑️ Excluir", key=f"del_alim_{alimentacao['id']}"):
                        # Deletar do Supabase
                        if supabase_delete('alimentacao', alimentacao['id']):
                            recarregar_dados()
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA VETERINÁRIO ====================
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🏥 Histórico Veterinário")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para registrar consultas.")
    else:
        # Formulário para adicionar consulta
        with st.form("add_veterinario_form"):
            st.markdown("#### Registrar Consulta Veterinária")

            col1, col2 = st.columns(2)

            with col1:
                pet_selecionado = st.selectbox(
                    "Selecione o Pet",
                    options=[pet['nome'] for pet in st.session_state.pets]
                )
                nome_veterinario = st.text_input("Nome do Veterinário/Clínica", placeholder="Dr. João Silva")
                motivo = st.selectbox("Motivo da Consulta", ["Rotina", "Emergência", "Retorno", "Cirurgia", "Exame"])

            with col2:
                data_consulta = st.date_input("Data da Consulta", value=datetime.now(), format="DD/MM/YYYY")
                diagnostico = st.text_input("Diagnóstico", placeholder="Ex: Saudável, Otite...")
                prescricoes = st.text_area("Prescrições", placeholder="Medicamentos prescritos...")

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_veterinario = st.form_submit_button("Salvar Consulta", use_container_width=True)

                if submitted_veterinario:
                    nova_consulta = {
                        'pet': pet_selecionado,
                        'nome_veterinario': nome_veterinario,
                        'motivo': motivo,
                        'data_consulta': data_consulta.isoformat(),
                        'diagnostico': diagnostico,
                        'prescricoes': prescricoes
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('veterinario', nova_consulta)
                    if resultado:
                        st.success(f"✅ Consulta registrada para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir histórico de consultas
        if st.session_state.veterinario:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Histórico de Consultas")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets],
                key="filtro_veterinario"
            )

            veterinario_filtrado = st.session_state.veterinario
            if pet_filtro != "Todos":
                veterinario_filtrado = [v for v in st.session_state.veterinario if v['pet'] == pet_filtro]

            # Ordenar por data (mais recente primeiro)
            veterinario_filtrado = sorted(veterinario_filtrado, key=lambda x: x['data_consulta'], reverse=True)

            for consulta in veterinario_filtrado:
                with st.expander(f"**{consulta['pet']}** - {consulta['motivo']} ({consulta['data_consulta'].strftime('%d/%m/%Y')})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Veterinário/Clínica:** {consulta['nome_veterinario']}")
                        st.write(f"**Motivo:** {consulta['motivo']}")
                        st.write(f"**Data:** {consulta['data_consulta'].strftime('%d/%m/%Y')}")
                    with col2:
                        st.write(f"**Diagnóstico:** {consulta['diagnostico']}")

                    if consulta['prescricoes']:
                        st.markdown("**Prescrições:**")
                        st.write(consulta['prescricoes'])

                    st.markdown("---")
                    if st.button(f"🗑️ Excluir", key=f"del_vet_{consulta['id']}"):
                        # Deletar do Supabase
                        if supabase_delete('veterinario', consulta['id']):
                            recarregar_dados()
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA MEDICAMENTOS ====================
with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💊 Controle de Medicamentos")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para registrar medicamentos.")
    else:
        # Formulário para adicionar medicamento
        with st.form("add_medicamento_form"):
            st.markdown("#### Registrar Medicamento")

            col1, col2 = st.columns(2)

            with col1:
                pet_selecionado = st.selectbox(
                    "Selecione o Pet",
                    options=[pet['nome'] for pet in st.session_state.pets]
                )
                nome_remedio = st.text_input("Nome do Remédio", placeholder="Ex: Amoxicilina")
                dosagem = st.text_input("Dosagem", placeholder="Ex: 5mg, 10ml")

            with col2:
                frequencia = st.text_input("Frequência", placeholder="Ex: 12/12h, 8/8h")
                doses_por_dia = st.number_input("Doses por Dia", min_value=1, max_value=10, value=2, help="Quantas vezes por dia o medicamento deve ser administrado")
                horarios_admin = st.text_input("Horários de Administração", placeholder="Ex: 08:00, 20:00")
                duracao = st.number_input("Duração do Tratamento (dias)", min_value=1, value=7)
                data_inicio = st.date_input("Data de Início", value=datetime.now(), format="DD/MM/YYYY")

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_medicamento = st.form_submit_button("Salvar Medicamento", use_container_width=True)

                if submitted_medicamento:
                    data_fim = datetime.combine(data_inicio, datetime.min.time()).date() + timedelta(days=duracao)
                    novo_medicamento = {
                        'pet': pet_selecionado,
                        'nome_remedio': nome_remedio,
                        'dosagem': dosagem,
                        'frequencia': frequencia,
                        'horarios_admin': horarios_admin,
                        'duracao': duracao,
                        'doses_por_dia': doses_por_dia,
                        'data_inicio': data_inicio.isoformat(),
                        'data_fim': data_fim.isoformat(),
                        'concluido': False
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('medicamentos', novo_medicamento)
                    if resultado:
                        # Criar log de doses (total = duracao * doses_por_dia)
                        medicamento_id = resultado[0]['id']
                        total_doses = duracao * doses_por_dia
                        for i in range(1, total_doses + 1):
                            dias_desde_inicio = (i - 1) // doses_por_dia
                            data_dose = data_inicio + timedelta(days=dias_desde_inicio)
                            log_dose = {
                                'medicamento_id': medicamento_id,
                                'numero_dose': i,
                                'data_dose': data_dose.isoformat(),
                                'realizado': False
                            }
                            supabase_post('medicamentos_log', log_dose)

                        st.success(f"✅ Medicamento registrado para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir medicamentos ativos
        if st.session_state.medicamentos:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 💊 Medicamentos Ativos")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets],
                key="filtro_medicamentos"
            )

            medicamentos_filtrados = st.session_state.medicamentos
            if pet_filtro != "Todos":
                medicamentos_filtrados = [m for m in st.session_state.medicamentos if m['pet'] == pet_filtro]

            # Separar ativos e finalizados
            hoje = datetime.now().date()
            medicamentos_ativos = [m for m in medicamentos_filtrados if m['data_fim'] >= hoje]
            medicamentos_finalizados = [m for m in medicamentos_filtrados if m['data_fim'] < hoje]

            if medicamentos_ativos:
                st.markdown("#### 🟢 Em Andamento")
                for medicamento in medicamentos_ativos:
                    # Buscar log de doses
                    doses_log = supabase_get('medicamentos_log', f"medicamento_id=eq.{medicamento['id']}")
                    doses_log = sorted(doses_log, key=lambda x: x['numero_dose']) if doses_log else []

                    # Calcular progresso
                    total_doses = len(doses_log)
                    doses_realizadas = sum(1 for d in doses_log if d.get('realizado', False))
                    percentual = (doses_realizadas / total_doses * 100) if total_doses > 0 else 0

                    with st.expander(f"**{medicamento['pet']}** - {medicamento['nome_remedio']} ({doses_realizadas}/{total_doses} doses)"):
                        # Barra de progresso
                        st.markdown(f"""
                        <div class='progress-bar-container'>
                            <div class='progress-bar-fill' style='width: {percentual}%;'>
                                {percentual:.0f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Remédio:** {medicamento['nome_remedio']}")
                            st.write(f"**Dosagem:** {medicamento['dosagem']}")
                            st.write(f"**Frequência:** {medicamento['frequencia']}")
                            if medicamento.get('horarios_admin'):
                                st.write(f"**Horários:** {medicamento['horarios_admin']}")
                        with col2:
                            st.write(f"**Duração:** {medicamento['duracao']} dias")
                            st.write(f"**Doses/dia:** {medicamento.get('doses_por_dia', 1)}")
                            st.write(f"**Início:** {medicamento['data_inicio'].strftime('%d/%m/%Y')}")
                            st.write(f"**Término:** {medicamento['data_fim'].strftime('%d/%m/%Y')}")

                        st.markdown("---")
                        st.markdown("**📋 Controle de Doses:**")

                        # Exibir apenas as próximas 10 doses não realizadas
                        doses_pendentes = [d for d in doses_log if not d.get('realizado', False)][:10]

                        if doses_pendentes:
                            for dose in doses_pendentes:
                                col_check, col_info = st.columns([1, 4])
                                with col_check:
                                    realizado = st.checkbox(
                                        "",
                                        value=dose.get('realizado', False),
                                        key=f"dose_{dose['id']}"
                                    )
                                    if realizado != dose.get('realizado', False):
                                        # Atualizar no Supabase
                                        if supabase_update('medicamentos_log', dose['id'], {'realizado': realizado}):
                                            recarregar_dados()
                                            st.rerun()
                                with col_info:
                                    data_dose_obj = datetime.fromisoformat(dose['data_dose'].replace('Z', '+00:00')).date() if isinstance(dose['data_dose'], str) else dose['data_dose']
                                    st.write(f"Dose {dose['numero_dose']}/{total_doses} - {data_dose_obj.strftime('%d/%m/%Y')}")

                            if len(doses_pendentes) < len([d for d in doses_log if not d.get('realizado', False)]):
                                st.info(f"Mostrando as próximas 10 doses. Total pendentes: {len([d for d in doses_log if not d.get('realizado', False)])}")
                        else:
                            st.success("✅ Todas as doses foram realizadas!")

                        st.markdown("---")

                        if st.button(f"🗑️ Excluir Medicamento", key=f"del_med_{medicamento['id']}"):
                            # Deletar log de doses primeiro
                            for dose in doses_log:
                                supabase_delete('medicamentos_log', dose['id'])
                            # Deletar medicamento do Supabase
                            if supabase_delete('medicamentos', medicamento['id']):
                                recarregar_dados()
                                st.rerun()

            if medicamentos_finalizados:
                st.markdown("#### ⚪ Finalizados")
                for medicamento in medicamentos_finalizados:
                    # Buscar log de doses
                    doses_log = supabase_get('medicamentos_log', f"medicamento_id=eq.{medicamento['id']}")
                    doses_log = sorted(doses_log, key=lambda x: x['numero_dose']) if doses_log else []

                    # Calcular progresso
                    total_doses = len(doses_log)
                    doses_realizadas = sum(1 for d in doses_log if d.get('realizado', False))
                    percentual = (doses_realizadas / total_doses * 100) if total_doses > 0 else 0

                    with st.expander(f"**{medicamento['pet']}** - {medicamento['nome_remedio']} (Finalizado - {doses_realizadas}/{total_doses})"):
                        # Barra de progresso
                        st.markdown(f"""
                        <div class='progress-bar-container'>
                            <div class='progress-bar-fill' style='width: {percentual}%;'>
                                {percentual:.0f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Remédio:** {medicamento['nome_remedio']}")
                            st.write(f"**Dosagem:** {medicamento['dosagem']}")
                        with col2:
                            st.write(f"**Início:** {medicamento['data_inicio'].strftime('%d/%m/%Y')}")
                            st.write(f"**Término:** {medicamento['data_fim'].strftime('%d/%m/%Y')}")

                        st.markdown("---")

                        if st.button(f"🗑️ Excluir", key=f"del_med_fin_{medicamento['id']}"):
                            # Deletar log de doses primeiro
                            for dose in doses_log:
                                supabase_delete('medicamentos_log', dose['id'])
                            # Deletar do Supabase
                            if supabase_delete('medicamentos', medicamento['id']):
                                recarregar_dados()
                                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA PREVENTIVOS ====================
with tab6:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🛡️ Preventivos (Antipulgas/Vermífugos)")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para registrar preventivos.")
    else:
        # Formulário para adicionar preventivo
        with st.form("add_preventivo_form"):
            st.markdown("#### Registrar Preventivo")

            col1, col2 = st.columns(2)

            with col1:
                pet_selecionado = st.selectbox(
                    "Selecione o Pet",
                    options=[pet['nome'] for pet in st.session_state.pets]
                )
                nome_produto = st.text_input("Nome do Produto", placeholder="Ex: Bravecto, Advocate")
                tipo_preventivo = st.selectbox("Tipo", ["Antipulgas", "Vermífugo", "Combo"])

            with col2:
                data_aplicacao = st.date_input("Data da Aplicação", value=datetime.now(), format="DD/MM/YYYY")
                proxima_dose = st.date_input("Data da Próxima Dose", value=None, format="DD/MM/YYYY")

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_preventivo = st.form_submit_button("Salvar Preventivo", use_container_width=True)

                if submitted_preventivo:
                    novo_preventivo = {
                        'pet': pet_selecionado,
                        'nome_produto': nome_produto,
                        'tipo_preventivo': tipo_preventivo,
                        'data_aplicacao': data_aplicacao.isoformat(),
                        'proxima_dose': proxima_dose.isoformat() if proxima_dose else None,
                        'concluido': False
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('preventivos', novo_preventivo)
                    if resultado:
                        st.success(f"✅ Preventivo registrado para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir histórico de preventivos
        if st.session_state.preventivos:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Histórico de Preventivos")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets],
                key="filtro_preventivos"
            )

            preventivos_filtrados = st.session_state.preventivos
            if pet_filtro != "Todos":
                preventivos_filtrados = [p for p in st.session_state.preventivos if p['pet'] == pet_filtro]

            # Ordenar por próxima dose
            preventivos_filtrados = sorted(preventivos_filtrados, key=lambda x: x['proxima_dose'] if x['proxima_dose'] else datetime.max.date())

            hoje = datetime.now().date()

            for preventivo in preventivos_filtrados:
                # Verificar se está vencido
                vencido = False
                if preventivo['proxima_dose'] and preventivo['proxima_dose'] < hoje:
                    vencido = True

                titulo = f"**{preventivo['pet']}** - {preventivo['nome_produto']} ({preventivo['tipo_preventivo']})"

                # Selo de status
                status_concluido = preventivo.get('concluido', False)
                selo_status = "✅ CONCLUÍDO" if status_concluido else "⚠️ PENDENTE"
                classe_status = "status-concluido" if status_concluido else "status-pendente"

                with st.expander(titulo):
                    # Exibir selo de status
                    st.markdown(f"<div class='{classe_status}'>{selo_status}</div>", unsafe_allow_html=True)
                    st.markdown("")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Produto:** {preventivo['nome_produto']}")
                        st.write(f"**Tipo:** {preventivo['tipo_preventivo']}")
                        st.write(f"**Data da Aplicação:** {preventivo['data_aplicacao'].strftime('%d/%m/%Y')}")
                    with col2:
                        if preventivo['proxima_dose']:
                            if vencido:
                                st.markdown(
                                    f"<div class='alerta-vencido'>⚠️ VENCIDO - Próxima Dose: {preventivo['proxima_dose'].strftime('%d/%m/%Y')}</div>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.write(f"**Próxima Dose:** {preventivo['proxima_dose'].strftime('%d/%m/%Y')}")
                                dias_restantes = (preventivo['proxima_dose'] - hoje).days
                                st.info(f"📅 Faltam {dias_restantes} dias")

                    st.markdown("---")

                    # Checkbox para marcar como concluído
                    novo_status = st.checkbox("Ação realizada?", value=status_concluido, key=f"status_prev_{preventivo['id']}")
                    if novo_status != status_concluido:
                        # Atualizar no Supabase
                        if supabase_update('preventivos', preventivo['id'], {'concluido': novo_status}):
                            recarregar_dados()
                            st.rerun()

                    if st.button(f"🗑️ Excluir", key=f"del_prev_{preventivo['id']}"):
                        # Deletar do Supabase
                        if supabase_delete('preventivos', preventivo['id']):
                            recarregar_dados()
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA PESO ====================
with tab7:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚖️ Controle de Peso")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para registrar pesagens.")
    else:
        # Formulário para adicionar pesagem
        with st.form("add_peso_form"):
            st.markdown("#### Registrar Pesagem")

            col1, col2, col3 = st.columns(3)

            with col1:
                pet_selecionado = st.selectbox(
                    "Selecione o Pet",
                    options=[pet['nome'] for pet in st.session_state.pets]
                )
            with col2:
                data_pesagem = st.date_input("Data da Pesagem", value=datetime.now(), format="DD/MM/YYYY")
            with col3:
                peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_peso = st.form_submit_button("Salvar Pesagem", use_container_width=True)

                if submitted_peso:
                    nova_pesagem = {
                        'pet': pet_selecionado,
                        'data_pesagem': data_pesagem.isoformat(),
                        'peso': peso
                    }
                    # Salvar no Supabase
                    resultado = supabase_post('peso', nova_pesagem)
                    if resultado:
                        st.success(f"✅ Pesagem registrada para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir histórico de peso
        if st.session_state.peso:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📊 Histórico de Peso")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets],
                key="filtro_peso"
            )

            peso_filtrado = st.session_state.peso
            if pet_filtro != "Todos":
                peso_filtrado = [p for p in st.session_state.peso if p['pet'] == pet_filtro]

            # Ordenar por data (mais recente primeiro)
            peso_filtrado = sorted(peso_filtrado, key=lambda x: x['data_pesagem'], reverse=True)

            for idx, pesagem in enumerate(peso_filtrado):
                # Calcular variação em relação à pesagem anterior
                variacao = ""
                if idx < len(peso_filtrado) - 1:
                    peso_anterior = peso_filtrado[idx + 1]['peso']
                    diferenca = pesagem['peso'] - peso_anterior
                    if diferenca > 0:
                        variacao = f"📈 +{diferenca:.2f}kg"
                    elif diferenca < 0:
                        variacao = f"📉 {diferenca:.2f}kg"
                    else:
                        variacao = "➡️ Manteve"

                with st.expander(f"**{pesagem['pet']}** - {pesagem['peso']}kg ({pesagem['data_pesagem'].strftime('%d/%m/%Y')}) {variacao}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Data:** {pesagem['data_pesagem'].strftime('%d/%m/%Y')}")
                        st.write(f"**Peso:** {pesagem['peso']}kg")
                    with col2:
                        if variacao:
                            st.write(f"**Variação:** {variacao}")

                    st.markdown("---")
                    if st.button(f"🗑️ Excluir", key=f"del_peso_{pesagem['id']}"):
                        # Deletar do Supabase
                        if supabase_delete('peso', pesagem['id']):
                            recarregar_dados()
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA NOTAS ====================
with tab8:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📝 Notas e Observações")

    if not st.session_state.pets:
        st.warning("⚠️ Cadastre um pet primeiro na aba 'Início' para criar notas.")
    else:
        # Formulário para adicionar nota
        with st.form("add_nota_form"):
            st.markdown("#### Criar Nova Nota")

            pet_selecionado = st.selectbox(
                "Selecione o Pet",
                options=[pet['nome'] for pet in st.session_state.pets]
            )
            titulo_nota = st.text_input("Título da Nota", placeholder="Ex: Comportamento estranho")
            texto_nota = st.text_area("Texto da Nota", placeholder="Descreva a observação...", height=150)

            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted_nota = st.form_submit_button("Salvar Nota", use_container_width=True)

                if submitted_nota:
                    nova_nota = {
                        'pet': pet_selecionado,
                        'titulo': titulo_nota,
                        'texto': texto_nota
                    }
                    # Salvar no Supabase (data_criacao é automático no banco)
                    resultado = supabase_post('notas', nova_nota)
                    if resultado:
                        st.success(f"✅ Nota criada para {pet_selecionado}!")
                        recarregar_dados()
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Exibir notas
        if st.session_state.notas:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Notas Salvas")

            # Filtro por pet
            pet_filtro = st.selectbox(
                "Filtrar por Pet",
                ["Todos"] + [pet['nome'] for pet in st.session_state.pets],
                key="filtro_notas"
            )

            notas_filtradas = st.session_state.notas
            if pet_filtro != "Todos":
                notas_filtradas = [n for n in st.session_state.notas if n['pet'] == pet_filtro]

            # Ordenar por data (mais recente primeiro)
            notas_filtradas = sorted(notas_filtradas, key=lambda x: x['data_criacao'], reverse=True)

            for nota in notas_filtradas:
                with st.expander(f"**{nota['pet']}** - {nota['titulo']} ({nota['data_criacao'].strftime('%d/%m/%Y')})"):
                    st.write(f"**Título:** {nota['titulo']}")
                    st.write(f"**Data:** {nota['data_criacao'].strftime('%d/%m/%Y')}")
                    st.markdown("**Observação:**")
                    st.write(nota['texto'])

                    st.markdown("---")
                    if st.button(f"🗑️ Excluir", key=f"del_nota_{nota['id']}"):
                        # Deletar do Supabase
                        if supabase_delete('notas', nota['id']):
                            recarregar_dados()
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== ABA CONFIGURAÇÕES ====================
with tab9:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Configurações")

    # Informações do Plano
    st.markdown("#### 💎 Plano Atual")

    # Card visual do plano
    pets_cadastrados = len(st.session_state.pets)
    percentual_uso = (pets_cadastrados / LIMITE_PETS * 100) if LIMITE_PETS > 0 else 0

    st.markdown(
        f"""
        <div class='plano-card'>
            <div class='plano-titulo'>Plano {PLANO_USUARIO}</div>
            <div class='plano-info'>🐾 Pets Cadastrados: {pets_cadastrados} / {LIMITE_PETS}</div>
            <div class='plano-info'>📊 Uso: {percentual_uso:.0f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar informações sobre planos disponíveis
    st.markdown("#### 📋 Planos Disponíveis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("**Essencial**\n\n🐾 1 pet\n\n✅ Recursos Completos")
    with col2:
        st.info("**Plus**\n\n🐾 4 pets\n\n✅ Recursos Completos")
    with col3:
        st.info("**Elite**\n\n🐾 15 pets\n\n✅ Recursos Completos")

    if pets_cadastrados >= LIMITE_PETS:
        st.warning(f"⚠️ Você atingiu o limite do seu plano {PLANO_USUARIO}. Faça upgrade para cadastrar mais pets!")

        # Link do WhatsApp para upgrade
        mensagem_whatsapp = f"Olá! Gostaria de fazer upgrade do meu plano {PLANO_USUARIO} no PetControl."
        link_whatsapp = f"https://wa.me/{WHATSAPP_NUMERO}?text={mensagem_whatsapp.replace(' ', '%20')}"

        st.markdown(
            f'<a href="{link_whatsapp}" target="_blank"><button style="background-color: #25D366; color: white; padding: 12px 24px; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">📱 Fazer Upgrade via WhatsApp</button></a>',
            unsafe_allow_html=True
        )
    else:
        vagas_restantes = LIMITE_PETS - pets_cadastrados
        st.success(f"✅ Você ainda pode cadastrar {vagas_restantes} pet{'s' if vagas_restantes > 1 else ''}.")

    st.markdown("---")

    st.markdown("#### 🔌 Conexão com Supabase")
    st.info("🚧 A conexão com Supabase será implementada aqui.")

    with st.expander("📝 Configurar Supabase"):
        supabase_url = st.text_input("Supabase URL", placeholder="https://seu-projeto.supabase.co")
        supabase_key = st.text_input("Supabase Key", type="password", placeholder="sua-api-key")

        if st.button("💾 Salvar Configurações"):
            st.success("✅ Configurações salvas! (Em desenvolvimento)")

    st.markdown("---")

    st.markdown("#### 📊 Dados da Aplicação")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Pets", len(st.session_state.pets))
        st.metric("Vacinas", len(st.session_state.vacinas))
        st.metric("Veterinário", len(st.session_state.veterinario))
    with col2:
        st.metric("Alimentação", len(st.session_state.alimentacao))
        st.metric("Medicamentos", len(st.session_state.medicamentos))
        st.metric("Preventivos", len(st.session_state.preventivos))
    with col3:
        st.metric("Pesagens", len(st.session_state.peso))
        st.metric("Notas", len(st.session_state.notas))

    st.markdown("---")

    st.markdown("#### 🗑️ Gerenciar Dados")
    st.warning("⚠️ Atenção: As ações abaixo são irreversíveis!")

    if st.button("🗑️ Limpar Todos os Dados", use_container_width=True):
        # Deletar todos os dados do Supabase
        for pet in st.session_state.pets:
            supabase_delete('pets', pet['id'])
        for vacina in st.session_state.vacinas:
            supabase_delete('vacinas', vacina['id'])
        for alim in st.session_state.alimentacao:
            supabase_delete('alimentacao', alim['id'])
        for vet in st.session_state.veterinario:
            supabase_delete('veterinario', vet['id'])
        for med in st.session_state.medicamentos:
            supabase_delete('medicamentos', med['id'])
        for prev in st.session_state.preventivos:
            supabase_delete('preventivos', prev['id'])
        for p in st.session_state.peso:
            supabase_delete('peso', p['id'])
        for nota in st.session_state.notas:
            supabase_delete('notas', nota['id'])

        # Recarregar dados
        recarregar_dados()
        st.success("✅ Todos os dados foram limpos!")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>PetControl v1.0 - Desenvolvido com ❤️</p>",
    unsafe_allow_html=True
)
