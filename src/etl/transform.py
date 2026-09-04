"""
Modulo de transformacao e enriquecimento dos dados de anuncios (Fase 3 - ETL).

Contem funcoes para:
- Extrair e padronizar marca e modelo a partir do titulo do anuncio.
- Normalizar tipos e campos de DataFrames de anuncios.
"""

import re
from typing import Optional, Tuple


MARCAS_MAP = {
    "chevrolet": "Chevrolet",
    "gm": "Chevrolet",
    "fiat": "Fiat",
    "volkswagen": "Volkswagen",
    "vw": "Volkswagen",
    "toyota": "Toyota",
    "hyundai": "Hyundai",
    "renault": "Renault",
    "jeep": "Jeep",
    "honda": "Honda",
    "nissan": "Nissan",
    "ford": "Ford",
    "byd": "BYD",
    "chery": "Chery",
    "caoa chery": "Chery",
    "mitsubishi": "Mitsubishi",
    "peugeot": "Peugeot",
    "citroen": "Citroën",
    "citroën": "Citroën",
    "gwm": "GWM",
    "bmw": "BMW",
    "mercedes": "Mercedes-Benz",
    "mercedes-benz": "Mercedes-Benz",
    "audi": "Audi",
    "kia": "Kia",
    "volvo": "Volvo",
    "ram": "RAM",
    "suzuki": "Suzuki",
    "subaru": "Subaru",
    "porsche": "Porsche",
    "land rover": "Land Rover",
    "jac": "JAC",
    "changan": "Changan",
    "dodge": "Dodge",
    "troller": "Troller",
}

MODELOS_POR_MARCA = {
    "Chevrolet": [
        "Onix Plus", "Onix", "Tracker", "Spin", "Cruze", "S10", "Montana",
        "Prisma", "Celta", "Corsa", "Cobalt", "Astra", "Vectra", "Trailblazer",
        "Captiva", "Zafira", "Meriva", "Sonic", "Agile", "Classic", "Equinox", "Camaro"
    ],
    "Fiat": [
        "Fastback", "Pulse", "Argo", "Cronos", "Mobi", "Strada", "Toro",
        "Fiorino", "Uno", "Palio", "Siena", "Grand Siena", "Punto", "Idea",
        "Doblo", "Linea", "Bravo", "Stilo", "Ducato", "Titano", "Marea", "Tempra"
    ],
    "Volkswagen": [
        "T-Cross", "Nivus", "Virtus", "Polo", "Gol", "Voyage", "Saveiro",
        "Amarok", "Jetta", "Taos", "Fox", "Up!", "Up", "Golf", "Crossfox",
        "Spacefox", "Tiguan", "Passat", "Bora", "Fusca", "Kombi", "Santana", "Parati"
    ],
    "Toyota": [
        "Corolla Cross", "Corolla", "Hilux", "Yaris", "Etios", "SW4",
        "RAV4", "Camry", "Prius", "Fielder", "Bandeirante"
    ],
    "Hyundai": [
        "HB20S", "HB20X", "HB20", "Creta", "Tucson", "ix35", "Santa Fe",
        "i30", "Azera", "Elantra", "HR", "Vera Cruz", "Sonata", "Ioniq"
    ],
    "Renault": [
        "Kwid", "Duster", "Sandero", "Logan", "Captur", "Kardian",
        "Oroch", "Stepway", "Clio", "Fluence", "Megane", "Master", "Scenic", "Kangoo"
    ],
    "Jeep": [
        "Renegade", "Compass", "Commander", "Cherokee", "Grand Cherokee", "Wrangler", "Gladiator"
    ],
    "Honda": [
        "Civic", "HR-V", "HRV", "Fit", "City", "WR-V", "WRV", "CR-V", "CRV", "Accord", "ZR-V"
    ],
    "Nissan": [
        "Kicks", "Versa", "March", "Frontier", "Sentra", "Livina", "Grand Livina", "Tiida"
    ],
    "Ford": [
        "Ka+", "Ka Sedan", "Ka", "Ecosport", "Ranger", "Fiesta", "Focus",
        "Fusion", "Territory", "Bronco", "Maverick", "Edge", "Courier"
    ],
    "Chery": [
        "Tiggo 8", "Tiggo 7", "Tiggo 5X", "Tiggo 3X", "Tiggo 2", "Tiggo",
        "Arrizo 6", "Arrizo 5", "QQ", "Celer", "Face", "S18"
    ],
    "BYD": [
        "Dolphin Mini", "Dolphin", "Song Plus", "Song Pro", "Yuan Plus", "Yuan Pro",
        "Seal", "King", "Tan", "Han", "Shark"
    ],
    "Mitsubishi": [
        "L200 Triton Sport", "L200 Triton", "L200", "Eclipse Cross", "ASX",
        "Outlander", "Pajero TR4", "Pajero Dakar", "Pajero Full", "Pajero", "Lancer"
    ],
    "Peugeot": [
        "208", "2008", "3008", "207", "206", "308", "408", "Partner", "Expert", "Boxer"
    ],
    "Citroën": [
        "C3 Aircross", "C3", "C4 Cactus", "C4 Lounge", "C4 Pallas", "C4", "Aircross", "Jumpy", "Berlingo"
    ],
    "GWM": [
        "Haval H6", "Ora 03"
    ],
    "BMW": [
        "320i", "328i", "Série 3", "Série 1", "X1", "X3", "X5", "X6", "M3"
    ],
    "Mercedes-Benz": [
        "Classe A", "Classe C", "GLA", "GLB", "GLC", "C180", "C200", "C250", "Sprinter"
    ],
    "Audi": [
        "A3", "A4", "A5", "Q3", "Q5", "Q7", "Q8"
    ],
    "Kia": [
        "Sportage", "Cerato", "Picanto", "Soul", "Seltos", "Carnival", "Bongo"
    ],
}


