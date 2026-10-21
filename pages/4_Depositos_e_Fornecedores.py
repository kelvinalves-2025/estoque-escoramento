import pandas as pd
import streamlit as st

from auth import exigir_login
from db import consultar, salvar, lembrar, mostrar_aviso

perfil = exigir_login()
admin = perfil["perfil"] == "admin"
st.title("Depósitos e Fornecedores/Locadores")
mostrar_aviso()

TIPOS = {"fornecedor": "Fornecedor", "locador": "Locador", "ambos": "Fornecedor e locador"}
depositos = consultar("depositos", "*", "nome")
fornecedores = consultar("fornecedores", "*", "nome")

aba_dep, aba_for = st.tabs(["Depósitos", "Fornecedores/Locadores"])

with aba_dep:
    st.dataframe(pd.DataFrame([{"Depósito": d["nome"], "Endereço": d["endereco"] or "—",
                                "Situação": "Ativo" if d["ativo"] else "Inativo"} for d in depositos]),
                 use_container_width=True, hide_index=True)
    if admin:
        with st.form("novo_dep", clear_on_submit=True):
            nome = st.text_input("Novo depósito")
            end = st.text_input("Endereço")
            if st.form_submit_button("Cadastrar depósito"):
                if not nome.strip():
                    st.error("Informe o nome.")
                else:
                    ok, r = salvar("depositos", {"nome": nome.strip(), "endereco": end.strip() or None})
                    if ok:
                        lembrar("Depósito cadastrado.")
                        st.rerun()
                    else:
                        st.error(r)

with aba_for:
    st.dataframe(pd.DataFrame([{"Nome": f["nome"], "Tipo": TIPOS[f["tipo"]], "Contato": f["contato"] or "—",
                                "Situação": "Ativo" if f["ativo"] else "Inativo"} for f in fornecedores]),
                 use_container_width=True, hide_index=True)
    if admin:
        with st.form("novo_for", clear_on_submit=True):
            nome = st.text_input("Nome do fornecedor/locador")
            tipo = st.selectbox("Tipo", list(TIPOS), format_func=TIPOS.get)
            contato = st.text_input("Contato")
            if st.form_submit_button("Cadastrar"):
                if not nome.strip():
                    st.error("Informe o nome.")
                else:
                    ok, r = salvar("fornecedores", {"nome": nome.strip(), "tipo": tipo, "contato": contato.strip() or None})
                    if ok:
                        lembrar("Cadastrado.")
                        st.rerun()
                    else:
                        st.error(r)
        if fornecedores:
            st.divider()
            i = st.selectbox("Ativar/desativar", range(len(fornecedores)), format_func=lambda k: fornecedores[k]["nome"])
            f = fornecedores[i]
            with st.form(f"edit_for_{f['id']}"):
                ativo = st.checkbox("Ativo", value=f["ativo"])
                contato = st.text_input("Contato", value=f["contato"] or "")
                if st.form_submit_button("Salvar"):
                    ok, r = salvar("fornecedores", {"ativo": ativo, "contato": contato.strip() or None}, f["id"])
                    if ok:
                        lembrar("Atualizado.")
                        st.rerun()
                    else:
                        st.error(r)
