"""
Classe base para todos os scrapers do projeto.

Cada scraper de uma plataforma especifica (OLX, Marketplace) deve herdar
desta classe e implementar o metodo `coletar_anuncios`. Isso garante que
o resto do sistema (ETL, banco) sempre receba os dados no mesmo formato,
independente de qual site originou a informacao.

Uso tipico (o olx_scraper.py vai fazer isso):

    class OlxScraper(BaseScraper):
        def coletar_anuncios(self, url_busca):
            # logica especifica da OLX aqui
            ...

    scraper = OlxScraper()
    anuncios = scraper.executar(url_busca="https://www.olx.com.br/...")
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.scrapers.driver_factory import criar_driver


class BaseScraper:
    """
    Fornece o driver e utilitarios comuns (esperar elemento, fechar
    navegador com seguranca). As subclasses so precisam se preocupar
    com a logica de extracao especifica de cada site.
    """

    def __init__(self, headless: bool = None, timeout_padrao: int = 10):
        self.driver = criar_driver(headless=headless)
        self.timeout_padrao = timeout_padrao

    def esperar_elemento(self, by, seletor, timeout: int = None):
        """
        Espera um elemento aparecer na pagina antes de tentar interagir
        com ele. Evita o erro classico de tentar ler algo que ainda
        nao carregou.
        """
        timeout = timeout or self.timeout_padrao
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, seletor)))

    def esperar_elementos(self, by, seletor, timeout: int = None):
        """Mesma ideia acima, mas para quando se espera uma LISTA de elementos."""
        timeout = timeout or self.timeout_padrao
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_all_elements_located((by, seletor)))

    def coletar_anuncios(self, *args, **kwargs):
        """
        Cada scraper especifico (OlxScraper, MarketplaceScraper) deve
        sobrescrever este metodo com a logica real de extracao.
        Deve retornar uma lista de dicionarios, todos com as MESMAS
        chaves, independente da fonte - isso e o que permite o resto
        do pipeline (ETL, banco) tratar qualquer fonte de forma igual.

        Formato esperado de cada item da lista:
        {
            "id_externo": str,
            "titulo": str,
            "url": str,
            "marca": str | None,
            "modelo": str | None,
            "ano": int | None,
            "km": int | None,
            "preco": float | None,
            "cidade": str | None,
            "estado": str | None,
            "vendedor_tipo": str | None,
            "telefone": str | None,
            "whatsapp": str | None,
        }
        """
        raise NotImplementedError("Cada scraper precisa implementar coletar_anuncios().")

    def fechar(self):
        """Fecha o navegador com seguranca."""
        if self.driver:
            self.driver.quit()

    def executar(self, *args, **kwargs):
        """
        Metodo de conveniencia: chama coletar_anuncios() e garante que
        o navegador e fechado no final, mesmo se der erro no meio -
        evita "vazar" processos do Chrome abertos na sua maquina.
        """
        try:
            return self.coletar_anuncios(*args, **kwargs)
        finally:
            self.fechar()