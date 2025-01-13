from bs4 import BeautifulSoup
import requests

def calculadora(consumo: list, classe: str, bandeira: str) -> tuple:
    """
    Retorna uma tupla de floats contendo economia anual, economia mensal,
    desconto aplicado e cobertura.
    """
    economia_anual = 0
    economia_mensal = 0
    desconto_aplicado = 0
    cobertura = 0

    if classe in ["Comercial", "Industrial"]:
        classe_original = classe  
        classe = "Industrial/Comercial"
    else:
        classe_original = classe

    url = 'https://www.cemig.com.br/atendimento/valores-de-tarifas-e-servicos/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    tarifas = {}

    sections = soup.find_all('section')

    tabela = None

    for section in sections:
        if classe == "Residencial" and "B1- RESIDENCIAL NORMAL" in section.text:
            tabela = section.find('table', {'class': 'table-bordered'})
            break
        elif classe == "Industrial/Comercial" and "B3 - DEMAIS CLASSES" in section.text:
            tabela = section.find('table', {'class': 'table-bordered'})
            break


    cabecalhos = [
        th.text.strip().split(" -")[0] for th in tabela.find('thead').find_all('th')
    ]

    linhas = tabela.find('tbody').find_all('tr')

    for linha in linhas:
        colunas = linha.find_all('td')
        classe_atual = colunas[0].text.strip()

        if "Residencial" in classe_atual:
            classe_atual = "Residencial"
        elif "Demais classes" in classe_atual:
            classe_atual = "Industrial/Comercial"

        tarifas_bandeiras = {}
        for i in range(1, len(colunas)):
            bandeira_atual = cabecalhos[i]
            valor = colunas[i].text.strip().replace(',', '.')
            tarifas_bandeiras[bandeira_atual] = float(valor)

        tarifas[classe_atual] = tarifas_bandeiras

    consumo_medio = sum(consumo) / len(consumo)

    if consumo_medio < 10000:
        descontos = {
            "Residencial": 0.18,
            "Comercial": 0.16,
            "Industrial": 0.12
        }
        cobertura = 0.90
    elif 10000 <= consumo_medio <= 20000:
        descontos = {
            "Residencial": 0.22,
            "Comercial": 0.18,
            "Industrial": 0.15
        }
        cobertura = 0.95
    else:
        descontos = {
            "Residencial": 0.25,
            "Comercial": 0.22,
            "Industrial": 0.18
        }
        cobertura = 0.99

    desconto_aplicado = descontos[classe_original]
    custo_mensal = consumo_medio * tarifas[classe][bandeira] * cobertura
    economia_mensal = custo_mensal * desconto_aplicado
    economia_anual = economia_mensal * 12

    return (
        round(economia_anual, 2),
        round(economia_mensal, 2),
        round(desconto_aplicado, 2),
        round(cobertura, 2),
    )


if __name__ == "__main__":
    print("Testando...")

    assert calculadora([1518, 1071, 968], "Industrial", "BANDEIRA VERMELHA 2") == (
        1349.86,
        112.49,
        0.12,
        0.90,
    ) 

    assert calculadora([1000, 1054, 1100], "Residencial", "BANDEIRA VERMELHA 1") == (
        1725.61,
        143.8,
        0.18,
        0.90
    )

    assert calculadora([973, 629, 726], "Comercial", "BANDEIRA AMARELA") == (
        1097.6,
        91.47,
        0.16,
        0.90
    )

    assert calculadora([15000, 14000, 16000], "Industrial", "BANDEIRA VERMELHA 1") == (
        21656.81,
        1804.73,
        0.15,
        0.95
    )

    assert calculadora([12000, 11000, 11400], "Residencial", "BANDEIRA VERDE") == (
        22997.8,
        1916.48,
        0.22,
        0.95
    )

    assert calculadora([17500, 16000, 16400], "Comercial", "BANDEIRA AMARELA") == (
        27938.08,
        2328.17,
        0.18,
        0.95
    )

    assert calculadora([30000, 29000, 29500], "Industrial", "BANDEIRA VERMELHA 1") == (
        53262.07,
        4438.51,
        0.18,
        0.99
    )

    assert calculadora([22000, 21000, 21400], "Residencial", "BANDEIRA AMARELA") == (
        52186.84,
        4348.9,
        0.25,
        0.99
    )

    assert calculadora([25500, 23000, 21400], "Comercial", "BANDEIRA VERDE") == (
        48697.35,
        4058.11,
        0.22,
        0.99
    )

    print("Todos os testes passaram!")
    