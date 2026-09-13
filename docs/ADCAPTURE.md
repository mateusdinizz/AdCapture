# 🚗 Projeto: Captura de Anúncios de Carros (OLX / Marketplace)

> Arquivo de contexto do projeto — atualizar conforme o progresso avança. Última atualização: 2026-09-10 (Fase 7 concluída — Dashboard; numeração do roadmap corrigida)

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
 → Dashboard
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
|Estilização|Tailwind CSS (via CDN) + Lucide Icons (via CDN)|Classes utilitárias para estilizar rápido; ícones consistentes na interface|
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
|Selenium / automação de navegador|🟢 Testado com sucesso|Scraper da OLX funcionando ponta a ponta em produção (4 cidades)|
|Flask / Jinja2|🟢 Testado com sucesso|Interface completa rodando (Anúncios + Filtros + Dashboard), consumindo dados reais do MySQL|
|HTML/CSS/JS|🟡 Já fiz páginas simples|Suficiente para o que o projeto pediu até aqui|
|MySQL / MySQL Workbench|🟢 Testado com sucesso|Banco em uso ativo com dados reais (180+ anúncios)|
|SQLAlchemy|🟢 Testado com sucesso|ORM em uso ativo (queries com filtros dinâmicos, agregações para dashboard)|
|Git/GitHub|🟢 Em uso|Commits regulares a cada fase concluída|

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
- **Marketplace exige login:** rodar o Selenium logado pode expor a conta pessoal/comercial do meu pai a suspensão. Considerar usar uma conta separada, pelo menos na fase de testes. *(Decisão atual: Marketplace adiado — ver seção de roadmap)*
- **Selenium é mais "detectável" que requests simples:** por controlar um navegador real, sites conseguem identificar padrões de automação mais facilmente. Mitigar com delays humanizados, execução espaçada, e evitar rodar em excesso.
- **Plano B:** se o scraping automatizado se tornar inviável (bloqueios recorrentes), ter um processo alternativo (ex: captura manual assistida, parcerias oficiais).
- **robots.txt da OLX (descoberto na Fase 2):** o arquivo `robots.txt` da OLX contém `Disallow: /q/*` e outras regras bloqueando URLs de busca livre (parâmetro `?q=`), usadas quando alguém pesquisa pela barra de busca do site. **Decisão: o scraper usa apenas URLs de categoria + localização** (ex: `/autos-e-pecas/carros-vans-e-utilitarios/estado-pe/grande-recife/recife`), que não caem nessa restrição — nunca URLs com `?q=busca`.

---

## 🗂️ Estrutura do Repositório (atualizada)

```
AdCapture/
├── app.py                    <- Flask, ponto de entrada da interface
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   └── settings.py
├── templates/
│   ├── base.html
│   ├── anuncios.html
│   └── dashboard.html
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py
│   │   ├── driver_factory.py
│   │   ├── olx_scraper.py
│   │   └── marketplace_scraper.py   <- ainda não criado (Marketplace adiado)
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── queries.py
│   ├── etl/
│   │   ├── clean.py
│   │   ├── deduplicate.py
│   │   └── transform.py             <- ainda não criado
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── notebooks/
├── tests/
├── scripts/
│   ├── testar_conexao_db.py
│   ├── rodar_scraper_olx.py
│   └── executar_pipeline.py
└── sql/
    └── schema.sql
```

---

## 🧩 Modelagem do banco

### ✅ Schema fechado (MVP de captura) — arquivo `sql/schema.sql`, 4 tabelas

- **fontes** — id, nome (OLX, Marketplace), url_base, ativo
- **anuncios** — id, fonte_id, id_externo, titulo, url, marca, modelo, ano, km, preco, cidade, estado, vendedor_tipo, ativo, **telefone, whatsapp, whatsapp_link**, data_captura (com `UNIQUE(fonte_id, id_externo)` pra evitar duplicar o mesmo anúncio, e índices em marca/modelo, preço, ano, cidade e data)
- **historico_precos** — id, anuncio_id, preco, data_registro
- **imagens** — id, anuncio_id, url_imagem, ordem *(tabela existe, mas ainda não é populada — o scraper não captura imagens ainda, ver backlog na Fase 2)*

