"""
Pipeline completo da Fase 3: roda o scraper da OLX, limpa e deduplica
os dados, e grava tudo no MySQL - criando anuncios novos, atualizando
os que ja existem, e registrando no historico_precos sempre que o
preco de um anuncio mudar em relacao a ultima captura.

Como rodar (raiz do projeto, venv ativado):
    python scripts/executar_pipeline.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scrapers.olx_scraper import OlxScraper
from src.etl.clean import limpar_anuncios
from src.etl.deduplicate import deduplicar_anuncios
from src.database.connection import get_session
from src.database.models import Fonte, Anuncio, HistoricoPreco

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


def coletar_todos_os_anuncios(max_por_regiao: int = 20) -> list[dict]:
    """Roda o scraper em todas as regioes configuradas e junta os resultados."""
    todos = []
    for regiao, config in URLS_BUSCA.items():
        print(f"Coletando anuncios de: {regiao}...")
        scraper = OlxScraper(headless=False)
        anuncios = scraper.executar(
            url_busca=config["url"],
            max_anuncios=max_por_regiao,
            cidade_padrao=config["cidade_padrao"],
        )
        print(f"   {len(anuncios)} anuncios coletados.")
        todos.extend(anuncios)
    return todos


def salvar_no_banco(anuncios_limpos: list[dict]) -> dict:
    """
    Grava a lista de anuncios ja limpos/deduplicados no MySQL.

    Para cada anuncio:
    - Se NAO existir (mesma fonte_id + id_externo), cria um registro
      novo em `anuncios` E um primeiro registro em `historico_precos`.
    - Se JA existir, atualiza os campos e, SE o preco mudou desde a
      ultima captura, adiciona um novo registro em `historico_precos`
      (sem apagar o anterior - e assim que o historico se acumula).

    Retorna um resumo com as contagens (novos, atualizados, precos_alterados).
    """
    resumo = {"novos": 0, "atualizados": 0, "precos_alterados": 0, "ignorados": 0}

    with get_session() as session:
        fonte_olx = session.query(Fonte).filter_by(nome="OLX").first()
        if not fonte_olx:
            raise RuntimeError(
                "Fonte 'OLX' nao encontrada no banco - rode o schema.sql primeiro."
            )

        for dados in anuncios_limpos:
            id_externo = dados.get("id_externo")
            if not id_externo:
                resumo["ignorados"] += 1
                continue

            anuncio_existente = (
                session.query(Anuncio)
                .filter_by(fonte_id=fonte_olx.id, id_externo=id_externo)
                .first()
            )

            if anuncio_existente is None:
                novo_anuncio = Anuncio(
                    fonte_id=fonte_olx.id,
                    id_externo=id_externo,
                    titulo=dados.get("titulo"),
                    url=dados.get("url"),
                    marca=dados.get("marca"),
                    modelo=dados.get("modelo"),
                    ano=dados.get("ano"),
                    km=dados.get("km"),
                    preco=dados.get("preco"),
                    cidade=dados.get("cidade"),
                    estado=dados.get("estado"),
                    vendedor_tipo=dados.get("vendedor_tipo") or "desconhecido",
                    telefone=dados.get("telefone"),
                    whatsapp=dados.get("whatsapp"),
                    whatsapp_link=dados.get("whatsapp_link"),
                    ativo=True,
                )
                session.add(novo_anuncio)
                session.flush()  # garante novo_anuncio.id preenchido

                if dados.get("preco") is not None:
                    session.add(HistoricoPreco(
                        anuncio_id=novo_anuncio.id,
                        preco=dados["preco"],
                    ))

                resumo["novos"] += 1

            else:
                preco_novo = dados.get("preco")
                preco_mudou = (
                    preco_novo is not None
                    and anuncio_existente.preco is not None
                    and float(preco_novo) != float(anuncio_existente.preco)
                )

                anuncio_existente.titulo = dados.get("titulo") or anuncio_existente.titulo
                anuncio_existente.url = dados.get("url") or anuncio_existente.url
                anuncio_existente.marca = dados.get("marca") or anuncio_existente.marca
                anuncio_existente.modelo = dados.get("modelo") or anuncio_existente.modelo
                anuncio_existente.ano = dados.get("ano") or anuncio_existente.ano
                anuncio_existente.km = dados.get("km") or anuncio_existente.km
                anuncio_existente.cidade = dados.get("cidade") or anuncio_existente.cidade
                anuncio_existente.ativo = True

                if preco_novo is not None:
                    anuncio_existente.preco = preco_novo

                if preco_mudou:
                    session.add(HistoricoPreco(
                        anuncio_id=anuncio_existente.id,
                        preco=preco_novo,
                    ))
                    resumo["precos_alterados"] += 1

                resumo["atualizados"] += 1

    return resumo


def main():
    brutos = coletar_todos_os_anuncios()
    print(f"\nTotal bruto coletado: {len(brutos)} anuncios")

    deduplicados = deduplicar_anuncios(brutos)
    print(f"Apos deduplicar: {len(deduplicados)} anuncios")

    limpos = limpar_anuncios(deduplicados)
    sem_marca = sum(1 for a in limpos if not a.get("marca"))
    print(f"Apos limpeza: {sem_marca} anuncios sem marca identificada (de {len(limpos)})\n")

    print("Gravando no banco de dados...")
    resumo = salvar_no_banco(limpos)

    print("\nResumo do pipeline:")
    print(f"   Novos anuncios:        {resumo['novos']}")
    print(f"   Anuncios atualizados:  {resumo['atualizados']}")
    print(f"   Precos que mudaram:    {resumo['precos_alterados']}")
    print(f"   Ignorados (sem id):    {resumo['ignorados']}")


if __name__ == "__main__":
    main()