"""
Scraper especifico da OLX. Herda de BaseScraper.

ESTRATEGIA DE EXTRACAO:
Em vez de depender de nomes de classe CSS (que a OLX muda com
frequencia, quebrando o scraper toda hora), localizamos cada anuncio
pelo PADRAO DA URL: todo link de anuncio de carro na OLX contem
"/autos-e-pecas/carros-vans-e-utilitarios/" e termina em numeros
(o id do anuncio). Isso tende a ser mais estavel que classes CSS.

Dentro do "card" (elemento pai do link), extraimos o TEXTO COMPLETO
visivel e usamos expressoes regulares para achar preco, km, ano e
cidade - porque a ORDEM em que esses dados aparecem costuma ser mais
estavel do que o nome das classes usadas para estiliza-los.

IMPORTANTE: este scraper foi escrito sem acesso a um navegador real
durante o desenvolvimento (ambiente sem internet/Chrome). A parte mais
provavel de precisar de ajuste eh o metodo que "sobe" do link ate o
card pai (_encontrar_card) - use o metodo depurar_estrutura() abaixo
para investigar a estrutura real e corrigir se necessario.
"""

import re
from selenium.webdriver.common.by import By

from src.scrapers.base_scraper import BaseScraper


class OlxScraper(BaseScraper):

    PADRAO_URL_ANUNCIO = re.compile(r"/autos-e-pecas/carros-vans-e-utilitarios/.+-(\d+)(?:\?|$)")
    PADRAO_PRECO = re.compile(r"R\$\s?([\d.]+)")
    PADRAO_KM = re.compile(r"([\d.]+)\s?km", re.IGNORECASE)
    PADRAO_ANO = re.compile(r"\b(19[8-9]\d|20[0-4]\d)\b")

    def coletar_anuncios(self, url_busca: str, max_anuncios: int = 20, cidade_padrao: str = None) -> list[dict]:
        """
        Acessa uma pagina de busca da OLX e extrai os anuncios visiveis.

        url_busca: URL completa da busca (ex: carros em Recife)
        max_anuncios: limite de quantos anuncios coletar dessa pagina
        cidade_padrao: cidade a usar quando nao for possivel extrair a
            localizacao exata do card (ex: "Recife"). Como cada URL de
            busca ja e especifica de uma cidade/regiao, isso e uma boa
            aproximacao - o bairro exato fica para uma melhoria futura
            (visitar a pagina de detalhe do anuncio).
        """
        self.driver.get(url_busca)

        seletor_links = "a[href*='autos-e-pecas/carros-vans-e-utilitarios']"
        self.esperar_elementos(By.CSS_SELECTOR, seletor_links)

        links = self.driver.find_elements(By.CSS_SELECTOR, seletor_links)

        anuncios = []
        urls_vistas = set()

        for link in links:
            url = link.get_attribute("href")
            if not url or url in urls_vistas:
                continue

            match_id = self.PADRAO_URL_ANUNCIO.search(url)
            if not match_id:
                # Provavelmente um link de categoria/marca (ex: "todas as marcas"),
                # nao um anuncio de verdade - ignora e segue para o proximo
                continue

            urls_vistas.add(url)

            # Descoberta no debug: o proprio link ja contem titulo, km, ano
            # e preco no seu texto - nao precisa (e nao deve) subir para
            # elementos "pai", porque em niveis mais altos o texto passa a
            # misturar VARIOS anuncios vizinhos ao mesmo tempo.
            texto_card = link.text

            linhas = [l.strip() for l in texto_card.split("\n") if l.strip()]
            # Remove textos de interface que nao sao dado do anuncio
            linhas = [l for l in linhas if l not in ("Adicionar aos favoritos",)]
            titulo = linhas[0] if linhas else (link.get_attribute("title") or "Sem titulo")

            anuncios.append({
                "id_externo": match_id.group(1),
                "titulo": titulo,
                "url": url,
                "marca": None,    # extraido do titulo depois, na Fase 3 (ETL)
                "modelo": None,   # idem
                "ano": self._extrair_ano(texto_card),
                "km": self._extrair_km(texto_card),
                "preco": self._extrair_preco(texto_card),
                "cidade": cidade_padrao,  # aproximacao pela regiao buscada (ver docstring)
                "estado": "PE",
                "vendedor_tipo": "desconhecido",
                "telefone": None,
                "whatsapp": None,
            })

            if len(anuncios) >= max_anuncios:
                break

        return anuncios

    def _extrair_preco(self, texto: str):
        matches = self.PADRAO_PRECO.findall(texto)
        if not matches:
            return None
        # Quando ha preco riscado (de/por), o ultimo valor listado
        # costuma ser o preco atual (com desconto)
        valor = matches[-1].replace(".", "")
        try:
            return float(valor)
        except ValueError:
            return None

    def _extrair_km(self, texto: str):
        match = self.PADRAO_KM.search(texto)
        if not match:
            return None
        try:
            return int(match.group(1).replace(".", ""))
        except ValueError:
            return None

    def _extrair_ano(self, texto: str):
        match = self.PADRAO_ANO.search(texto)
        return int(match.group(1)) if match else None

    def depurar_estrutura(self, url_busca: str):
        """
        Metodo de apoio para debug MANUAL. Nao faz parte do fluxo normal
        de coleta - roda separadamente quando algo nao estiver batendo.

        Abre a pagina, acha o PRIMEIRO link de anuncio, e imprime:
        1. O texto do proprio link
        2. O texto de cada nivel de "ancestral" (pai, avo, bisavo...)

        Isso ajuda a identificar visualmente em qual nivel esta o card
        completo do anuncio (com preco, km, cidade), para corrigir o
        _encontrar_card() se as tentativas automaticas nao funcionarem.

        Uso:
            scraper = OlxScraper(headless=False)
            scraper.depurar_estrutura("https://www.olx.com.br/...")
            scraper.fechar()
        """
        self.driver.get(url_busca)
        seletor_links = "a[href*='autos-e-pecas/carros-vans-e-utilitarios']"
        self.esperar_elementos(By.CSS_SELECTOR, seletor_links)

        links = self.driver.find_elements(By.CSS_SELECTOR, seletor_links)
        primeiro_valido = None
        for link in links:
            url = link.get_attribute("href") or ""
            if self.PADRAO_URL_ANUNCIO.search(url):
                primeiro_valido = link
                break

        if not primeiro_valido:
            print("Nenhum link de anuncio encontrado - confira a URL de busca.")
            return

        print(f"URL do anuncio: {primeiro_valido.get_attribute('href')}")
        print(f"Texto do link: {primeiro_valido.text!r}\n")

        elemento = primeiro_valido
        for nivel in range(1, 6):
            try:
                elemento = elemento.find_element(By.XPATH, "./..")
                print(f"--- Nivel {nivel} (pai #{nivel}) ---")
                print(f"Tag: {elemento.tag_name}")
                print(f"Texto: {elemento.text[:300]!r}\n")
            except Exception as e:
                print(f"Parou no nivel {nivel}: {e}")
                break