"""
Classe base para todos os scrapers do projeto.

Cada scraper de uma plataforma especifica (OLX, Marketplace) deve herdar
desta classe e implementar o metodo `coletar_anuncios`. Isso garante que
o resto do sistema (ETL, banco) sempre receba os dados no mesmo formato,
independente de qual site originou a informacao.

A implementacao completa (setup do driver, waits, extracao) sera feita
na proxima etapa do projeto.
"""


class BaseScraper:
    def __init__(self):
        raise NotImplementedError("Implementar na proxima etapa.")

    def coletar_anuncios(self):
        """Metodo que cada scraper especifico deve implementar."""
        raise NotImplementedError
