"""
Responsavel por criar e configurar a instancia do Selenium WebDriver
(Chrome), centralizando essa configuracao para nao duplicar em cada
scraper (olx_scraper.py, marketplace_scraper.py, etc).

Reaproveita a mesma logica que voce ja testou no exemplo isolado
(scraper_teste.py com books.toscrape.com), agora integrada as
configuracoes do projeto (HEADLESS vem do .env via config/settings.py).

Uso tipico dentro de um scraper:

    from src.scrapers.driver_factory import criar_driver

    driver = criar_driver()
    try:
        driver.get("https://www.olx.com.br/...")
        ...
    finally:
        driver.quit()
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import HEADLESS

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def criar_driver(headless: bool = None) -> webdriver.Chrome:
    """
    Cria e retorna uma instancia configurada do Chrome controlada
    pelo Selenium.

    headless=None (padrao) -> usa o valor definido no .env (HEADLESS=True/False).
    Passar True/False explicitamente aqui sobrescreve o .env so para
    aquela chamada especifica - util por exemplo para forcar headless=False
    durante o desenvolvimento de um scraper novo, mesmo que o .env esteja
    configurado como True para producao.
    """
    if headless is None:
        headless = HEADLESS

    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    # user-agent deixa a requisicao mais parecida com um navegador comum,
    # em vez de um user-agent generico que identifica automacao
    options.add_argument(f"user-agent={USER_AGENT}")

    # Reduz a chance de deteccao como bot em alguns sites
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Janela grande o suficiente para o site nao cair em layout mobile
    options.add_argument("--window-size=1920,1080")

    # webdriver-manager baixa e gerencia a versao correta do chromedriver
    # automaticamente, sem precisar baixar/configurar nada na mao
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    # Remove um sinalizador comum que sites usam para detectar automacao
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )

    return driver
