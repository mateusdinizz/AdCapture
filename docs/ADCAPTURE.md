# 🚗 Projeto: Captura de Anúncios de Carros (OLX / Marketplace)

> Arquivo de contexto do projeto — atualizar conforme o progresso avança. Última atualização: 2026-08-15 (Fase 2 concluída — scraper OLX validado ponta a ponta)

---

## 🎯 Objetivo do Projeto

Criar um sistema automatizado que **capture e centralize anúncios de carros usados/seminovos** publicados na OLX, Facebook Marketplace e outras plataformas, para que meu pai (vendedor de carros) tenha um fluxo constante de "produtos" (carros) disponíveis para comprar e revender.

### Problema que o projeto resolve

- Meu pai tem uma boa carteira de contatos/compradores para vender carros.
- O gargalo dele **não é vender**, é **encontrar carros para comprar e revender**.
- Ele nunca usou plataformas de anúncios (OLX, Marketplace) para captar esses carros — não tem o hábito nem o tempo de ficar garimpando manualmente.
- O sistema deve fazer esse garimpo automaticamente e entregar os anúncios organizados (idealmente filtráveis por marca, modelo, ano, preço, km, região).

### Resultado esperado (visão de longo prazo)

- Um pipeline que roda periodicamente, captura anúncios novos, limpa/organiza os dados e disponibiliza isso através de uma **interface própria** (não apenas planilha) para meu pai consultar.
- Histórico de preços dos anúncios (para identificar quando um vendedor abaixa o preço, o que ajuda na negociação).
- Visão de produto (não só scraper): **"Um sistema que encontra oportunidades de compra de carros para revenda."** O scraper encontra e centraliza os anúncios; a interface organiza, filtra, compara e destaca as oportunidades.

---

## 🖥️ Visão da Interface e Experiência do Sistema

> Definido em 12/08/2026. Documento completo com os mockups em texto está salvo separadamente — aqui fica o resumo estrutural para referência rápida.

### Conceito

Catálogo inteligente de carros: anúncios de diferentes fontes centralizados, filtráveis e organizados por critério de compra. Interface simples e visual, sem exigir conhecimento técnico do usuário final (meu pai).

### Áreas principais da aplicação

1. **Dashboard** — visão geral: total de anúncios, novos hoje, favoritos, oportunidades, últimos capturados.
2. **Anúncios** — tela principal, cards com foto, marca/modelo, ano, preço, km, cidade, fonte, data de captura, link original, botão de favoritar. Barra lateral de filtros (marca, modelo, faixa de preço, faixa de ano, faixa de km, cidade/estado, fonte, tipo de vendedor, data de captura) + busca + ordenação + paginação.
3. **Favoritos** — anúncios salvos pelo usuário para análise posterior.
4. **Perfil de compra / Configurações** — critérios de compra persistentes (ex: preço R$25k–80k, ano 2018–2025, até 100.000 km, região Recife + RMR).

### Funcionalidades futuras (pós-MVP)

- Página de detalhes do anúncio com histórico de preços (gráfico simples tipo `R$79.900 → R$76.900 → R$72.900`)
- Classificação visual de oportunidade (🟢 Boa oportunidade / 🟡 Analisar / 🔴 Fora do perfil) via sistema de pontuação
- Alertas automáticos quando um anúncio novo bate com o perfil de compra salvo

### Ordem de evolução planejada

```
MVP (anúncios + filtros)
 → Favoritos
 → Página de detalhes
 → Histórico de preços
 → Perfil de compra
 → Classificação/score de oportunidades
 → Alertas automáticos
```

### Arquitetura conceitual (visão geral do pipeline completo)

```
Scrapers → Dados capturados → ETL/pandas → MySQL → Interface
   (Filtros + Busca + Ordenação → Anúncios → Detalhes + Favoritos + Histórico → Perfil de compra → Oportunidades → Alertas)
```

### ✅ Decisão de stack fechada

