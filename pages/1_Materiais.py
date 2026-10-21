import pandas as pd
import streamlit as st

from auth import exigir_login
from db import consultar, salvar, lembrar, mostrar_aviso
from formatos import moeda, numero

perfil = exigir_login()
admin = perfil["perfil"] == "admin"
st.title("Materiais")
mostrar_aviso()

UNIDADES = ["peça", "kg", "L"]
TIPOS = {"reutilizavel": "Reutilizável", "consumivel": "Consumível"}
PROPRIEDADES = {"proprio": "Próprio", "alugado": "Alugado"}

materiais = consultar("materiais", "*, subtipos(codigo, nome, familias(codigo, nome)), fornecedores(nome)", "codigo")
subtipos = [s for s in consultar("subtipos", "*, familias(codigo, nome)") if s["ativo"]]
fornecedores = [f for f in consultar("fornecedores", "*", "nome") if f["ativo"]]


def _idx(lista, valor):
    return lista.index(valor) if valor in lista else 0


def _opc(valor):  # número do banco -> valor do campo (0 = não informado)
    return float(valor) if valor is not None else 0.0


def form_material(chave, ini, novo):
    ini = ini or {}
    with st.form(chave, clear_on_submit=novo):
        subtipo_id = None
        if novo:
            rotulos = {f"{s['familias']['codigo']}-{s['codigo']} — {s['nome']}": s["id"] for s in subtipos}
            subtipo_id = rotulos[st.selectbox("Subtipo (o código FAM-SUB-NNNN é gerado sozinho)", list(rotulos))]
        descricao = st.text_input("Descrição (inclua a medida, ex.: Escora metálica 3,00 m)", value=ini.get("descricao", ""))
        c1, c2 = st.columns(2)
        unidade = c1.selectbox("Unidade de controle", UNIDADES, index=_idx(UNIDADES, ini.get("unidade")))
        peso = c2.number_input("Peso unitário (kg) — 0 = não informado; ignorado se a unidade for kg",
                               min_value=0.0, step=0.1, format="%.3f", value=_opc(ini.get("peso_unitario_kg")))
        m1, m2, m3 = st.columns(3)
        comp = m1.number_input("Comprimento (m)", min_value=0.0, step=0.1, format="%.3f", value=_opc(ini.get("comprimento_m")))
        larg = m2.number_input("Largura (m)", min_value=0.0, step=0.1, format="%.3f", value=_opc(ini.get("largura_m")))
        alt = m3.number_input("Altura ou espessura (m)", min_value=0.0, step=0.001, format="%.3f", value=_opc(ini.get("altura_m")))
        c3, c4 = st.columns(2)
        custo = c3.number_input("Custo unitário (R$)", min_value=0.0, step=0.01, format="%.2f", value=_opc(ini.get("custo_unitario")))
        minimo = c4.number_input("Estoque mínimo (na unidade de controle)", min_value=0.0, step=1.0, format="%.3f", value=_opc(ini.get("estoque_minimo")))
        c5, c6 = st.columns(2)
        tipo = c5.selectbox("Tipo", list(TIPOS), format_func=TIPOS.get, index=_idx(list(TIPOS), ini.get("tipo")))
        prop = c6.selectbox("Propriedade", list(PROPRIEDADES), format_func=PROPRIEDADES.get, index=_idx(list(PROPRIEDADES), ini.get("propriedade")))
        c7, c8 = st.columns(2)
        forn_ids = [None] + [f["id"] for f in fornecedores]
        forn_nomes = {f["id"]: f["nome"] for f in fornecedores}
        forn = c7.selectbox("Locador/fornecedor (obrigatório se alugado)", forn_ids,
                            format_func=lambda i: "—" if i is None else forn_nomes[i],
                            index=_idx(forn_ids, ini.get("fornecedor_id")))
        vida = c8.number_input("Vida útil estimada (meses) — só reutilizável; 0 = não informado",
                               min_value=0.0, step=1.0, format="%.1f", value=_opc(ini.get("vida_util_meses")))
        obs = st.text_area("Observações", value=ini.get("observacoes") or "")
        ativo = True if novo else st.checkbox("Material ativo", value=ini.get("ativo", True))
        enviado = st.form_submit_button("Cadastrar material" if novo else "Salvar alterações")
    if not enviado:
        return None
    if not descricao.strip():
        st.error("Informe a descrição.")
        return None
    if prop == "alugado" and forn is None:
        st.error("Material alugado precisa de locador/fornecedor.")
        return None
    dados = {
        "descricao": descricao.strip(), "unidade": unidade,
        "peso_unitario_kg": 1 if unidade == "kg" else (peso or None),
        "comprimento_m": comp or None, "largura_m": larg or None, "altura_m": alt or None,
        "custo_unitario": custo, "estoque_minimo": minimo, "tipo": tipo, "propriedade": prop,
        "fornecedor_id": forn if prop == "alugado" else None,
        "vida_util_meses": (vida or None) if tipo == "reutilizavel" else None,
        "observacoes": obs.strip() or None, "ativo": ativo,
    }
    if novo:
        dados["subtipo_id"] = subtipo_id
    return dados


