"""
Scraper especifico da OLX. Herda de BaseScraper.

ESTRATEGIA DE EXTRACAO:
Em vez de depender de nomes de classe CSS (que a OLX muda com
frequencia, quebrando o scraper toda hora), localizamos cada anuncio
pelo PADRAO DA URL: todo link de anuncio de carro na OLX contem
"/autos-e-pecas/carros-vans-e-utilitarios/" e termina em numeros
(o id do anuncio). Isso tende a ser mais estavel que classes CSS.

O proprio link de cada anuncio ja contem, no seu texto visivel,
titulo, km, ano e preco - confirmado via depurar_estrutura() contra
o site real. Nao subimos para elementos "pai" (isso foi testado e
descartado: em niveis mais altos da arvore, o texto passa a misturar
VARIOS anuncios vizinhos ao mesmo tempo, gerando dados errados).

LAZY LOADING: a OLX so renderiza preco/km de verdade apos um scroll
GRADUAL pela pagina (scrollIntoView direto por elemento nao funcionou -
o carregamento parece depender de deteccao de scroll continuo, nao de
"teleporte" ate o elemento). Por isso rolamos a pagina inteira aos
poucos ANTES de comecar a extrair (_rolar_pagina_gradualmente), em vez
de rolar elemento por elemento durante a extracao.

CIDADE: nao foi encontrada de forma confiavel na pagina de busca (nao
esta em nenhum elemento "pai" ate 5 niveis acima do link, testado via
depurar_estrutura()). Por isso o campo cidade usa uma aproximacao: a
regiao que foi buscada (Recife ou Jaboatao), passada via parametro
cidade_padrao. O bairro exato fica para uma melhoria futura, visitando
a pagina de detalhe de cada anuncio.
"""

import re
import time
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
        print(f"URL solicitada: {url_busca}")
        print(f"URL real apos carregar: {self.driver.current_url}")
        if url_busca.rstrip("/") != self.driver.current_url.rstrip("/"):
            print("   ATENCAO: a OLX redirecionou para uma URL diferente da solicitada!")
        print()

        seletor_links = "a[href*='autos-e-pecas/carros-vans-e-utilitarios']"
        self.esperar_elementos(By.CSS_SELECTOR, seletor_links)

        # O scrollIntoView() direto (usado na primeira tentativa) "teleporta"
        # para o elemento, sem passar suavemente pelo caminho - e o lazy
        # loading da OLX parece depender de um scroll GRADUAL para disparar
        # o carregamento de preco/km (por isso so os 3 primeiros itens,
        # ja visiveis sem rolar nada, vinham completos). Aqui simulamos um
        # scroll humano: descemos a pagina aos poucos, com pequenas pausas,
        # dando tempo do lazy loading real disparar em cada trecho.
        self._rolar_pagina_gradualmente()

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

    def _rolar_pagina_gradualmente(self, passo_px: int = 400, pausa: float = 0.3, max_passos: int = 25):
        """
        Rola a pagina aos poucos (em vez de pular direto para um elemento),
        para dar tempo do lazy loading real da OLX carregar preco/km de
        cada card. Para quando a altura da pagina para de crescer (chegou
        ao fim do conteudo carregado) ou atinge o limite de passos.
        """
        altura_anterior = 0
        for _ in range(max_passos):
            self.driver.execute_script(f"window.scrollBy(0, {passo_px});")
            time.sleep(pausa)

            altura_atual = self.driver.execute_script("return document.body.scrollHeight")
            posicao_atual = self.driver.execute_script("return window.pageYOffset")

            # Chegou ao fim da pagina (nao da mais pra rolar mais)
            if posicao_atual + passo_px >= altura_atual and altura_atual == altura_anterior:
                break
            altura_anterior = altura_atual

        # Da um respiro final para qualquer requisicao de rede em andamento terminar
        time.sleep(0.5)

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
        # Usamos o ULTIMO numero de 4 digitos parecido com ano, nao o
        # primeiro - porque alguns modelos de carro tem numero no nome
        # (ex: "Peugeot 2008"), o que faria o primeiro match pegar o
        # nome do modelo em vez do ano real. O ano de verdade sempre
        # aparece por ultimo no texto do card.
        matches = self.PADRAO_ANO.findall(texto)
        return int(matches[-1]) if matches else None

    def listar_todos_os_links(self, url_busca: str):
        """
        Metodo de diagnostico: navega, rola a pagina inteira (igual o
        fluxo normal) e imprime TODOS os links que batem com o seletor,
        em ordem, com indice + id + titulo (so a primeira linha do texto).

        Nao filtra nada, nao aplica max_anuncios - mostra tudo que o
        seletor encontrou, para comparar diretamente com a ordem visual
        da pagina real (role a pagina no navegador ao lado e compare
        titulo por titulo).

        Tambem imprime a URL solicitada e a URL real apos o carregamento,
        para detectar se a OLX esta redirecionando para algo diferente
        do que pedimos.

        Uso:
            scraper = OlxScraper(headless=False)
            scraper.listar_todos_os_links("https://www.olx.com.br/...")
            scraper.fechar()
        """
        self.driver.get(url_busca)
        print(f"URL solicitada: {url_busca}")
        print(f"URL real apos carregar: {self.driver.current_url}")
        if url_busca.rstrip("/") != self.driver.current_url.rstrip("/"):
            print("   ATENCAO: a OLX redirecionou para uma URL diferente da solicitada!")
        print()

        seletor_links = "a[href*='autos-e-pecas/carros-vans-e-utilitarios']"
        self.esperar_elementos(By.CSS_SELECTOR, seletor_links)
        self._rolar_pagina_gradualmente()
        print(f"URL apos rolar a pagina: {self.driver.current_url}\n")

        links = self.driver.find_elements(By.CSS_SELECTOR, seletor_links)
        print(f"Total de links encontrados pelo seletor: {len(links)}\n")

        urls_vistas = set()
        for i, link in enumerate(links, start=1):
            url = link.get_attribute("href") or ""
            match_id = self.PADRAO_URL_ANUNCIO.search(url)
            duplicado = " [DUPLICADO]" if url in urls_vistas else ""
            valido = "OK" if match_id else "IGNORADO (nao bate no padrao de anuncio)"

            linhas = [l.strip() for l in link.text.split("\n") if l.strip()]
            titulo = linhas[0] if linhas else "(sem texto)"

            id_str = match_id.group(1) if match_id else "-"
            print(f"[{i:02d}] id={id_str} | {valido}{duplicado}")
            print(f"     titulo: {titulo}")
            print(f"     url: {url}\n")

            urls_vistas.add(url)

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