**Frontend: Flask + Jinja2 + Tailwind CSS.** Motivo: aproveita conhecimento prévio em HTML/CSS, mantém tudo em Python (mesma linguagem do scraper/ETL/banco), dá controle total sobre o visual (prioridade: aparência profissional/customizável) sem a rigidez do Streamlit nem a complexidade de aprender React do zero. Testado com um exemplo mínimo funcional antes de aplicar no projeto real (ver notas).

---

## 🛠️ Ferramentas, Linguagem e Bibliotecas

|Categoria|Ferramenta|Função no projeto|
|---|---|---|
|Linguagem|Python 3.11+|Linguagem principal do projeto|
|Coleta de dados|Selenium + webdriver-manager|Automação de navegador para capturar anúncios (necessário pois Marketplace/OLX carregam conteúdo via JavaScript)|
|Manipulação de dados|pandas|Limpeza, normalização e deduplicação dos anúncios capturados|
|Banco de dados|MySQL|Armazenamento estruturado dos anúncios, histórico de preços etc.|
|Interface do banco|MySQL Workbench|Administração visual do banco, criação de schema|
|Conexão Python ↔ MySQL|SQLAlchemy + mysql-connector-python|Ponte entre pandas/Python e o banco MySQL|
|Configuração/segurança|python-dotenv|Guardar credenciais e configs fora do código-fonte|
|Backend web / Interface|Flask + Jinja2|Framework web leve em Python; Jinja2 é o motor de templates que insere dados Python dentro do HTML|
|Estilização|Tailwind CSS (via CDN inicialmente)|Classes utilitárias para estilizar rápido sem perder controle/customização do visual|
|Editor|VS Code|Ambiente de desenvolvimento|
|Versionamento|Git + GitHub|Controle de versão e histórico do projeto|
|Anotações/contexto|Obsidian|Este arquivo — acompanhamento do progresso do projeto|

### Bibliotecas descartadas por enquanto (simplificação)

- ~~`requests` + `BeautifulSoup4`~~ — não necessário porque o Selenium já resolve tanto a navegação quanto a extração de HTML.
- ~~`schedule` / `cron`~~ — agendamento automático fica para uma fase mais avançada, depois que o scraper estiver validado manualmente.

---

## 📊 Meu nível de conhecimento atual

|Ferramenta/Conceito|Nível|Observações|
|---|---|---|
|Python (geral)|✅ Já uso bibliotecas como pandas|Base sólida, não é o gargalo do projeto|
|pandas|✅ Já uso|Confortável com manipulação de dados|
|Selenium / automação de navegador|🟢 Testado com sucesso|Rodou exemplo funcional (books.toscrape.com) capturando título/preço/disponibilidade, salvando em CSV via pandas. Entendeu o fluxo geral (esperar elemento → achar cards → extrair campos); pode ter dúvidas pontuais ao aplicar na OLX — parar e revisar se necessário|
|Flask / Jinja2|🟡 Testado em exemplo mínimo|Já rodou um protótipo funcional (cards de carro + filtro de preço via GET); entende o fluxo básico rota → dados → template|
|HTML/CSS/JS|🟡 Já fiz páginas simples|Base suficiente para aproveitar no Flask + Jinja2|
|MySQL / MySQL Workbench|🟢 Testado com sucesso|Rodou o schema.sql sem erro, criou o banco car_scraper com 4 tabelas|
|SQLAlchemy|🟢 Testado com sucesso|Conexão via engine + sessionmaker funcionando; insert/select/delete via ORM testados ponta a ponta|
|Git/GitHub|_(a atualizar)_||

### Decisões sobre o repositório

- **Visibilidade:** Público (objetivo: portfólio)
- **Licença:** MIT
- **.gitignore:** Template Python do GitHub + complementos manuais (`.env`, dados capturados, logs de webdriver, etc.)
- **Cuidados por ser público:**
    - Nunca commitar dados reais capturados (telefone, nome de vendedor, dados de terceiros)
    - Avaliar se vale detalhar publicamente a lógica de scraping das plataformas desde o início, dado que os termos de uso da OLX/Marketplace restringem esse tipo de automação
    - Repositório pode começar como privado durante a fase de testes e ser tornado público depois de mais maduro — a troca é simples nas configurações do GitHub