def extrair_marca_modelo(titulo: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Identifica a marca e o modelo de um carro a partir do titulo do anuncio.

    Exemplos:
        'Chevrolet Tracker 1.0 Turbo 12V Aut. 2026' -> ('Chevrolet', 'Tracker')
        'Renault Kwid Zen 1.0 Flex 12V 5P Mec. 2026' -> ('Renault', 'Kwid')
        'CAOA Chery Tiggo 8 MAX Drive 1.6 Aut. 2024' -> ('Chery', 'Tiggo 8')
        'Fiat Fastback 1.0 200 Turbo Flex AUT 2024'  -> ('Fiat', 'Fastback')
    """
    if not titulo or not isinstance(titulo, str):
        return None, None

    titulo_limpo = titulo.strip()
    titulo_lower = titulo_limpo.lower()

    marca_encontrada: Optional[str] = None
    inicio_modelo = 0

    # 1. Identifica a Marca
    # Ordena marcas por tamanho decrescente (ex: "caoa chery" antes de "chery", "land rover" antes de "rover")
    marcas_ordenadas = sorted(MARCAS_MAP.keys(), key=len, reverse=True)
    for marca_busca in marcas_ordenadas:
        padrao = rf"^{re.escape(marca_busca)}\b"
        match = re.search(padrao, titulo_lower)
        if match:
            marca_encontrada = MARCAS_MAP[marca_busca]
            inicio_modelo = match.end()
            break

    # Se a marca nao estava no inicio, procura no texto inteiro
    if not marca_encontrada:
        for marca_busca in marcas_ordenadas:
            padrao = rf"\b{re.escape(marca_busca)}\b"
            match = re.search(padrao, titulo_lower)
            if match:
                marca_encontrada = MARCAS_MAP[marca_busca]
                inicio_modelo = match.end()
                break

    if not marca_encontrada:
        partes = titulo_limpo.split()
        if partes:
            return partes[0].capitalize(), partes[1] if len(partes) > 1 else None
        return None, None

    # 2. Identifica o Modelo dentro da Marca encontrada
    resto_titulo = titulo_limpo[inicio_modelo:].strip()
    resto_lower = resto_titulo.lower()

    modelos_conhecidos = MODELOS_POR_MARCA.get(marca_encontrada, [])
    modelos_ordenados = sorted(modelos_conhecidos, key=len, reverse=True)

    for modelo_candidato in modelos_ordenados:
        mod_escaped = re.escape(modelo_candidato.lower())
        fim_b = r"\b" if modelo_candidato[-1].isalnum() else r"(?!\w)"
        padrao_modelo = rf"\b{mod_escaped}{fim_b}"
        if re.search(padrao_modelo, resto_lower):
            return marca_encontrada, modelo_candidato

    # Fallback: se o modelo exato nao esta na lista, pega a proxima palavra significativa
    partes_resto = [p for p in resto_titulo.split() if p.isalnum() or "-" in p or "+" in p]
    if partes_resto:
        primeira_palavra = partes_resto[0]
        if not (primeira_palavra.isdigit() and len(primeira_palavra) == 4):
            return marca_encontrada, primeira_palavra.capitalize()

    return marca_encontrada, None
