"""
Aplicacao Flask — Fases 6-8 do roadmap.

Fase 6: tela de Anuncios + Filtros
Fase 7: Dashboard
Fase 8: Favoritos (sem login/usuarios)

Como rodar:
    python app.py

Depois abra http://127.0.0.1:5000 no navegador.
"""

from datetime import date

from flask import Flask, render_template, request, jsonify
from sqlalchemy import func, desc

from src.database.connection import get_session
from src.database.models import Anuncio, Favorito

app = Flask(__name__)

KM_MAX_SLIDER = 300000  # quando o slider estiver nesse valor, tratamos como "sem limite"


@app.context_processor
def injetar_estatisticas():
    """
    Deixa as estatisticas do cabecalho (total capturado, novos hoje,
    preco medio, total de favoritos) disponiveis automaticamente em
    QUALQUER template, sem precisar passar isso manualmente em cada
    rota nova que a interface for ganhando.
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

        total_favoritos = session.query(Favorito).count()

    return {
        "stat_total_geral": total_geral,
        "stat_novos_hoje": novos_hoje,
        "stat_preco_medio": float(preco_medio) if preco_medio else None,
        "stat_total_favoritos": total_favoritos,
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

        # IDs dos anuncios favoritados, para saber quais coracoes
        # devem aparecer preenchidos na tela
        ids_favoritados = {
            f.anuncio_id
            for f in session.query(Favorito.anuncio_id).all()
        }

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
                "favoritado": a.id in ids_favoritados,
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
    Score de oportunidades (Fase 11) exista.
    Fase 8 adiciona o cartao de Favoritos de volta com dados reais.
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


# -----------------------------------------------------------------
# Fase 8: Favoritos
# -----------------------------------------------------------------

@app.route("/api/favoritos/<int:anuncio_id>", methods=["POST"])
def favoritar(anuncio_id):
    """
    Adiciona um anuncio aos favoritos. Chamado via fetch() do JS no card.
    Retorna JSON com o estado atualizado.
    """
    with get_session() as session:
        # Verificar se o anuncio existe
        anuncio = session.query(Anuncio).filter(Anuncio.id == anuncio_id).first()
        if not anuncio:
            return jsonify({"erro": "Anúncio não encontrado"}), 404

        existe = (
            session.query(Favorito)
            .filter(Favorito.anuncio_id == anuncio_id)
            .first()
        )
        if existe:
            return jsonify({"favoritado": True, "msg": "Já está nos favoritos"})

        session.add(Favorito(anuncio_id=anuncio_id))
        # commit acontece automaticamente no get_session context manager

    return jsonify({"favoritado": True, "msg": "Adicionado aos favoritos"})


@app.route("/api/favoritos/<int:anuncio_id>", methods=["DELETE"])
def desfavoritar(anuncio_id):
    """
    Remove um anuncio dos favoritos. Chamado via fetch() do JS no card.
    """
    with get_session() as session:
        fav = (
            session.query(Favorito)
            .filter(Favorito.anuncio_id == anuncio_id)
            .first()
        )
        if fav:
            session.delete(fav)

    return jsonify({"favoritado": False, "msg": "Removido dos favoritos"})


@app.route("/api/favoritos/count")
def favoritos_count():
    """Retorna apenas a contagem de favoritos (para o badge do header via JS)."""
    with get_session() as session:
        total = session.query(Favorito).count()
    return jsonify({"total": total})


@app.route("/favoritos")
def favoritos():
    """
    Fase 8: tela dedicada de favoritos — mesma aparencia dos cards de
    anuncios, filtrada apenas pelos anuncios salvos pelo usuario.
    """
    ordenar = request.args.get("ordenar", default="recentes_fav")

    with get_session() as session:
        query = (
            session.query(Anuncio)
            .join(Favorito, Favorito.anuncio_id == Anuncio.id)
            .filter(Anuncio.ativo.is_(True))
        )

        if ordenar == "preco_asc":
            query = query.order_by(Anuncio.preco.asc())
        elif ordenar == "preco_desc":
            query = query.order_by(Anuncio.preco.desc())
        elif ordenar == "km_asc":
            query = query.order_by(Anuncio.km.asc())
        elif ordenar == "ano_desc":
            query = query.order_by(Anuncio.ano.desc())
        else:  # "recentes_fav" - mais recentemente favoritado
            query = query.order_by(Favorito.data_criacao.desc())

        resultados = query.all()

        favoritos_dados = [
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
                "favoritado": True,
            }
            for a in resultados
        ]

    return render_template(
        "favoritos.html",
        anuncios=favoritos_dados,
        total_favoritos=len(favoritos_dados),
        ordenar=ordenar,
    )


if __name__ == "__main__":
    app.run(debug=True)