---

## ⚠️ Riscos e Pontos de Atenção

- **Termos de uso:** OLX e Facebook Marketplace têm restrições quanto a scraping automatizado. Risco de bloqueio de IP e/ou suspensão de conta.
- **Marketplace exige login:** rodar o Selenium logado pode expor a conta pessoal/comercial do meu pai a suspensão. Considerar usar uma conta separada, pelo menos na fase de testes.
- **Selenium é mais "detectável" que requests simples:** por controlar um navegador real, sites conseguem identificar padrões de automação mais facilmente. Mitigar com delays humanizados, execução espaçada, e evitar rodar em excesso.
- **Plano B:** se o scraping automatizado se tornar inviável (bloqueios recorrentes), ter um processo alternativo (ex: captura manual assistida, parcerias oficiais).
- **robots.txt da OLX (descoberto na Fase 2):** o arquivo `robots.txt` da OLX contém `Disallow: /q/*` e outras regras bloqueando URLs de busca livre (parâmetro `?q=`), usadas quando alguém pesquisa pela barra de busca do site. **Decisão: o scraper usa apenas URLs de categoria + localização** (ex: `/autos-e-pecas/carros-vans-e-utilitarios/estado-pe/grande-recife/recife`), que não caem nessa restrição — nunca URLs com `?q=busca`.

---

## 🗂️ Estrutura do Repositório (referência)

```
car-scraper/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   └── settings.py
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py
│   │   ├── driver_factory.py
│   │   ├── olx_scraper.py
│   │   └── marketplace_scraper.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── queries.py
│   ├── etl/
│   │   ├── clean.py
│   │   ├── deduplicate.py
│   │   └── transform.py
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── notebooks/
├── tests/
├── scripts/
│   └── run_daily_capture.py
└── sql/
    └── schema.sql
```

---

## 🧩 Modelagem do banco

### ✅ Schema fechado (MVP de captura) — arquivo `sql/schema.sql`, 4 tabelas

- **fontes** — id, nome (OLX, Marketplace), url_base, ativo
- **anuncios** — id, fonte_id, id_externo, titulo, url, marca, modelo, ano, km, preco, cidade, estado, vendedor_tipo, ativo, **telefone, whatsapp, whatsapp_link**, data_captura (com `UNIQUE(fonte_id, id_externo)` pra evitar duplicar o mesmo anúncio, e índices em marca/modelo, preço, ano, cidade e data)
- **historico_precos** — id, anuncio_id, preco, data_registro
- **imagens** — id, anuncio_id, url_imagem, ordem

### Critério usado para decidir "tabela separada vs coluna na mesma tabela"

Só vale criar tabela filha quando a relação é genuinamente **1-para-muitos**. Se é **1-para-1**, a informação fica como coluna (aceitando `NULL` se for opcional) na própria tabela principal — separar nesse caso só adiciona JOIN desnecessário.

- `historico_precos` → 1 anúncio tem **N** preços ao longo do tempo → tabela separada ✅
- `imagens` → 1 anúncio tem **N** fotos → tabela separada ✅
- Contato do vendedor → 1 anúncio tem **no máximo 1** telefone/whatsapp → **não** é tabela separada, viraram colunas em `anuncios` (havia uma tabela `contatos_vendedor` no rascunho inicial, removida por ser 1-para-1 desnecessariamente separado)

Esse mesmo critério deve ser aplicado quando for modelar `favoritos` e `perfis_compra` na fase de interface (favoritos É 1-para-muitos por natureza — 1 usuário favorita N anúncios — então tabela separada está correta nesse caso).

### Acesso ao anúncio / contato com o vendedor

