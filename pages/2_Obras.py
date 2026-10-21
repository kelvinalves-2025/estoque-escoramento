from datetime import date

import pandas as pd
import streamlit as st

from auth import exigir_login
from db import consultar, salvar, lembrar, mostrar_aviso
from formatos import data_br

perfil = exigir_login()
admin = perfil["perfil"] == "admin"
st.title("Obras")
mostrar_aviso()

SITUACOES = {"planejada": "Planejada", "ativa": "Ativa", "concluida": "Concluída"}
obras = consultar("obras", "*", "nome")


def _data(txt):
    return date.fromisoformat(txt) if txt else None


def form_obra(chave, ini, novo):
    ini = ini or {}
    with st.form(chave, clear_on_submit=novo):
        nome = st.text_input("Nome da obra", value=ini.get("nome", ""))
        c1, c2 = st.columns(2)
        contrato = c1.text_input("Contrato", value=ini.get("contrato") or "")
        situ = c2.selectbox("Situação", list(SITUACOES), format_func=SITUACOES.get,
                            index=list(SITUACOES).index(ini.get("situacao", "planejada")))
        endereco = st.text_input("Endereço", value=ini.get("endereco") or "")
        d1, d2 = st.columns(2)
        inicio = d1.date_input("Início previsto", value=_data(ini.get("data_inicio_prevista")), format="DD/MM/YYYY")
        fim = d2.date_input("Fim previsto", value=_data(ini.get("data_fim_prevista")), format="DD/MM/YYYY")
        ativo = True if novo else st.checkbox("Obra ativa no cadastro", value=ini.get("ativo", True))
        enviado = st.form_submit_button("Cadastrar obra" if novo else "Salvar alterações")
    if not enviado:
        return None
    if not nome.strip():
        st.error("Informe o nome da obra.")
        return None
    if inicio and fim and fim < inicio:
        st.error("O fim previsto não pode ser anterior ao início.")
        return None
    return {"nome": nome.strip(), "contrato": contrato.strip() or None, "situacao": situ,
            "endereco": endereco.strip() or None,
            "data_inicio_prevista": inicio.isoformat() if inicio else None,
            "data_fim_prevista": fim.isoformat() if fim else None, "ativo": ativo}


aba_lista, aba_novo, aba_editar = st.tabs(["Lista", "Nova obra", "Editar obra"])

with aba_lista:
    if not obras:
        st.info("Nenhuma obra cadastrada.")
    else:
        df = pd.DataFrame([{
            "Obra": o["nome"], "Contrato": o["contrato"] or "—", "Situação": SITUACOES[o["situacao"]],
            "Início previsto": data_br(o["data_inicio_prevista"]), "Fim previsto": data_br(o["data_fim_prevista"]),
            "Cadastro": "Ativo" if o["ativo"] else "Inativo"} for o in obras])
        st.dataframe(df, use_container_width=True, hide_index=True)

with aba_novo:
    if not admin:
        st.info("Só o administrador cadastra obras.")
    else:
        dados = form_obra("nova_obra", None, True)
        if dados:
            ok, r = salvar("obras", dados)
            if ok:
                lembrar(f"Obra '{r['nome']}' cadastrada.")
                st.rerun()
            else:
                st.error(r)

with aba_editar:
    if not admin:
        st.info("Só o administrador edita obras.")
    elif not obras:
        st.info("Nenhuma obra para editar.")
    else:
        i = st.selectbox("Obra", range(len(obras)), format_func=lambda k: obras[k]["nome"])
        dados = form_obra(f"editar_obra_{obras[i]['id']}", obras[i], False)
        if dados:
            ok, r = salvar("obras", dados, obras[i]["id"])
            if ok:
                lembrar("Obra atualizada.")
                st.rerun()
            else:
                st.error(r)