aba_lista, aba_novo, aba_editar = st.tabs(["Lista", "Novo material", "Editar material"])

with aba_lista:
    linhas = []
    for m in materiais:
        sub = m["subtipos"]
        linhas.append({
            "Código": m["codigo"], "Descrição": m["descricao"],
            "Família": sub["familias"]["nome"], "Subtipo": sub["nome"], "Unidade": m["unidade"],
            "Peso unit. (kg)": numero(m["peso_unitario_kg"], 3), "Custo unit.": moeda(m["custo_unitario"]),
            "Tipo": TIPOS[m["tipo"]], "Propriedade": PROPRIEDADES[m["propriedade"]],
            "Locador": (m["fornecedores"] or {}).get("nome", "—"),
            "Estoque mín.": numero(m["estoque_minimo"], 3), "Situação": "Ativo" if m["ativo"] else "Inativo",
        })
    df = pd.DataFrame(linhas)
    if df.empty:
        st.info("Nenhum material cadastrado ainda.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        busca = f1.text_input("Buscar por código ou descrição")
        fam = f2.multiselect("Família", sorted(df["Família"].unique()))
        tipo_f = f3.multiselect("Tipo", sorted(df["Tipo"].unique()))
        inativos = f4.checkbox("Mostrar inativos")
        if busca:
            b = busca.lower()
            df = df[df["Código"].str.lower().str.contains(b) | df["Descrição"].str.lower().str.contains(b)]
        if fam:
            df = df[df["Família"].isin(fam)]
        if tipo_f:
            df = df[df["Tipo"].isin(tipo_f)]
        if not inativos:
            df = df[df["Situação"] == "Ativo"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} material(is) exibido(s).")

with aba_novo:
    if not admin:
        st.info("Só o administrador cadastra materiais.")
    elif not subtipos:
        st.warning("Cadastre ao menos um subtipo em 'Famílias e Subtipos' antes de criar materiais.")
    else:
        dados = form_material("novo_material", None, True)
        if dados:
            ok, r = salvar("materiais", dados)
            if ok:
                lembrar(f"Material cadastrado com o código **{r['codigo']}**.")
                st.rerun()
            else:
                st.error(r)

with aba_editar:
    if not admin:
        st.info("Só o administrador edita materiais.")
    elif not materiais:
        st.info("Nenhum material para editar.")
    else:
        i = st.selectbox("Material", range(len(materiais)),
                         format_func=lambda k: f"{materiais[k]['codigo']} — {materiais[k]['descricao']}")
        m = materiais[i]
        st.caption(f"Código e subtipo não podem ser alterados. Subtipo: {m['subtipos']['nome']}.")
        dados = form_material(f"editar_{m['id']}", m, False)
        if dados:
            ok, r = salvar("materiais", dados, m["id"])
            if ok:
                lembrar(f"Material {m['codigo']} atualizado.")
                st.rerun()
            else:
                st.error(r)