### Critério usado para decidir "tabela separada vs coluna na mesma tabela"

Só vale criar tabela filha quando a relação é genuinamente **1-para-muitos**. Se é **1-para-1**, a informação fica como coluna (aceitando `NULL` se for opcional) na própria tabela principal — separar nesse caso só adiciona JOIN desnecessário.

- `historico_precos` → 1 anúncio tem **N** preços ao longo do tempo → tabela separada ✅
- `imagens` → 1 anúncio tem **N** fotos → tabela separada ✅
- Contato do vendedor → 1 anúncio tem **no máximo 1** telefone/whatsapp → **não** é tabela separada, viraram colunas em `anuncios`

### Acesso ao anúncio / contato com o vendedor

- **Caminho principal e garantido:** campo `url` em `anuncios` — link direto pro anúncio original. É o botão de destaque do card ("Ver anúncio").
- **Caminho alternativo, não garantido:** `whatsapp_link` — só existe quando o vendedor optou por expor o número. Aparece como ação **secundária**, condicional, no card.

### Tabelas futuras — a serem criadas quando a fase correspondente chegar

- **favoritos** — id, anuncio_id, data_criacao. **Sem tabela `usuarios` por enquanto** (ver decisão de 2026-09-11 nas notas) — ferramenta de uso pessoal/familiar, sem sistema de login; lista de favoritos compartilhada, não por usuário individual. Se algum dia for necessário multiusuário de verdade, revisitar essa decisão e adicionar `usuarios` + `usuario_id` em `favoritos` nesse momento.
- **perfis_compra** — id, nome_perfil, preco_min, preco_max, ano_min, ano_max, km_max, regiao, ativo (mesma lógica: sem dono/usuário por enquanto)
- **oportunidades** _(fase futura, junto com o score)_ — id, anuncio_id, perfil_compra_id, score, classificacao (boa/analisar/fora_do_perfil), data_calculo

---

## ✅ Objetivos / Roadmap

> Numeração corrigida em 2026-09-11 — havia uma inconsistência entre o roadmap e as notas (Dashboard aparecia como Fase 7 nas notas e Fase 8 no roadmap). Sequência abaixo é a oficial daqui pra frente.

### Fase 0 — Fundamentos ✅
- [x] Confirmar Chrome instalado na máquina de desenvolvimento
- [x] Rodar um exemplo simples de Selenium (fora do projeto) para entender o fluxo básico
- [x] Criar repositório no GitHub com a estrutura de pastas definida

### Fase 1 — Banco de dados ✅
- [x] Desenhar o schema definitivo
- [x] Criar o `schema.sql`
- [x] Rodar o script no MySQL Workbench e confirmar execução sem erros
- [x] Testar conexão Python → MySQL via SQLAlchemy (insert manual de teste)

### Fase 2 — Primeiro scraper (OLX) ✅
- [x] Criar `driver_factory.py` (setup do Chrome/Selenium, com camadas anti-detecção)
- [x] Criar `base_scraper.py` (estrutura comum, waits, métodos abstratos)
- [x] Criar `olx_scraper.py` funcional
- [x] Validar dados capturados manualmente contra o site real
- [x] Confirmar que preço/km vêm completos em todos os itens
- [x] Bairro exato — decidido usar aproximação pela região buscada (cidade_padrao); bairro específico fica como melhoria futura
- [ ] **Backlog:** captura de imagens do anúncio (tabela `imagens` já existe no banco, mas nunca é populada — scraper não extrai URLs de foto ainda)

### Fase 3 — ETL com pandas ✅
- [x] Função de limpeza de preço, km, ano (normalizar formatos)
- [x] Função de deduplicação de anúncios
- [x] Pipeline conectando scraper → limpeza → MySQL

