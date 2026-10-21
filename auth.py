"""Login, sessão e controle de acesso. Cada pessoa tem o próprio cliente Supabase
(guardado na sessão do Streamlit), para que o login de um nunca vaze para outro."""
import streamlit as st
from supabase import create_client


def cliente():
    if "sb" not in st.session_state:
        st.session_state["sb"] = create_client(
            st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"]
        )
    return st.session_state["sb"]


def _tela_login():
    st.title("Estoque de Escoramento")
    st.subheader("Entrar")
    with st.form("login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        enviar = st.form_submit_button("Entrar")
    if not enviar:
        return
    sb = cliente()
    try:
        resp = sb.auth.sign_in_with_password({"email": email.strip(), "password": senha})
        dados = sb.table("perfis").select("*").eq("id", resp.user.id).execute().data
    except Exception as erro:
        st.error("Não foi possível entrar. Verifique e-mail e senha.")
        st.caption(f"Detalhe técnico: {type(erro).__name__}")
        return
    if not dados or not dados[0]["ativo"]:
        sb.auth.sign_out()
        st.error("Usuário sem acesso. Fale com o administrador.")
        return
    st.session_state["perfil"] = dados[0]
    st.rerun()


def sair():
    try:
        cliente().auth.sign_out()
    except Exception:
        pass
    st.session_state.clear()
    st.rerun()


def exigir_login(somente_admin=False):
    """Chamar na primeira linha de cada página. Devolve o perfil do usuário."""
    st.set_page_config(page_title="Estoque de Escoramento", layout="wide")
    perfil = st.session_state.get("perfil")
    if not perfil:
        _tela_login()
        st.stop()
    with st.sidebar:
        st.write(f"**{perfil['nome']}**")
        st.caption("Administrador" if perfil["perfil"] == "admin" else "Operador")
        if st.button("Sair"):
            sair()
    if somente_admin and perfil["perfil"] != "admin":
        st.warning("Esta página é só para o administrador.")
        st.stop()
    return perfil