- **Caminho principal e garantido:** campo `url` em `anuncios` — link direto pro anúncio original (OLX/Marketplace). É o botão de destaque do card ("Ver anúncio"), porque leva pra dentro da própria plataforma, onde o contato de fato acontece (chat interno da OLX, Messenger no Marketplace).
- **Caminho alternativo, não garantido:** `whatsapp_link` — só existe quando o vendedor optou por expor o número no anúncio (minoria dos casos, principalmente na OLX). Deve aparecer como ação **secundária** no card (ex: ícone pequeno ao lado do botão principal), nunca substituindo o link do anúncio.
- Na prática da interface: todo card sempre tem o botão "Ver anúncio"; o botão de WhatsApp só renderiza condicionalmente, quando `whatsapp_link IS NOT NULL`.

### Tabelas novas — necessárias pela visão de interface (implementar na fase de interface, não no MVP de captura)

- **usuarios** — id, nome, email (mesmo sendo uso pessoal/familiar no início, já modelar pensando em múltiplos usuários facilita evoluir depois)
- **favoritos** — id, usuario_id, anuncio_id, data_criacao _(1-para-muitos genuíno: 1 usuário favorita N anúncios — tabela separada correta)_
- **perfis_compra** — id, usuario_id, nome_perfil, preco_min, preco_max, ano_min, ano_max, km_max, regiao, ativo
- **oportunidades** _(fase futura, junto com o score)_ — id, anuncio_id, perfil_compra_id, score, classificacao (boa/analisar/fora_do_perfil), data_calculo

> Nota: as tabelas de `usuarios`/`favoritos`/`perfis_compra` só fazem sentido depois que existir uma camada de interface/autenticação — não implementar antes da hora. No MVP de captura (Fases 1-3 do roadmap), focar só nas tabelas de dados brutos.

---

## ✅ Objetivos / Roadmap

### Fase 0 — Fundamentos ✅

- [x] Confirmar Chrome instalado na máquina de desenvolvimento
- [x] Rodar um exemplo simples de Selenium (fora do projeto) para entender o fluxo básico (abrir página → esperar elemento → extrair dado → fechar navegador)
- [x] Criar repositório no GitHub com a estrutura de pastas definida

### Fase 1 — Banco de dados ✅

- [x] Desenhar o schema definitivo
- [x] Criar o `schema.sql`
- [x] Rodar o script no MySQL Workbench e confirmar execução sem erros
- [x] Testar conexão Python → MySQL via SQLAlchemy (insert manual de teste)

### Fase 2 — Primeiro scraper (OLX) ✅

- [x] Criar `driver_factory.py` (setup do Chrome/Selenium, com camadas anti-detecção)
- [x] Criar `base_scraper.py` (estrutura comum, waits, métodos abstratos)
- [x] Criar `olx_scraper.py` funcional, capturando um conjunto pequeno de anúncios de teste
- [x] Validar dados capturados manualmente (rodado contra o site real — título, preço, km, ano confirmados)
- [x] Rodar a versão corrigida e confirmar que preço/km vêm completos em todos os itens, não só nos primeiros
- [x] Bairro exato — decidido usar aproximação pela região buscada (cidade_padrao); bairro específico fica como melhoria futura, não bloqueia o fechamento da fase

### Fase 3 — ETL com pandas

- [ ] Função de limpeza de preço, km, ano (normalizar formatos)
- [ ] Função de deduplicação de anúncios
- [ ] Pipeline conectando scraper → limpeza → MySQL

> **Backlog avaliado (não agendado ainda):** Integração com API da FIPE (terceiro, `parallelum.com.br`) para substituir a heurística de regex de marca/modelo por dados oficiais, e futuramente comparar preço do anúncio com preço FIPE (alimenta a Fase 11 - Score de oportunidades).
> 
> **Avaliação feita em 2026-08-15:** API não é uma consulta direta - exige cascata de 4 chamadas (marcas → modelos → anos → valor), limite de 500 req/dia grátis (1000 com token), e o trabalho real está no **matching difuso** entre o título capturado (ex: "Onix Plus LTZ") e o nome oficial da FIPE (ex: "ONIX PLUS 10 MT LTZ") - exige lib de similaridade de texto (`rapidfuzz`), sujeito a erros. Estimativa: ~8-14h de trabalho (cliente API + cache local + matching + validação + integração no banco), prováveis 3-5 sessões.
> 
> **Decisão: adiado.** Isso já está coberto pela Fase 11 (Score de oportunidades) do roadmap - não desbloqueia nada usável antes da interface existir, e a heurística de regex atual (`extrair_marca_modelo` em `clean.py`) já foi validada com 12 títulos reais, incluindo casos difíceis (Peugeot 2008, Citroën C3, Chevrolet S10). Reavaliar quando chegar na Fase 11.