> **Backlog avaliado (não agendado):** Integração com API da FIPE (terceiro, `parallelum.com.br`) para substituir a heurística de regex de marca/modelo por dados oficiais, e futuramente comparar preço do anúncio com preço FIPE. Estimativa: ~8-14h (cliente API + cache local + matching difuso + validação + integração no banco). **Decisão: adiado até a fase de Score de oportunidades**, quando o dado de referência de preço passa a ter uso real na interface.

### Fase 4 — Ampliar captura OLX ✅
- [x] Aumentar `max_anuncios` por região (de 10-20 para valores maiores)
- [x] Adicionar Olinda e Paulista como novas regiões de busca
- [ ] **Camaragibe ainda não foi implementado** — estava no plano original da fase mas não foi feito; fica como pendência aberta, baixa prioridade (adicionar é trivial: mesma lógica de URL do `olx_scraper.py`, só falta confirmar o slug correto da cidade)
- [x] Rodar o pipeline algumas vezes para "engordar" a base antes de conectar à interface

### Fase 5 — Definir stack de interface ✅
- [x] Decidir tecnologia de frontend → **Flask + Jinja2 + Tailwind CSS**
- [x] Validar a escolha com exemplo mínimo funcional

### Fase 6 — MVP de Interface (Anúncios + Filtros) ✅
- [x] Tela de Anúncios com cards (marca/modelo, ano, preço, km, cidade, fonte, link)
- [x] Barra lateral de filtros (marca, modelo, faixa de preço, faixa de ano, km máximo, busca, ordenação)
- [x] Busca e ordenação funcionando
- [x] **Testado por mim (desenvolvedor)** — funcionando corretamente com dados reais
- [ ] **Testado pelo meu pai (uso real)** — ainda não aconteceu; são coisas diferentes e vale rastrear separado

### Fase 7 — Dashboard ✅
- [x] Tela com totais reais (total capturado, novos hoje)
- [x] Substituídos "Favoritos" e "Oportunidades" (não implementados ainda) por "Marca mais comum" e "Cidade com mais anúncios"
- [x] Gráfico de distribuição por marca (CSS puro, sem biblioteca nova)
- [x] Lista dos últimos anúncios capturados

### Fase [Marketplace] — condicional, não agendada
> Movida para depois da interface MVP (decisão de 2026-09-05).
> **Critério objetivo de retomada:** implementar quando o volume da OLX (já ampliada) se mostrar insuficiente no uso real do meu pai — não por suposição antecipada.
- [ ] Avaliar estratégia de login (conta separada?)
- [ ] Criar `marketplace_scraper.py`
- [ ] Integrar ao mesmo pipeline de ETL

### Fase 8 — Favoritos
> **Escopo simplificado em 2026-09-11:** sem tabela `usuarios` nem login — ferramenta de uso pessoal/familiar, lista de favoritos compartilhada. Revisitar essa decisão só se um dia for necessário multiusuário de verdade.
- [ ] Tabela `favoritos` (id, anuncio_id, data_criacao) — sem `usuario_id`
- [ ] Botão de favoritar funcional nos cards (hoje está oculto)
- [ ] Tela de Favoritos na interface

### Fase 9 — Página de detalhes + histórico de preços
- [ ] Modal/página de detalhes do anúncio
- [ ] Gráfico/lista de histórico de preços (usando a tabela `historico_precos`, já alimentada desde a Fase 3)

### Fase 10 — Perfil de compra
- [ ] Tabela `perfis_compra` (sem dono/usuário, mesma lógica da Fase 8)
- [ ] Tela de configuração de critérios de compra
- [ ] Destacar automaticamente anúncios dentro do perfil

### Fase 11 — Score de oportunidades e alertas (futuro)
- [ ] Sistema de pontuação (🟢 boa oportunidade / 🟡 analisar / 🔴 fora do perfil)
- [ ] Tabela `oportunidades`
- [ ] Reavaliar integração com FIPE aqui (ver backlog da Fase 3)
- [ ] Alertas automáticos de novos anúncios dentro do perfil

