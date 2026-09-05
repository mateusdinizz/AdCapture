"""
Logica para identificar e remover anuncios duplicados dentro de uma
mesma leva de captura (ex: o mesmo anuncio aparecendo tanto na busca
de Recife quanto na de Jaboatao, se a regiao dele for ambigua).

A deduplicacao CONTRA o banco (anuncio que ja existe de uma captura
anterior) e tratada separadamente no pipeline (upsert), nao aqui -
esta funcao cuida so de duplicatas DENTRO da lista que acabou de ser
capturada.
"""


def deduplicar_anuncios(anuncios: list[dict]) -> list[dict]:
    """
    Remove anuncios duplicados de uma lista, usando id_externo como
    chave. Quando ha duplicata, mantem a versao com MAIS dados
    preenchidos (menos campos None) - criterio simples de "qualidade".
    """
    por_id: dict[str, dict] = {}

    for anuncio in anuncios:
        id_externo = anuncio.get("id_externo")
        if not id_externo:
            continue

        existente = por_id.get(id_externo)
        if existente is None:
            por_id[id_externo] = anuncio
            continue

        if _contar_campos_preenchidos(anuncio) > _contar_campos_preenchidos(existente):
            por_id[id_externo] = anuncio

    return list(por_id.values())


def _contar_campos_preenchidos(anuncio: dict) -> int:
    """Conta quantos campos do dicionario nao sao None/vazio."""
    return sum(1 for v in anuncio.values() if v not in (None, "", []))