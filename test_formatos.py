from formatos import moeda, numero, data_br
from datetime import date


def test_moeda():
    assert moeda(1234.5) == "R$ 1.234,50"
    assert moeda(0) == "R$ 0,00"
    assert moeda(1234567.891) == "R$ 1.234.567,89"
    assert moeda(None) == "—"


def test_numero():
    assert numero(0.5, 3) == "0,500"
    assert numero(12500, 0) == "12.500"


def test_data():
    assert data_br("2026-10-21") == "21/10/2026"
    assert data_br("2026-10-21T10:00:00+00:00") == "21/10/2026"
    assert data_br(date(2026, 1, 5)) == "05/01/2026"
    assert data_br(None) == "—"


if __name__ == "__main__":
    test_moeda(); test_numero(); test_data()
    print("formatos: todos os testes passaram")
