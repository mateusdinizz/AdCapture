# car-scraper

Sistema de captura automatizada de anúncios de carros usados/seminovos (OLX, Facebook Marketplace) para alimentar um fluxo constante de oportunidades de compra/revenda.

## Stack
- Python 3.11+
- Selenium (coleta de dados)
- pandas (limpeza e transformação)
- MySQL + SQLAlchemy (armazenamento)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # preencher com suas credenciais locais
```

## Estrutura do projeto

```
config/       -> configurações gerais (paths, constantes)
src/scrapers/ -> scrapers por plataforma (OLX, Marketplace)
src/database/ -> conexão e modelos do banco MySQL
src/etl/      -> limpeza, transformação e deduplicação dos dados
src/utils/    -> funções auxiliares (logger, helpers)
notebooks/    -> exploração de dados com pandas/Jupyter
tests/        -> testes automatizados
scripts/      -> pontos de entrada executáveis
sql/          -> schema e scripts SQL
```