### Fase 12 — Automação (futuro)
- [ ] Definir frequência ideal de execução
- [ ] Implementar agendamento (schedule ou cron)
- [ ] Monitoramento de falhas/bloqueios

---

## 📝 Notas e Decisões ao longo do projeto

> Espaço livre para registrar decisões técnicas, problemas encontrados e soluções, conforme o projeto avança.

### 🔖 Onde paramos (retomar por aqui)
Fases 0-7 concluídas e commitadas — captura OLX (4 cidades), banco, ETL/pipeline, interface web (Anúncios + Filtros + Dashboard) funcionando ponta a ponta com dados reais. Numeração do roadmap corrigida (Dashboard = Fase 7, oficialmente). Próximo passo: **Fase 8 — Favoritos**, com escopo simplificado (sem login/usuários).

- 2026-08-12: Decisão de simplificar a stack inicial removendo `requests`/`BeautifulSoup4` e `schedule`/`cron` das dependências imediatas, focando primeiro em Selenium + pandas + MySQL.
- 2026-08-12: Definido que o repositório no GitHub será público (objetivo de portfólio), com licença MIT e `.gitignore` baseado no template Python + complementos manuais.
- 2026-08-12: Definida a visão de interface e experiência do sistema — o projeto deixa de ser "só um scraper" e passa a ter visão de produto completo.
- 2026-08-12: **Stack de frontend definida: Flask + Jinja2 + Tailwind CSS.** Lição aprendida: comentários HTML (`<!-- -->`) não protegem `{% %}`/`{{ }}` de serem interpretados pelo Jinja2.
- 2026-08-13: **Fase 0 concluída.** Teste com Selenium rodado com sucesso (books.toscrape.com).
- 2026-08-13: **Schema do MVP de captura fechado** (5 tabelas nessa versão inicial), validado manualmente.
- 2026-08-13: Definido que `url` é o caminho principal de contato/acesso ao anúncio; `whatsapp_link` complementar.
- 2026-08-14: **Schema simplificado de 5 para 4 tabelas** — `contatos_vendedor` era 1-para-1, virou colunas em `anuncios`. Critério fixado: só separar em tabela filha quando a relação for genuinamente 1-para-muitos.
- 2026-08-14: **Fase 1 concluída.** `schema.sql` executado sem erros. `connection.py` e `models.py` implementados e testados ponta a ponta via `testar_conexao_db.py`.
- 2026-08-14: **Fase 2 iniciada.** `driver_factory.py` e `base_scraper.py` criados. URLs de Recife e Jaboatão confirmadas. **Descoberto o `robots.txt` da OLX**, que bloqueia URLs de busca livre (`?q=`) — decisão de usar só URLs de categoria+localização.
- 2026-08-14: Primeiro teste real (modo debug) revelou que o link do anúncio já contém título/km/ano/preço no próprio texto — subir para elementos "pai" misturava vários anúncios ao mesmo tempo (bug identificado e evitado).
- 2026-08-14: Primeira rodada completa (20 anúncios) — preço/km incompletos além dos 3 primeiros itens (lazy loading); bug no regex de ano corrigido (pegava "2008" do "Peugeot 2008" em vez do ano real — corrigido para pegar o último número de 4 dígitos, não o primeiro).
- 2026-08-15: **Fase 2 concluída.** Causa real do bug do "link genérico" identificada: **não era scroll/lazy loading**, era **formatação do CSV sem aspas** — vírgulas dentro de campos (títulos) deslocavam colunas e corrompiam a URL lida. Corrigido com `quoting=csv.QUOTE_NONNUMERIC`. `coletar_anuncios` também alinhado ao comportamento do `listar_todos_os_links` (removido scroll individual por item). Scraper validado ponta a ponta.
- 2026-08-15: Avaliada integração com API da FIPE — adiada para a fase de Score de oportunidades (não desbloqueia nada usável antes da interface existir).
- 2026-09-05: **Fase 3 concluída.** `clean.py`, `deduplicate.py` e `executar_pipeline.py` implementados e testados com dois lotes reais de 40 anúncios cada, 100% com marca identificada em ambos.
- 2026-09-05: **Anomalia não resolvida (baixo impacto):** anúncio "GWM Haval H6" apareceu com marca/modelo corretos mesmo "GWM" não estando na lista de marcas conhecidas. Investigado exaustivamente sem causa encontrada (não é cache, não é arquivo duplicado, não é inserção manual). Print de debug deixado em `limpar_anuncio()` (dispara só se "GWM" aparecer no título) para flagrar se acontecer de novo:
  ```python
  marca, modelo = extrair_marca_modelo(limpo.get("titulo"))

  # DEBUG TEMPORARIO - remover depois de descobrir a causa do caso GWM
  if limpo.get("titulo") and "GWM" in limpo.get("titulo", ""):
      print(f"[DEBUG] titulo={limpo.get('titulo')!r}")
      print(f"[DEBUG] marca ANTES (vinda do scraper)={limpo.get('marca')!r}")
      print(f"[DEBUG] marca extraida agora por extrair_marca_modelo={marca!r}, modelo={modelo!r}")

  limpo["marca"] = limpo.get("marca") or marca
  limpo["modelo"] = limpo.get("modelo") or modelo

  if limpo.get("titulo") and "GWM" in limpo.get("titulo", ""):
      print(f"[DEBUG] marca FINAL apos o 'or'={limpo['marca']!r}, modelo FINAL={limpo['modelo']!r}")
  ```
  Se disparar de novo, colar a saída completa numa conversa nova pra retomar a investigação.
