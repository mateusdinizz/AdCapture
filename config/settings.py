"""
Configuracoes gerais do projeto.

Centraliza a leitura de variaveis de ambiente (.env) e constantes
usadas em varias partes do codigo, para evitar valores "soltos"
espalhados pelos scrapers, ETL e conexao com banco.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Banco de dados ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "car_scraper")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# --- Selenium ---
HEADLESS = os.getenv("HEADLESS", "True") == "True"

# --- Constantes do dominio ---
FONTES_SUPORTADAS = ["olx", "marketplace"]
