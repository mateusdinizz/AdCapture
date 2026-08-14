"""
Cria a "engine" de conexao com o MySQL via SQLAlchemy, usando as
configuracoes definidas em config/settings.py (que por sua vez le do .env).

A "engine" e o objeto que sabe COMO conectar no banco (host, usuario,
senha, etc). A partir dela, criamos "sessions" - que sao usadas para
efetivamente executar operacoes (insert, select, update, delete).

Uso tipico em outro arquivo:

    from src.database.connection import SessionLocal

    session = SessionLocal()
    # ... usar a session ...
    session.close()

Ou, de forma mais segura (fecha automaticamente mesmo se der erro):

    from src.database.connection import get_session

    with get_session() as session:
        # ... usar a session ...
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# String de conexao no formato que o SQLAlchemy espera:
# dialeto+driver://usuario:senha@host:porta/nome_do_banco
DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# echo=False evita que o SQLAlchemy imprima todo SQL executado no terminal.
# Mude para True temporariamente se precisar debugar uma query.
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# SessionLocal e uma "fabrica" de sessions - cada chamada gera uma nova.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session():
    """
    Context manager que abre uma session, entrega para o bloco 'with',
    e garante o fechamento no final - mesmo se ocorrer uma excecao.
    Tambem faz rollback automatico em caso de erro, evitando deixar
    a transacao "pendurada" no banco.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def testar_conexao() -> bool:
    """
    Faz uma tentativa simples de conexao com o banco, so para validar
    que as credenciais e o servidor estao acessiveis. Retorna True/False.
    """
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception as e:
        print(f"Falha ao conectar no banco: {e}")
        return False


if __name__ == "__main__":
    # Permite rodar "python -m src.database.connection" para um teste rapido
    if testar_conexao():
        print("Conexao com o MySQL bem-sucedida.")
    else:
        print("Nao foi possivel conectar ao MySQL. Verifique o .env e o servidor.")
