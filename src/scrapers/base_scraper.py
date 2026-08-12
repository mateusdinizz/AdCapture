
class BaseScraper:
    def __init__(self):
        raise NotImplementedError("Implementar na proxima etapa.")

    def coletar_anuncios(self):
        """Metodo que cada scraper especifico deve implementar."""
        raise NotImplementedError
