"""Formatação em português do Brasil: R$, números e datas DD/MM/AAAA."""
from datetime import date, datetime


def _ptbr(texto: str) -> str:
    return texto.replace(",", "\0").replace(".", ",").replace("\0", ".")


def numero(valor, casas=2):
    if valor is None:
        return "—"
    return _ptbr(f"{float(valor):,.{casas}f}")


def moeda(valor):
    if valor is None:
        return "—"
    return "R$ " + numero(valor, 2)


def data_br(valor):
    if valor in (None, ""):
        return "—"
    if isinstance(valor, date):  # datetime também é date
        return valor.strftime("%d/%m/%Y")
    return datetime.strptime(str(valor)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
