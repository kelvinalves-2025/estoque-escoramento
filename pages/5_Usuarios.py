import pandas as pd
import streamlit as st

from auth import exigir_login
from db import consultar, salvar, lembrar, mostrar_aviso
from formatos import data_br

exigir_login(somente_admin=True)
st.title("Usuários")
mostrar_aviso()
st.caption("Para criar um usuário novo, cadastre o e-mail e a senha no painel do Supabase (veja o passo a passo). "
           "Ele aparece aqui como INATIVO; ative e defina o perfil. Usuários não são excluídos, só desativados.")

PERFIS = {"operador": "Operador", "admin": "Administrador"}
usuarios = consultar("perfis", "*", "nome")

st.dataframe(pd.DataFrame([{"Nome": u["nome"], "Função": u["funcao"] or "—", "Perfil": PERFIS[u["perfil"]],
                            "Situação": "Ativo" if u["ativo"] else "Inativo",
                            "Criado em": data_br(u["criado_em"])} for u in usuarios]),
             use_container_width=True, hide_index=True)

i = st.selectbox("Editar usuário", range(len(usuarios)), format_func=lambda k: usuarios[k]["nome"])
u = usuarios[i]
with st.form(f"edit_user_{u['id']}"):
    nome = st.text_input("Nome", value=u["nome"])
    funcao = st.text_input("Função (ex.: Encarregado, Técnico)", value=u["funcao"] or "")
    perfil_novo = st.selectbox("Perfil", list(PERFIS), format_func=PERFIS.get, index=list(PERFIS).index(u["perfil"]))
    ativo = st.checkbox("Ativo", value=u["ativo"])
    if st.form_submit_button("Salvar"):
        if not nome.strip():
            st.error("Informe o nome.")
        else:
            ok, r = salvar("perfis", {"nome": nome.strip(), "funcao": funcao.strip() or None,
                                      "perfil": perfil_novo, "ativo": ativo}, u["id"])
            if ok:
                lembrar("Usuário atualizado. Mudanças de perfil valem no próximo login da pessoa.")
                st.rerun()
            else:
                st.error(r)
