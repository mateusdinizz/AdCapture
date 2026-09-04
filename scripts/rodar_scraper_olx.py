"""
Script de teste da Fase 2: roda o OlxScraper de verdade contra a OLX
e salva o resultado em CSV para voce conferir manualmente se os dados
capturados batem com os anuncios reais.

Como rodar (raiz do projeto, venv ativado):
    python scripts/rodar_scraper_olx.py

Se os dados vierem incompletos (preco/km/cidade como None com
frequencia), rode o modo debug:
    python scripts/rodar_scraper_olx.py --debug

Se os anuncios capturados nao baterem com a ordem/conteudo real da
pagina (pulando anuncios, por exemplo), rode o modo listar - ele
mostra TODOS os links encontrados, em ordem, com a URL real usada
(util para comparar lado a lado com o navegador manualmente):
    python scripts/rodar_scraper_olx.py --listar
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import csv
import pandas as pd

from src.scrapers.olx_scraper import OlxScraper

URLS_BUSCA = {
    "Recife": {
        "url": "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-pe/grande-recife/recife",
        "cidade_padrao": "Recife",
    },
    "Jaboatao (Candeias/Piedade)": {
        "url": "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-pe/grande-recife/grande-recife/jaboatao-dos-guararapes",
        "cidade_padrao": "Jaboatão dos Guararapes",
    },
}


def main():
    if "--debug" in sys.argv:
        print("Modo DEBUG: investigando a estrutura da pagina...\n")
        scraper = OlxScraper(headless=False)
        try:
            scraper.depurar_estrutura(URLS_BUSCA["Recife"]["url"])
        finally:
            scraper.fechar()
        return

    if "--listar" in sys.argv:
        print("Modo LISTAR: mostrando todos os links encontrados, em ordem...\n")
        for regiao, config in URLS_BUSCA.items():
            print("=" * 70)
            print(f"REGIAO: {regiao}")
            print("=" * 70)
            scraper = OlxScraper(headless=False)
            try:
                scraper.listar_todos_os_links(config["url"])
            finally:
                scraper.fechar()
            print()
        return

    todos_anuncios = []

    for regiao, config in URLS_BUSCA.items():
        print(f"Coletando anuncios de: {regiao}...")
        scraper = OlxScraper(headless=False)  # False para voce acompanhar visualmente por enquanto
        anuncios = scraper.executar(
            url_busca=config["url"],
            max_anuncios=10,
            cidade_padrao=config["cidade_padrao"],
        )
        print(f"   {len(anuncios)} anuncios coletados.\n")

        for a in anuncios:
            a["regiao_busca"] = regiao
        todos_anuncios.extend(anuncios)

    df = pd.DataFrame(todos_anuncios)
    print(df[["titulo", "marca", "modelo", "preco", "km", "ano", "cidade"]], "\n")

    caminho_csv = "anuncios_olx_teste.csv"
    df.to_csv(caminho_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"Salvo em: {caminho_csv}")
    print("\nAbra o CSV e compare alguns anuncios com o site real da OLX")
    print("para confirmar se preco, km, ano e cidade bateram certinho.")


if __name__ == "__main__":
    main()