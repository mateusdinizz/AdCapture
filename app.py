"""
Aplicacao Flask - Fase 6 do roadmap: tela de Anuncios + Filtros.

Como rodar:
    python app.py

Depois abra http://127.0.0.1:5000 no navegador.
"""

from datetime import date

from flask import Flask, render_template, request
from sqlalchemy import func, desc

from src.database.connection import get_session
from src.database.models import Anuncio

app = Flask(__name__)

KM_MAX_SLIDER = 300000  # quando o slider estiver nesse valor, tratamos como "sem limite"


@app.context_processor
def injetar_estatisticas():
    """
    Deixa as estatisticas do cabecalho (total capturado, novos hoje,
    preco medio) disponiveis automaticamente em QUALQUER template,
    sem precisar passar isso manualmente em cada rota nova que a
    interface for ganhando (dashboard, favoritos, etc.).
    """
    with get_session() as session:
        total_geral = session.query(Anuncio).filter(Anuncio.ativo.is_(True)).count()

        novos_hoje = (
            session.query(Anuncio)
            .filter(Anuncio.ativo.is_(True))
            .filter(func.date(Anuncio.data_captura) == date.today())
            .count()
        )

        preco_medio = (
            session.query(func.avg(Anuncio.preco))
            .filter(Anuncio.ativo.is_(True), Anuncio.preco.isnot(None))
            .scalar()
        )

    return {
        "stat_total_geral": total_geral,
        "stat_novos_hoje": novos_hoje,
        "stat_preco_medio": float(preco_medio) if preco_medio else None,
    }


@app.route("/")
def anuncios():
    """
    Tela principal: lista de anuncios com filtros aplicados via query
    string (ex: ?marca=Toyota&preco_max=80000).
    """
    marca = request.args.get("marca") or None
    modelo_busca = request.args.get("modelo") or None
    cidade = request.args.get("cidade") or None
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    ano_min = request.args.get("ano_min", type=int)
    ano_max = request.args.get("ano_max", type=int)
    km_max = request.args.get("km_max", type=int)
    # Slider no maximo = "sem limite", nao aplica filtro nenhum. Isso evita
    # esconder anuncios silenciosamente so porque o slider tem um valor
    # padrao alto sendo enviado mesmo sem o usuario mexer nele.
    if km_max is not None and km_max >= KM_MAX_SLIDER:
        km_max = None
    busca = request.args.get("busca") or None
    ordenar = request.args.get("ordenar", default="recentes")

    with get_session() as session:
        query = session.query(Anuncio).filter(Anuncio.ativo.is_(True))

        if marca:
            query = query.filter(Anuncio.marca == marca)
        if modelo_busca:
            query = query.filter(Anuncio.modelo.ilike(f"%{modelo_busca}%"))
        if cidade:
            query = query.filter(Anuncio.cidade == cidade)
        if preco_min is not None:
            query = query.filter(Anuncio.preco >= preco_min)
        if preco_max is not None:
            query = query.filter(Anuncio.preco <= preco_max)
        if ano_min is not None:
            query = query.filter(Anuncio.ano >= ano_min)
        if ano_max is not None:
            query = query.filter(Anuncio.ano <= ano_max)
        if km_max is not None:
            query = query.filter(Anuncio.km <= km_max)
        if busca:
            termo = f"%{busca}%"
            query = query.filter(Anuncio.titulo.ilike(termo))

        if ordenar == "preco_asc":
            query = query.order_by(Anuncio.preco.asc())
        elif ordenar == "preco_desc":
            query = query.order_by(Anuncio.preco.desc())
        elif ordenar == "km_asc":
            query = query.order_by(Anuncio.km.asc())
        elif ordenar == "ano_desc":
            query = query.order_by(Anuncio.ano.desc())
        else:  # "recentes" - padrao
            query = query.order_by(Anuncio.data_captura.desc())

        resultados = query.limit(60).all()

        marcas_disponiveis = sorted({
            a.marca for a in session.query(Anuncio.marca).filter(Anuncio.marca.isnot(None)).distinct()
        })
        cidades_disponiveis = sorted({
            a.cidade for a in session.query(Anuncio.cidade).filter(Anuncio.cidade.isnot(None)).distinct()
        })

        total_filtrado = query.count()

        anuncios_dados = [
            {
                "id": a.id,
                "titulo": a.titulo,
                "marca": a.marca,
                "modelo": a.modelo,
                "ano": a.ano,
                "km": a.km,
                "preco": float(a.preco) if a.preco is not None else None,
                "cidade": a.cidade,
                "estado": a.estado,
                "url": a.url,
                "whatsapp_link": a.whatsapp_link,
                "fonte_nome": a.fonte.nome if a.fonte else "Desconhecida",
            }
            for a in resultados
        ]

    filtros_atuais = {
        "marca": marca or "",
        "modelo": modelo_busca or "",
        "cidade": cidade or "",
        "preco_min": request.args.get("preco_min", ""),
        "preco_max": request.args.get("preco_max", ""),
        "ano_min": request.args.get("ano_min", ""),
        "ano_max": request.args.get("ano_max", ""),
        "km_max": request.args.get("km_max", str(KM_MAX_SLIDER)),
        "busca": busca or "",
        "ordenar": ordenar,
    }

    return render_template(
        "anuncios.html",
        anuncios=anuncios_dados,
        total_filtrado=total_filtrado,
        marcas_disponiveis=marcas_disponiveis,
        cidades_disponiveis=cidades_disponiveis,
        filtros=filtros_atuais,
    )


