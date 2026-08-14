"""
Definicao das tabelas do banco como classes Python (SQLAlchemy ORM),
espelhando exatamente o sql/schema.sql (4 tabelas: fontes, anuncios,
historico_precos, imagens).

Isso permite trabalhar com o banco usando objetos Python em vez de
escrever SQL na mao toda hora. Exemplo:

    novo_anuncio = Anuncio(titulo="Civic 2020", preco=65000, fonte_id=1, ...)
    session.add(novo_anuncio)
    session.commit()

em vez de escrever manualmente:

    INSERT INTO anuncios (titulo, preco, fonte_id, ...) VALUES (...)

Importante: este arquivo so DEFINE a estrutura em Python. As tabelas
de verdade ja foram criadas no MySQL pelo schema.sql - nao usamos
Base.metadata.create_all() aqui para evitar ter duas fontes de verdade
divergentes (SQL manual vs SQLAlchemy). O schema.sql continua sendo
a fonte oficial da estrutura do banco.
"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, SmallInteger, DECIMAL, Boolean,
    TIMESTAMP, Enum, ForeignKey, CHAR
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Fonte(Base):
    __tablename__ = "fontes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False, unique=True)
    url_base = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(TIMESTAMP, default=datetime.utcnow)

    # relationship() nao cria coluna nenhuma - e so um "atalho" Python
    # para acessar os anuncios relacionados, tipo: minha_fonte.anuncios
    anuncios = relationship("Anuncio", back_populates="fonte")

    def __repr__(self):
        return f"<Fonte {self.nome}>"


class Anuncio(Base):
    __tablename__ = "anuncios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fonte_id = Column(Integer, ForeignKey("fontes.id"), nullable=False)
    id_externo = Column(String(100), nullable=False)
    titulo = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)

    marca = Column(String(50))
    modelo = Column(String(100))
    ano = Column(SmallInteger)
    km = Column(Integer)
    preco = Column(DECIMAL(10, 2))

    cidade = Column(String(100))
    estado = Column(CHAR(2))

    vendedor_tipo = Column(
        Enum("particular", "loja", "desconhecido", name="vendedor_tipo_enum"),
        default="desconhecido",
    )
    ativo = Column(Boolean, default=True, nullable=False)

    telefone = Column(String(20))
    whatsapp = Column(String(20))
    whatsapp_link = Column(String(255))

    data_captura = Column(TIMESTAMP, default=datetime.utcnow)
    atualizado_em = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    fonte = relationship("Fonte", back_populates="anuncios")
    historico_precos = relationship(
        "HistoricoPreco", back_populates="anuncio", cascade="all, delete-orphan"
    )
    imagens = relationship(
        "Imagem", back_populates="anuncio", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Anuncio {self.titulo} - R${self.preco}>"


class HistoricoPreco(Base):
    __tablename__ = "historico_precos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anuncio_id = Column(Integer, ForeignKey("anuncios.id", ondelete="CASCADE"), nullable=False)
    preco = Column(DECIMAL(10, 2), nullable=False)
    data_registro = Column(TIMESTAMP, default=datetime.utcnow)

    anuncio = relationship("Anuncio", back_populates="historico_precos")

    def __repr__(self):
        return f"<HistoricoPreco anuncio_id={self.anuncio_id} R${self.preco}>"


class Imagem(Base):
    __tablename__ = "imagens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anuncio_id = Column(Integer, ForeignKey("anuncios.id", ondelete="CASCADE"), nullable=False)
    url_imagem = Column(String(500), nullable=False)
    ordem = Column(SmallInteger, default=0)

    anuncio = relationship("Anuncio", back_populates="imagens")

    def __repr__(self):
        return f"<Imagem anuncio_id={self.anuncio_id}>"
