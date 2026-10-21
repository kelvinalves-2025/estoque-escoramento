"""Acesso ao banco. A segurança de verdade está no banco (RLS); aqui só
organizamos leitura, gravação e mensagens de erro em português."""
import streamlit as st
from postgrest.exceptions import APIError

from auth import cliente


def consultar(tabela, colunas="*", ordem=None):
    """Lê a tabela inteira (paginando de 1000 em 1000)."""
    tudo, ini, passo = [], 0, 1000
    while True:
        q = (cliente().table(tabela).select(colunas)
             .order(ordem or "id").range(ini, ini + passo - 1))
        lote = q.execute().data
        tudo += lote
        if len(lote) < passo:
            return tudo
        ini += passo


def _traduzir(erro):
    codigo = getattr(erro, "code", None)
    msg = getattr(erro, "message", None) or str(erro)
    if codigo == "23505":
        return "Já existe um registro com esse nome ou código."
    if codigo == "23514":
        return "Algum valor não é permitido. Revise os campos."
    if codigo == "23503":
        return "Este registro está ligado a outros e não pode ser alterado assim."
    if codigo == "42501":
        return "Sem permissão para esta operação."
    return msg  # mensagens escritas nas regras do banco já estão em português


def salvar(tabela, dados, id_=None):
    """Insere (id_ None) ou atualiza. Devolve (True, registro) ou (False, mensagem)."""
    try:
        t = cliente().table(tabela)
        r = t.insert(dados).execute() if id_ is None else t.update(dados).eq("id", id_).execute()
    except APIError as erro:
        return False, _traduzir(erro)
    if not r.data:
        return False, "Nada foi gravado. Verifique suas permissões."
    return True, r.data[0]


def lembrar(msg):
    st.session_state["_aviso"] = msg


def mostrar_aviso():
    msg = st.session_state.pop("_aviso", None)
    if msg:
        st.success(msg)