### Fase 4 — Segunda fonte (Marketplace)

- [ ] Avaliar estratégia de login (conta separada?)
- [ ] Criar `marketplace_scraper.py`
- [ ] Integrar ao mesmo pipeline de ETL

### Fase 5 — Definir stack de interface ✅

- [x] Decidir tecnologia de frontend (Streamlit? Flask/Django + HTML? React separado? App desktop?) → **Flask + Jinja2 + Tailwind CSS**
- [x] Validar a escolha considerando meu nível de conhecimento atual → testado com exemplo mínimo funcional (cards de carro + filtro por preço)

### Fase 6 — MVP de Interface (Anúncios + Filtros)

- [ ] Tela de Anúncios com cards (foto, marca/modelo, ano, preço, km, cidade, fonte, data captura, link, favoritar)
- [ ] Barra lateral de filtros (marca, modelo, faixa de preço, faixa de ano, faixa de km, cidade/estado, fonte, tipo de vendedor, data)
- [ ] Busca, ordenação e paginação
- [ ] Testar usabilidade com meu pai

### Fase 7 — Dashboard

- [ ] Tela inicial com totais (anúncios encontrados, novos hoje, favoritos, oportunidades) e últimos capturados

### Fase 8 — Favoritos

- [ ] Tabela `favoritos` + `usuarios` no banco
- [ ] Tela de Favoritos na interface

### Fase 9 — Página de detalhes + histórico de preços

- [ ] Modal/página de detalhes do anúncio
- [ ] Gráfico/lista de histórico de preços (usando a tabela `historico_precos`)

### Fase 10 — Perfil de compra

- [ ] Tabela `perfis_compra`
- [ ] Tela de configuração de critérios de compra
- [ ] Destacar automaticamente anúncios dentro do perfil

### Fase 11 — Score de oportunidades e alertas (futuro)

- [ ] Sistema de pontuação (🟢 boa oportunidade / 🟡 analisar / 🔴 fora do perfil)
- [ ] Tabela `oportunidades`
- [ ] Alertas automáticos de novos anúncios dentro do perfil

### Fase 12 — Automação (futuro)

- [ ] Definir frequência ideal de execução
- [ ] Implementar agendamento (schedule ou cron)
- [ ] Monitoramento de falhas/bloqueios

---

## 📝 Notas e Decisões ao longo do projeto

> Espaço livre para registrar decisões técnicas, problemas encontrados e soluções, conforme o projeto avança.

### 🔖 Onde paramos (retomar por aqui)
Fase 2 concluída — scraper da OLX funcionando ponta a ponta (título, preço, km, ano e link corretos em todos os anúncios testados). Próximo passo: **Fase 3 — ETL com pandas**: função de limpeza de preço/km/ano (normalizar formatos, já que o scraper hoje entrega dados relativamente limpos, mas vale garantir robustez), função de deduplicação de anúncios, e o pipeline conectando scraper → limpeza → MySQL (usando os models do `src/database/models.py` já validados na Fase 1).

