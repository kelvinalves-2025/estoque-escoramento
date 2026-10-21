import io
import zipfile
from datetime import date

import pandas as pd
import streamlit as st

from auth import exigir_login
from db import consultar

exigir_login(somente_admin=True)
st.title("Backup dos dados")
st.write("Gera um arquivo .zip com uma planilha (CSV) de cada cadastro. "
         "Guarde o arquivo no Google Drive da empresa. Faça isso toda semana e antes de qualquer mudança grande.")

TABELAS = ["perfis", "familias", "subtipos", "estados_conservacao", "depositos",
           "fornecedores", "obras", "materiais"]

if st.button("Gerar backup agora"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for t in TABELAS:
            df = pd.DataFrame(consultar(t, "*"))
            z.writestr(f"{t}.csv", df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"))
    st.session_state["backup"] = buf.getvalue()
    st.session_state["backup_nome"] = f"backup_estoque_{date.today().strftime('%d-%m-%Y')}.zip"

if "backup" in st.session_state:
    st.download_button("Baixar backup", st.session_state["backup"],
                       file_name=st.session_state["backup_nome"], mime="application/zip")