- 2026-09-05: **Decisão estratégica: Marketplace adiado para depois da interface MVP.** Estrutura já preparada para múltiplas fontes desde a Fase 1 (não gera retrabalho); Marketplace estimado em 2-4x o esforço da OLX (login, anti-bot mais agressivo, risco de suspensão de conta); gargalo real era "nenhuma interface", não "poucas fontes". Critério objetivo de retomada: volume insuficiente no uso real, não suposição.
- 2026-09-10: **Fase 6 concluída.** Interface web construída com Flask + Jinja2, adaptando um template visual (estilo indigo/slate, fornecido pelo usuário) para consumir dados reais do banco via SQLAlchemy. Badge/preço FIPE removido, botão de favoritar oculto (Fase 8), checkbox Marketplace desabilitado ("em breve"), campo Modelo virou busca de texto livre, campos de Ano viraram numéricos livres, fotos substituídas por ícone neutro (backlog). Estatísticas do cabeçalho via `context_processor` do Flask.
- 2026-09-10: **Bug encontrado e corrigido:** slider de km com teto padrão de 200.000 km escondia anúncios silenciosamente mesmo sem filtro aplicado pelo usuário (usuário viu 177 de 181 anúncios). Corrigido tratando o valor máximo do slider (agora 300.000) como "sem limite" explícito. Lição: controles de UI com valor padrão sempre preenchido podem filtrar dados sem o usuário perceber.
- 2026-09-10: **Fase 7 concluída.** Rota `/dashboard` criada reaproveitando o `context_processor`. Testado incluindo caso de banco vazio (proteção contra divisão por zero no gráfico de barras).
- 2026-09-11: **Auditoria do arquivo de contexto.** Corrigidas inconsistências: numeração do roadmap alinhada (Dashboard oficialmente Fase 7, Marketplace sem número fixo por ser condicional); item "Camaragibe" da Fase 4 estava marcado como feito sem ter sido implementado — corrigido para pendência aberta; item "testado com meu pai" da Fase 6 separado em dois (teste técnico meu ✅, uso real do pai ainda pendente); estrutura do repositório atualizada para refletir `app.py`/`templates/`; backlog de captura de imagens explicitado na Fase 2. **Decisão adicional:** Favoritos (Fase 8) e Perfil de compra (Fase 10) simplificados para não exigir tabela `usuarios`/login — ferramenta de uso pessoal/familiar, sem necessidade de multiusuário real por enquanto; revisitar só se isso mudar.