@app.route("/dashboard")
def dashboard():
    """
    Fase 7 do roadmap: visao geral do sistema.

    Os cartoes de "Favoritos" e "Oportunidades" da visao original da
    interface foram substituidos por "Marca mais comum" e "Cidade com
    mais anuncios" - dados que ja temos de verdade hoje, ate que
    Favoritos (Fase 8) e Score de oportunidades (Fase 11) existam.
    """
    with get_session() as session:
        distribuicao_marca = (
            session.query(Anuncio.marca, func.count(Anuncio.id).label("total"))
            .filter(Anuncio.ativo.is_(True), Anuncio.marca.isnot(None))
            .group_by(Anuncio.marca)
            .order_by(desc("total"))
            .limit(8)
            .all()
        )
        marca_mais_comum = distribuicao_marca[0][0] if distribuicao_marca else None

        cidade_top = (
            session.query(Anuncio.cidade, func.count(Anuncio.id).label("total"))
            .filter(Anuncio.ativo.is_(True), Anuncio.cidade.isnot(None))
            .group_by(Anuncio.cidade)
            .order_by(desc("total"))
            .limit(1)
            .first()
        )
        cidade_mais_comum = cidade_top[0] if cidade_top else None

        ultimos = (
            session.query(Anuncio)
            .filter(Anuncio.ativo.is_(True))
            .order_by(Anuncio.data_captura.desc())
            .limit(8)
            .all()
        )

        ultimos_dados = [
            {
                "titulo": a.titulo,
                "preco": float(a.preco) if a.preco is not None else None,
                "cidade": a.cidade,
                "fonte_nome": a.fonte.nome if a.fonte else "Desconhecida",
                "url": a.url,
                "data_captura": a.data_captura,
            }
            for a in ultimos
        ]

        # Grafico de barras: percentual relativo a marca com MAIS anuncios
        # (a barra do topo sempre fica em 100%, as outras proporcionais).
        maior_total = distribuicao_marca[0][1] if distribuicao_marca else 1
        grafico_marcas = [
            {"marca": m, "total": t, "percentual": round((t / maior_total) * 100)}
            for m, t in distribuicao_marca
        ]

    return render_template(
        "dashboard.html",
        marca_mais_comum=marca_mais_comum,
        cidade_mais_comum=cidade_mais_comum,
        ultimos=ultimos_dados,
        grafico_marcas=grafico_marcas,
    )


if __name__ == "__main__":
    app.run(debug=True)