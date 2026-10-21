import streamlit as st

from auth import exigir_login
from db import consultar

perfil = exigir_login()

st.title("Estoque de Escoramento")
st.write(f"Olá, {perfil['nome']}. Use o menu à esquerda.")

col1, col2, col3 = st.columns(3)
col1.metric("Materiais ativos", sum(1 for m in consultar("materiais", "id,ativo") if m["ativo"]))
col2.metric("Obras ativas", sum(1 for o in consultar("obras", "id,ativo,situacao")
                                if o["ativo"] and o["situacao"] == "ativa"))
col3.metric("Famílias", len(consultar("familias", "id")))
st.info("Etapa 1 (cadastros). Entradas, saídas e saldos entram na Etapa 2.")
