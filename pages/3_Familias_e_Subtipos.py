import re

import pandas as pd
import streamlit as st

from auth import exigir_login
from db import consultar, salvar, lembrar, mostrar_aviso

perfil = exigir_login()
admin = perfil["perfil"] == "admin"
st.title("Famílias e Subtipos")
st.caption("O código do material é FAM-SUB-NNNN: 3 letras da família, 3 letras do subtipo e um número sequencial.")
mostrar_aviso()

familias = consultar("familias", "*", "codigo")
subtipos = consultar("subtipos", "*, familias(codigo, nome)")
subtipos.sort(key=lambda s: (s["familias"]["codigo"], s["codigo"]))
CODIGO = re.compile(r"^[A-Z]{3}$")

aba_lista, aba_fam, aba_sub = st.tabs(["Lista", "Famílias", "Subtipos"])

with aba_lista:
    st.dataframe(pd.DataFrame([{"Família": f"{s['familias']['codigo']} — {s['familias']['nome']}",
                                "Subtipo": f"{s['codigo']} — {s['nome']}",
                                "Último nº usado": s["ultimo_numero"],
                                "Situação": "Ativo" if s["ativo"] else "Inativo"} for s in subtipos]),
                 use_container_width=True, hide_index=True)
    st.write("**Famílias:** " + ", ".join(f"{f['codigo']} ({f['nome']})" for f in familias))

with aba_fam:
    if not admin:
        st.info("Só o administrador altera famílias.")
    else:
        with st.form("nova_familia", clear_on_submit=True):
            c1, c2 = st.columns([1, 3])
            cod = c1.text_input("Código (3 letras maiúsculas)", max_chars=3).upper()
            nome = c2.text_input("Nome da família")
            if st.form_submit_button("Cadastrar família"):
                if not CODIGO.match(cod) or not nome.strip():
                    st.error("Informe 3 letras para o código (A-Z, sem acento) e o nome.")
                else:
                    ok, r = salvar("familias", {"codigo": cod, "nome": nome.strip()})
                    if ok:
                        lembrar(f"Família {cod} cadastrada.")
                        st.rerun()
                    else:
                        st.error(r)
        st.divider()
        i = st.selectbox("Editar família", range(len(familias)),
                         format_func=lambda k: f"{familias[k]['codigo']} — {familias[k]['nome']}")
        f = familias[i]
        with st.form(f"edit_fam_{f['id']}"):
            novo_nome = st.text_input("Nome", value=f["nome"])
            ativo = st.checkbox("Ativa", value=f["ativo"])
            if st.form_submit_button("Salvar"):
                ok, r = salvar("familias", {"nome": novo_nome.strip(), "ativo": ativo}, f["id"])
                if ok:
                    lembrar("Família atualizada.")
                    st.rerun()
                else:
                    st.error(r)

with aba_sub:
    if not admin:
        st.info("Só o administrador altera subtipos.")
    else:
        fam_ativas = [f for f in familias if f["ativo"]]
        with st.form("novo_subtipo", clear_on_submit=True):
            fam = st.selectbox("Família", fam_ativas, format_func=lambda f: f"{f['codigo']} — {f['nome']}")
            c1, c2 = st.columns([1, 3])
            cod = c1.text_input("Código do subtipo (3 letras)", max_chars=3).upper()
            nome = c2.text_input("Nome do subtipo (ex.: Escora metálica extensível)")
            if st.form_submit_button("Cadastrar subtipo"):
                if not CODIGO.match(cod) or not nome.strip():
                    st.error("Informe 3 letras para o código (A-Z, sem acento) e o nome.")
                else:
                    ok, r = salvar("subtipos", {"familia_id": fam["id"], "codigo": cod, "nome": nome.strip()})
                    if ok:
                        lembrar(f"Subtipo {fam['codigo']}-{cod} cadastrado.")
                        st.rerun()
                    else:
                        st.error(r)
        if subtipos:
            st.divider()
            i = st.selectbox("Editar subtipo", range(len(subtipos)),
                             format_func=lambda k: f"{subtipos[k]['familias']['codigo']}-{subtipos[k]['codigo']} — {subtipos[k]['nome']}")
            s = subtipos[i]
            with st.form(f"edit_sub_{s['id']}"):
                novo_nome = st.text_input("Nome", value=s["nome"])
                ativo = st.checkbox("Ativo", value=s["ativo"])
                if st.form_submit_button("Salvar"):
                    ok, r = salvar("subtipos", {"nome": novo_nome.strip(), "ativo": ativo}, s["id"])
                    if ok:
                        lembrar("Subtipo atualizado.")
                        st.rerun()
                    else:
                        st.error(r)