- 2026-08-12: Decisão de simplificar a stack inicial removendo `requests`/`BeautifulSoup4` e `schedule`/`cron` das dependências imediatas, focando primeiro em Selenium + pandas + MySQL.
- 2026-08-12: Definido que o repositório no GitHub será público (objetivo de portfólio), com licença MIT e `.gitignore` baseado no template Python + complementos manuais. Atenção especial para nunca versionar dados capturados reais ou credenciais.
- 2026-08-12: Definida a visão de interface e experiência do sistema — o projeto deixa de ser "só um scraper" e passa a ter visão de produto completo (dashboard, anúncios com filtros, favoritos, perfil de compra, score de oportunidades, alertas). Modelagem do banco expandida com tabelas de `usuarios`, `favoritos`, `perfis_compra` e `oportunidades` (implementação adiada para as fases de interface). Stack de frontend ainda não decidida — vira decisão pendente no roadmap (Fase 5).
- 2026-08-12: **Stack de frontend definida: Flask + Jinja2 + Tailwind CSS** (venceu Streamlit, Django e FastAPI+React na comparação — melhor equilíbrio entre aproveitar conhecimento prévio em HTML/CSS, manter tudo em Python e ter controle total do visual). Testado com um exemplo mínimo (cards de carro fictícios + filtro de preço via query string). Lição aprendida no processo: comentários HTML (`<!-- -->`) não protegem `{% %}` / `{{ }}` de serem interpretados pelo Jinja2 — o motor de templates processa essas tags antes do HTML existir de fato; usar `{% raw %}...{% endraw %}` se precisar mesmo exibir chaves Jinja como texto literal.
- 2026-08-13: **Fase 0 concluída.** Teste com Selenium rodado com sucesso (site de prática books.toscrape.com) — abriu o Chrome, esperou elementos carregarem, extraiu título/preço/disponibilidade de todos os "cards" da página, organizou com pandas e salvou em CSV. Fluxo geral compreendido; dúvidas pontuais serão resolvidas quando aparecerem durante a construção do scraper real da OLX. Próximo passo: modelagem do banco (Fase 1).
- 2026-08-13: **Schema do MVP de captura fechado** (`sql/schema.sql`) — 5 tabelas (fontes, anuncios, historico_precos, imagens, contatos_vendedor), com UNIQUE em `(fonte_id, id_externo)` pra evitar duplicatas, índices nos campos de filtro, `DECIMAL(10,2)` pro preço e `ON DELETE CASCADE` nas tabelas filhas. Validado manualmente (ordem de criação das FKs, balanceamento de sintaxe) — validação real de execução ainda pendente no MySQL Workbench do usuário.
- 2026-08-13: Discutido como o usuário acessa o anúncio/contata o vendedor a partir do card. Definido que o campo `url` (link do anúncio original) é o caminho principal e garantido, já que tanto OLX quanto Marketplace concentram o contato em chat interno da própria plataforma. Telefone/WhatsApp são complementares, quando o vendedor expõe. Adicionado `whatsapp_link` (formato `https://wa.me/55...`) na tabela `contatos_vendedor`, montado no ETL, pra virar botão de ação de um clique no card.
- 2026-08-14: **Schema simplificado de 5 para 4 tabelas.** Análise crítica identificou que `contatos_vendedor` era uma relação 1-para-1 (1 anúncio tem no máximo 1 telefone/whatsapp) modelada incorretamente como tabela separada (1-para-muitos). Colunas `telefone`, `whatsapp`, `whatsapp_link` movidas para dentro de `anuncios` como campos opcionais (`NULL`). Critério fixado: só separar em tabela filha quando a relação for genuinamente 1-para-muitos (caso de `historico_precos` e `imagens`, mantidas). Mesmo critério já aplicado retroativamente à decisão sobre `favoritos` (1-para-muitos genuíno, tabela separada permanece correta).
- 2026-08-14: **Fase 1 concluída.** `schema.sql` executado no MySQL Workbench sem erros (banco `car_scraper` criado com as 4 tabelas). Implementados `src/database/connection.py` (engine SQLAlchemy + `get_session()` context manager) e `src/database/models.py` (classes ORM `Fonte`, `Anuncio`, `HistoricoPreco`, `Imagem`, espelhando o schema.sql). Script `scripts/testar_conexao_db.py` criado e rodado com sucesso: conectou, buscou a fonte OLX, inseriu anúncio de teste + histórico de preço, leu de volta via pandas, e removeu os dados de teste automaticamente. Pipeline Python ↔ MySQL validado ponta a ponta. Próximo passo: Fase 2 — primeiro scraper (OLX) com Selenium.
- 2026-08-14: **Fase 2 iniciada.** Criados `driver_factory.py` (config do Chrome integrada ao .env) e `base_scraper.py` (classe base com waits reutilizáveis). URLs de busca confirmadas: Recife e Jaboatão dos Guararapes (Candeias/Piedade são bairros dessa cidade, cobertos automaticamente). Criado `olx_scraper.py` com estratégia de extração por padrão de URL + regex (mais resiliente a mudanças de CSS que a OLX faz com frequência) — ainda não testado contra o site real, aguardando validação do usuário. **Descoberto o `robots.txt` da OLX**, que bloqueia URLs de busca livre (`?q=`) — decisão tomada de usar só URLs de categoria+localização, nunca busca por texto livre.
- 2026-08-14: **Primeiro teste real do scraper contra a OLX (modo debug).** Resultado revelou que o próprio link do anúncio já contém título, km, ano e preço no texto — não é necessário (e é prejudicial) subir para elementos "pai", porque em níveis mais altos da árvore o texto passa a misturar vários anúncios vizinhos ao mesmo tempo (bug real identificado e corrigido). Cidade/bairro não foi encontrada em nenhum nível — resolvido usando a região buscada (Recife/Jaboatão) como aproximação via parâmetro `cidade_padrao`.
- 2026-08-14: **Primeira rodada completa do scraper (20 anúncios, Recife + Jaboatão).** Título e ano vieram corretos em 100% dos casos. Preço e km só vieram completos nos 3 primeiros itens de cada busca — diagnosticado como **lazy loading**: a OLX só renderiza preço/km de verdade quando o card entra na área visível da tela. Também identificado bug no regex de ano: pegava o primeiro número de 4 dígitos parecido com ano, mas alguns modelos têm número no nome (ex: "Peugeot 2008"), fazendo o scraper capturar o nome do modelo em vez do ano real.
- 2026-08-14: **Correções aplicadas ao `olx_scraper.py`:** (1) adicionado `scrollIntoView()` + espera curta pelo "R$" aparecer antes de ler o texto de cada card, forçando o lazy loading a carregar; (2) `_extrair_ano` corrigido para pegar o **último** número de 4 dígitos do texto, não o primeiro (o ano real sempre aparece por último; testado e confirmado com o caso real do "Peugeot 2008" → agora extrai 2017 corretamente). Correções validadas por simulação com os dados reais coletados, mas **ainda não re-testadas contra o site ao vivo** — próximo passo ao retomar o projeto.
- 2026-08-15: **Fase 2 concluída.** Descoberta importante que corrige o diagnóstico anterior: o bug do "link genérico" (redirecionando pra home) **não era causado por virtualização de scroll ou lazy loading do href** — era um problema de **formatação do CSV**: campos sem aspas (quoting) faziam vírgulas dentro de algum valor (ex: título com vírgula) deslocarem as colunas seguintes, corrompendo a URL lida. Corrigido usando aspas para delimitar os campos no CSV. Em paralelo, o `coletar_anuncios` também foi alinhado ao comportamento do `listar_todos_os_links` (removido o scroll individual por item, que causava vaivém de scroll). Com as duas correções, um novo teste completo confirmou: título, ano, preço e km vêm corretos em 100% dos anúncios (não só nos 3 primeiros), e os links abrem o anúncio certo. Scraper da OLX validado ponta a ponta. Próximo passo: Fase 3 (ETL com pandas).
- 2026-08-15: Avaliada a integração com a API da FIPE para enriquecer marca/modelo e futuro comparativo de preço. Decisão: adiar para a Fase 11 (já é o lugar natural no roadmap), evitando interromper o momentum atual (Fase 3/4) por uma funcionalidade que só teria valor de uso depois que a interface existir. Detalhes da avaliação de esforço registrados no roadmap.