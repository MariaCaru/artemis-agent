"""
app.py — Interface web do Agent Moon (Streamlit).

Rodar com:
    streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent.core import PersonalAgent
from agent import memory as mem_module

# ---------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Agent Moon",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_OPTIONS = {
    "Ollama (local)": "local",
    "Groq": "groq",
    "Hugging Face": "huggingface",
    "DeepSeek": "deepseek",
}

TOOL_GROUPS = {
    "📁 Organização": ["save_note", "list_files", "run_safe_command"],
    "🔐 Segurança de Dados": [
        "encrypt_file", "decrypt_file", "check_password_strength",
        "hash_text", "generate_password",
    ],
    "🛡️ Pentest": [
        "nmap_scan", "port_scan_python", "http_headers",
        "ssl_cert_info", "check_robots_txt", "ping_host",
    ],
    "💻 Código": [
        "read_file", "list_project_tree", "search_in_code",
        "git_diff", "git_log",
    ],
}

# ---------------------------------------------------------------
# Session state
# ---------------------------------------------------------------
def _init_state():
    defaults = {
        "messages": [],
        "agent": None,
        "agent_signature": None,
        "backend_label": "Groq",
        "enable_routing": True,
        "session_id": mem_module.new_session_id(),
        "show_history": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ---------------------------------------------------------------
# Agente
# ---------------------------------------------------------------
def get_agent():
    """Cria ou reutiliza o agente, recriando se configs mudarem."""
    backend_type = BACKEND_OPTIONS[st.session_state.backend_label]
    routing = (
        st.session_state.enable_routing
        and backend_type != "local"
    )
    signature = (backend_type, routing, st.session_state.session_id)

    if st.session_state.agent is None or st.session_state.agent_signature != signature:
        st.session_state.agent = PersonalAgent(
            backend_type=backend_type,
            enable_routing=routing,
            default_backend=backend_type,
            session_id=st.session_state.session_id,
        )
        st.session_state.agent_signature = signature
    return st.session_state.agent

# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌙 Agent Moon")
    st.caption("Assistente pessoal — organização, segurança, pentest e código")

    st.divider()

    st.markdown("### ⚙️ Configuração")
    st.session_state.backend_label = st.selectbox(
        "Backend padrão",
        options=list(BACKEND_OPTIONS.keys()),
        index=list(BACKEND_OPTIONS.keys()).index(st.session_state.backend_label),
    )

    is_local = st.session_state.backend_label == "Ollama (local)"
    st.session_state.enable_routing = st.checkbox(
        "Roteamento automático (local ↔ nuvem)",
        value=st.session_state.enable_routing,
        disabled=is_local,
        help="Perguntas sensíveis vão para o Ollama local; demais vão para o backend padrão.",
    )
    if is_local and st.session_state.enable_routing:
        st.session_state.enable_routing = False

    st.divider()

    st.markdown("### 🧰 Ferramentas")
    for group_name, tools in TOOL_GROUPS.items():
        with st.expander(group_name, expanded=False):
            for t in tools:
                st.markdown(f"- `{t}`")

    st.divider()

    st.markdown("### 💬 Sessão")
    st.caption(f"ID: `{st.session_state.session_id}`")
    total = mem_module.count_messages()
    st.caption(f"Mensagens no histórico: {total}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nova sessão", use_container_width=True):
            st.session_state.session_id = mem_module.new_session_id()
            st.session_state.messages = []
            st.session_state.agent = None
            st.session_state.agent_signature = None
            st.rerun()
    with col2:
        if st.button("🧹 Limpar chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if st.button("📜 Ver histórico", use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history

    if st.session_state.show_history:
        st.markdown("#### Últimas mensagens")
        rows = mem_module.get_session_history(st.session_state.session_id, limit=20)
        if not rows:
            st.caption("Nenhuma mensagem nesta sessão ainda.")
        for row in rows:
            role = "**Você:**" if row["role"] == "user" else "**Agente:**"
            content = row["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            st.markdown(f"{role} {content}")

# ---------------------------------------------------------------
# Área principal — chat
# ---------------------------------------------------------------
st.markdown("## 💬 Chat")

# Renderiza histórico da sessão
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        meta = msg.get("metadata")
        if meta and meta.get("tools"):
            tool_names = [t["name"] for t in meta["tools"]]
            with st.expander(
                f"🔧 {len(tool_names)} ferramenta(s) · backend: {meta.get('backend')}"
            ):
                for t in meta["tools"]:
                    st.markdown(f"**`{t['name']}`** — entrada: `{t['input']}`")
                    obs = t["observation"]
                    st.code(obs[:800] + ("..." if len(obs) > 800 else ""), language=None)

# Input
user_input = st.chat_input("Digite sua mensagem...")

if user_input:
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Processa
    agent = get_agent()
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = agent.ask(user_input)
                meta = getattr(agent, "last_turn_metadata", None)
            except Exception as e:
                response = f"⚠️ Erro: {e}"
                meta = None

        st.markdown(response)
        if meta and meta.get("tools"):
            tool_names = [t["name"] for t in meta["tools"]]
            with st.expander(
                f"🔧 {len(tool_names)} ferramenta(s) · backend: {meta.get('backend')}"
            ):
                for t in meta["tools"]:
                    st.markdown(f"**`{t['name']}`** — entrada: `{t['input']}`")
                    obs = t["observation"]
                    st.code(obs[:800] + ("..." if len(obs) > 800 else ""), language=None)

    # Salva no session_state
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "metadata": meta,
    })