"""
Script de teste da Fase 1 do roadmap: valida que o Python consegue
conversar com o MySQL de ponta a ponta.

O que ele faz:
1. Testa a conexao pura (sem tocar em nenhuma tabela)
2. Busca a fonte "OLX" (ja inserida pelo schema.sql)
3. Insere um anuncio de teste vinculado a essa fonte
4. Insere um registro de historico de preco vinculado a esse anuncio
5. Le tudo de volta e imprime, usando pandas (igual sera usado no ETL)
6. Remove o anuncio de teste no final, para nao sujar o banco

Como rodar (na raiz do projeto, com o venv ativado):
    python scripts/testar_conexao_db.py
"""

import sys
import os

# Garante que a raiz do projeto esta no path, para os imports funcionarem
# quando o script e rodado de dentro da pasta scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.database.connection import testar_conexao, get_session
from src.database.models import Fonte, Anuncio, HistoricoPreco


def main():
    print("1. Testando conexao pura com o MySQL...")
    if not testar_conexao():
        print("Parando aqui - verifique o .env e se o MySQL Server esta rodando.")
        return
    print("   OK - conexao estabelecida.\n")

    print("2. Buscando a fonte 'OLX' (inserida pelo schema.sql)...")
    with get_session() as session:
        fonte_olx = session.query(Fonte).filter_by(nome="OLX").first()

        if not fonte_olx:
            print("   ERRO: fonte 'OLX' nao encontrada. O schema.sql foi executado?")
            return
        print(f"   OK - encontrada: {fonte_olx} (id={fonte_olx.id})\n")

        print("3. Inserindo anuncio de teste...")
        anuncio_teste = Anuncio(
            fonte_id=fonte_olx.id,
            id_externo="teste-000001",
            titulo="[TESTE] Honda Civic EXL 2020",
            url="https://www.olx.com.br/exemplo-teste",
            marca="Honda",
            modelo="Civic",
            ano=2020,
            km=45000,
            preco=68500.00,
            cidade="Recife",
            estado="PE",
            vendedor_tipo="particular",
        )
        session.add(anuncio_teste)
        session.flush()  # envia para o banco e preenche o anuncio_teste.id, sem commitar ainda
        print(f"   OK - anuncio criado com id={anuncio_teste.id}\n")

        print("4. Inserindo um registro de historico de preco...")
        historico = HistoricoPreco(anuncio_id=anuncio_teste.id, preco=68500.00)
        session.add(historico)
        session.flush()
        print(f"   OK - historico criado com id={historico.id}\n")

        anuncio_id_criado = anuncio_teste.id
        # o "with get_session()" da commit automatico ao sair do bloco sem erro

    print("5. Lendo os dados de volta com pandas...")
    with get_session() as session:
        anuncios = session.query(Anuncio).filter_by(id_externo="teste-000001").all()

        dados = [
            {
                "id": a.id,
                "titulo": a.titulo,
                "marca": a.marca,
                "modelo": a.modelo,
                "preco": float(a.preco),
                "fonte": a.fonte.nome,  # acessa a fonte relacionada via relationship
            }
            for a in anuncios
        ]
        df = pd.DataFrame(dados)
        print(df, "\n")

    print("6. Limpando o anuncio de teste (cascade remove o historico junto)...")
    with get_session() as session:
        anuncio = session.query(Anuncio).filter_by(id=anuncio_id_criado).first()
        if anuncio:
            session.delete(anuncio)
    print("   OK - dados de teste removidos.\n")

    print("Fase 1 validada: Python conecta, insere, le e remove dados do MySQL com sucesso.")


if __name__ == "__main__":
    main()
