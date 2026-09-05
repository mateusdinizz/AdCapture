"""
Funcoes de limpeza dos dados brutos capturados pelos scrapers.

Cada funcao aqui e "pura" (recebe dado, devolve dado limpo, sem
efeitos colaterais) para facilitar testes e reuso em qualquer scraper
futuro (nao so OLX).
"""

import re
from datetime import datetime

# Lista de marcas conhecidas no mercado brasileiro, ordenada da mais
# especifica para a mais generica (importa a ordem: "Land Rover" precisa
# ser testada antes de qualquer prefixo que pudesse colidir, por exemplo).
# Isso nao substitui uma base de dados de referencia (tipo tabela FIPE),
# e uma heuristica pratica para o MVP - pode ser expandida conforme
# aparecerem marcas nao cobertas nos dados reais.
MARCAS_CONHECIDAS = [
    "Land Rover", "Mercedes-Benz", "Mercedes", "Volkswagen", "Chevrolet",
    "Mitsubishi", "Chery", "Peugeot", "Citroen", "Citroën", "Hyundai",
    "Renault", "Nissan", "Toyota", "Subaru", "Suzuki", "Honda", "Jeep",
    "Volvo", "Dodge", "Audi", "BYD", "Fiat", "Ford", "BMW", "RAM", "Kia",
]

# Um token e considerado "especificacao tecnica" (marca o fim do nome
# do modelo) se bater num desses padroes especificos - motorizacao
# (1.0, 2.0), valvulas (16V, 8V), tracao (4X4, 4X2).
_PADRAO_MOTORIZACAO = re.compile(r"^\d+\.\d+$")
_PADRAO_VALVULAS = re.compile(r"^\d+[Vv]$")
_PADRAO_TRACAO = re.compile(r"^\d+[Xx]\d+$")
_TOKEN_TEM_DIGITO = re.compile(r"\d")

ANO_MINIMO = 1980
ANO_MAXIMO = datetime.now().year + 1  # margem para veiculos 0km do ano seguinte


def _eh_token_de_especificacao(token: str, posicao: int) -> bool:
    """
    Decide se um token marca o fim do nome do modelo.

    Padroes de motorizacao/valvulas/tracao SEMPRE interrompem, em
    qualquer posicao. Ja um token que so "contem digito" sem bater
    nesses padroes (ex: "2008", "C3", "S10" - varias marcas usam
    numero/alfanumerico como nome de modelo) so e tratado como corte
    a partir da SEGUNDA palavra em diante - a primeira palavra apos a
    marca tem prioridade de ser considerada parte do modelo.
    """
    if _PADRAO_MOTORIZACAO.match(token) or _PADRAO_VALVULAS.match(token) or _PADRAO_TRACAO.match(token):
        return True
    if _TOKEN_TEM_DIGITO.search(token) and posicao > 0:
        return True
    return False


def extrair_marca_modelo(titulo: str, max_tokens_modelo: int = 3) -> tuple[str | None, str | None]:
    """
    Tenta extrair marca e modelo a partir do titulo do anuncio.

    Estrategia: compara o INICIO do titulo contra a lista de marcas
    conhecidas (a primeira que bater e a marca). Depois disso, pega as
    palavras seguintes ate encontrar uma que contenha numero (que
    normalmente marca o inicio da motorizacao/versao/ano) - essas
    palavras viram o modelo.

    Limitacoes conhecidas: as vezes uma palavra de acabamento/versao
    sem numero (ex: "Comfortline", "XRE") acaba entrando junto no
    modelo, ja que o criterio de corte e "contem digito". Isso e
    aceitavel para o MVP mas pode ser refinado depois com dados reais.

    Retorna (marca, modelo) - ambos None se a marca nao for reconhecida.
    """
    if not titulo:
        return None, None

    titulo_limpo = titulo.strip()

    for marca in MARCAS_CONHECIDAS:
        if titulo_limpo.lower().startswith(marca.lower()):
            resto = titulo_limpo[len(marca):].strip()
            tokens = resto.split()

            tokens_modelo = []
            for posicao, token in enumerate(tokens):
                if _eh_token_de_especificacao(token, posicao):
                    break
                tokens_modelo.append(token)
                if len(tokens_modelo) >= max_tokens_modelo:
                    break

            modelo = " ".join(tokens_modelo).strip(" -,.") or None
            return marca, modelo

    return None, None


def limpar_preco(preco) -> float | None:
    """Garante que o preco e um float positivo, ou None se invalido."""
    if preco is None:
        return None
    try:
        valor = float(preco)
    except (ValueError, TypeError):
        return None
    return valor if valor > 0 else None


def limpar_km(km) -> int | None:
    """Garante que o km e um inteiro nao-negativo, ou None se invalido."""
    if km is None:
        return None
    try:
        valor = int(km)
    except (ValueError, TypeError):
        return None
    return valor if valor >= 0 else None


def limpar_ano(ano) -> int | None:
    """Garante que o ano esta num intervalo plausivel, ou None se invalido."""
    if ano is None:
        return None
    try:
        valor = int(ano)
    except (ValueError, TypeError):
        return None
    return valor if ANO_MINIMO <= valor <= ANO_MAXIMO else None


def limpar_anuncio(anuncio: dict) -> dict:
    """
    Aplica todas as limpezas num dicionario de anuncio (no formato que
    os scrapers produzem) e devolve uma COPIA limpa - nao modifica o
    dicionario original.
    """
    limpo = dict(anuncio)

    marca, modelo = extrair_marca_modelo(limpo.get("titulo"))
    # So sobrescreve se o scraper nao tiver preenchido isso sozinho
    limpo["marca"] = limpo.get("marca") or marca
    limpo["modelo"] = limpo.get("modelo") or modelo

    limpo["preco"] = limpar_preco(limpo.get("preco"))
    limpo["km"] = limpar_km(limpo.get("km"))
    limpo["ano"] = limpar_ano(limpo.get("ano"))

    if limpo.get("titulo"):
        limpo["titulo"] = limpo["titulo"].strip()

    return limpo


def limpar_anuncios(anuncios: list[dict]) -> list[dict]:
    """Aplica limpar_anuncio em uma lista inteira de anuncios."""
    return [limpar_anuncio(a) for a in anuncios]