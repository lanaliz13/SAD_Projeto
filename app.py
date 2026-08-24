import os
import html
import textwrap

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.data_loader import carregar_dados, obter_coluna


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Duolingo Learning Insights",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def render_html(content):
    conteudo = textwrap.dedent(str(content)).strip()

    if hasattr(st, "html"):
        st.html(conteudo)
    else:
        st.markdown(conteudo, unsafe_allow_html=True)


def carregar_css():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base_dir, "assets", "style.css")

    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as arquivo:
            css = arquivo.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )


def percentual(valor):
    if pd.isna(valor) or valor is None:
        return "Não disponível"

    return f"{float(valor) * 100:.1f}%"


def numero(valor):
    if pd.isna(valor) or valor is None:
        return "0"

    return f"{int(valor):,}".replace(",", ".")


def cabecalho(titulo, descricao):
    render_html(f"""
        <div class="app-header">
            <div class="app-eyebrow">
                SISTEMA DE APOIO À DECISÃO
            </div>

            <h1>{html.escape(titulo)}</h1>

            <p>{html.escape(descricao)}</p>
        </div>
    """)


def secao(titulo, descricao=""):
    render_html(f"""
        <div class="section-title">
            <h2>{html.escape(titulo)}</h2>
            <p>{html.escape(descricao)}</p>
        </div>
    """)


def caixa_metrica(titulo, valor, descricao):
    render_html(f"""
        <div class="metric-box">
            <div class="metric-label">
                {html.escape(str(titulo))}
            </div>

            <div class="metric-value">
                {html.escape(str(valor))}
            </div>

            <div class="metric-description">
                {html.escape(str(descricao))}
            </div>
        </div>
    """)


def explicacao_grafico(titulo, texto):
    render_html(f"""
        <div class="insight-card insight-purple"
             style="margin-bottom: 1.2rem;">

            <div class="insight-title">
                💡 Como interpretar este gráfico
                ({html.escape(titulo)}):
            </div>

            <div class="insight-text">
                {html.escape(texto)}
            </div>

        </div>
    """)


def filtrar_idioma(df, idioma):
    if (
        df is None
        or df.empty
        or idioma == "Todos"
        or "idioma" not in df.columns
    ):
        return df.copy() if df is not None else pd.DataFrame()

    resultado = df[
        df["idioma"]
        .astype(str)
        .str.lower()
        == str(idioma).lower()
    ].copy()

    return resultado


def obter_idiomas(*dataframes):
    idiomas = set()

    for df in dataframes:

        if (
            df is not None
            and not df.empty
            and "idioma" in df.columns
        ):

            valores = (
                df["idioma"]
                .dropna()
                .astype(str)
                .unique()
            )

            for valor in valores:

                if valor.lower() not in [
                    "all",
                    "all languages",
                    "todos",
                    "nan"
                ]:
                    idiomas.add(valor)

    return sorted(list(idiomas))


def obter_nome_palavra(df):
    return obter_coluna(
        df,
        [
            "surface_form",
            "lemma",
            "word"
        ]
    )


def obter_recall_col(df):
    return obter_coluna(
        df,
        [
            "item_recall_rate",
            "avg_session_recall",
            "avg_recall",
            "recall"
        ]
    )


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

carregar_css()

dados = carregar_dados()

traces = dados["traces"]
courses = dados["courses"]
curve = dados["curve"]
words = dados["words"]

idiomas = obter_idiomas(
    traces,
    courses,
    curve,
    words
)


# ============================================================
# MENU LATERAL
# ============================================================

with st.sidebar:

    render_html("""
        <div class="sidebar-brand">

            <div class="sidebar-title">
                Duolingo Insights
            </div>

            <div class="sidebar-subtitle">
                Painel Decision Support System
            </div>

        </div>
    """)

    pagina = st.radio(
        "Navegação",
        [
            "Visão Geral",
            "Consulta de Pesquisa",
            "Análise por Idioma"
        ]
    )

    st.divider()

    st.caption("Parâmetros Globais")

    meta_recall = (
        st.slider(
            "Meta de recall",
            50,
            100,
            85
        ) / 100
    )

    quantidade_prioridades = st.slider(
        "Qtd. de itens exibidos",
        5,
        30,
        10
    )

    st.divider()

    st.caption(
        "Equipe: Ana Leticia · Denise Matos · Lana Liz"
    )


# ============================================================
# VISÃO GERAL
# ============================================================

if pagina == "Visão Geral":

    cabecalho(
        "Duolingo Learning Insights",
        "Painel analítico para tomada de decisão no aprendizado de idiomas."
    )

    # --------------------------------------------------------
    # CÁLCULO DAS MÉTRICAS
    # --------------------------------------------------------

    if (
        not courses.empty
        and "n_users" in courses.columns
    ):
        total_usuarios = courses["n_users"].sum()

    elif (
        not traces.empty
        and "user_id" in traces.columns
    ):
        total_usuarios = traces["user_id"].nunique()

    else:
        total_usuarios = 0


    if (
        not courses.empty
        and "n_traces" in courses.columns
    ):
        total_interacoes = courses["n_traces"].sum()

    else:
        total_interacoes = len(traces)


    recall_col = (
        obter_recall_col(courses)
        or obter_recall_col(traces)
    )


    if (
        recall_col
        and not courses.empty
    ):
        recall_medio = courses[recall_col].mean()

    else:
        recall_medio = np.nan


    # --------------------------------------------------------
    # CARDS DE MÉTRICAS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        caixa_metrica(
            "Total de usuários",
            numero(total_usuarios),
            "Usuários na base"
        )

    with c2:
        caixa_metrica(
            "Total de interações",
            numero(total_interacoes),
            "Registros de treino"
        )

    with c3:
        caixa_metrica(
            "Recall médio",
            percentual(recall_medio),
            "Retenção geral"
        )

    with c4:
        caixa_metrica(
            "Idiomas",
            str(len(idiomas)),
            "Idiomas analisados"
        )


    # --------------------------------------------------------
    # GRÁFICO DE RETENÇÃO
    # --------------------------------------------------------

    secao(
        "Distribuição de Retenção na Base"
    )

    explicacao_grafico(
        "Histograma de Recall",
        "Este gráfico mostra a quantidade de sessões "
        "divididas por sua taxa de acerto. Quanto mais "
        "barras concentradas à direita, próximas de 100%, "
        "melhor está a retenção geral dos alunos."
    )


    if not curve.empty:

        r_col = obter_recall_col(curve)

        if r_col:

            fig_overview = px.histogram(
                curve,
                x=r_col,
                nbins=20,
                title="Distribuição da Taxa de Recall (Retenção)",
                color_discrete_sequence=["#8b5cf6"],
                template="plotly_dark"
            )

            fig_overview.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Taxa de Retenção (0% a 100%)",
                yaxis_title="Frequência na Base",
                xaxis_tickformat=".0%"
            )

            st.plotly_chart(
                fig_overview,
                width="stretch"
            )


# ============================================================
# CONSULTA DE PESQUISA
# ============================================================

elif pagina == "Consulta de Pesquisa":

    cabecalho(
        "Consulta de Pesquisa",
        "Respostas visuais e diretas para as perguntas de negócio do sistema."
    )


    # --------------------------------------------------------
    # SELEÇÃO DA PERGUNTA
    # --------------------------------------------------------

    pergunta = st.selectbox(
        "Selecione a Pergunta Analítica",
        [
            "Como o tempo sem prática afeta a retenção?",
            "Mais revisões melhoram o recall?",
            "Quais palavras são mais difíceis de aprender?",
            "Quais classes gramaticais geram mais erros?"
        ]
    )


    idioma = st.selectbox(
        "Idioma",
        ["Todos"] + idiomas
    )


    # ========================================================
    # PERGUNTA 1
    # ========================================================

    if pergunta == "Como o tempo sem prática afeta a retenção?":

        explicacao_grafico(
            "Tempo sem Prática vs. Retenção",
            "A linha mostra como o recall, ou seja, os acertos, "
            "varia à medida que os dias passam sem revisão. "
            "A linha tracejada representa a meta do sistema. "
            "Quando a retenção fica abaixo da meta, o conteúdo "
            "pode precisar de revisão."
        )


        if idioma != "Todos":
            df = filtrar_idioma(
                curve,
                idioma
            )
        else:
            df = curve


        lag_col = obter_coluna(
            df,
            [
                "lag_bin",
                "lag_days",
                "avg_lag_days"
            ]
        )

        recall_col = obter_recall_col(df)


        if (
            not df.empty
            and lag_col
            and recall_col
        ):

            ordem_lag = [
                "<1 hour",
                "1-6 hours",
                "6-24 hours",
                "1-3 days",
                "3-7 days",
                "1-2 weeks",
                "2-4 weeks",
                "1-3 months",
                "3+ months"
            ]


            df[lag_col] = pd.Categorical(
                df[lag_col],
                categories=ordem_lag,
                ordered=True
            )


            res = (
                df
                .groupby(
                    lag_col,
                    as_index=False,
                    observed=False
                )[recall_col]
                .mean()
            )


            fig = px.line(
                res,
                x=lag_col,
                y=recall_col,
                markers=True,
                title=(
                    "Curva de Retenção pelo Tempo "
                    f"sem Prática — {idioma}"
                ),
                color_discrete_sequence=["#fb7185"],
                template="plotly_dark"
            )


            fig.add_hline(
                y=meta_recall,
                line_dash="dash",
                line_color="#34d399",
                annotation_text="Meta Global"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis_tickformat=".0%",
                yaxis_title="Taxa de Acerto",
                xaxis_title="Intervalo Sem Prática"
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.warning(
                "Dados não encontrados para o filtro selecionado."
            )


    # ========================================================
    # PERGUNTA 2
    # ========================================================

    elif pergunta == "Mais revisões melhoram o recall?":

        explicacao_grafico(
            "Quantidade de Revisões vs. Acertos",
            "Cada barra representa um nível de repetição. "
            "Barras mais altas indicam uma maior taxa de "
            "acerto conforme aumentam as exposições anteriores."
        )


        if idioma != "Todos":
            df = filtrar_idioma(
                curve,
                idioma
            )
        else:
            df = curve


        exp_col = obter_coluna(
            df,
            [
                "practice_bin",
                "avg_prior_exposures",
                "prior_exposures"
            ]
        )

        recall_col = obter_recall_col(df)


        if (
            not df.empty
            and exp_col
            and recall_col
        ):

            ordem_exposicoes = [
                "1-2 exposures",
                "3-4 exposures",
                "5-9 exposures",
                "10-19 exposures",
                "20+ exposures"
            ]


            df[exp_col] = pd.Categorical(
                df[exp_col],
                categories=ordem_exposicoes,
                ordered=True
            )


            res = (
                df
                .groupby(
                    exp_col,
                    as_index=False,
                    observed=False
                )[recall_col]
                .mean()
            )


            fig = px.bar(
                res,
                x=exp_col,
                y=recall_col,
                text_auto=".1%",
                title=(
                    "Impacto das Exposições Anteriores "
                    f"no Recall — {idioma}"
                ),
                color_discrete_sequence=["#60a5fa"],
                template="plotly_dark"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis_tickformat=".0%",
                yaxis_title="Taxa de Acerto",
                xaxis_title="Número de Revisões Anteriores"
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.warning(
                "Dados não encontrados para o filtro selecionado."
            )


    # ========================================================
    # PERGUNTA 3
    # ========================================================

    elif pergunta == "Quais palavras são mais difíceis de aprender?":

        explicacao_grafico(
            "Top Palavras com Menor Retenção",
            "As palavras apresentadas possuem as menores "
            "taxas de acerto na base de dados. Elas representam "
            "o vocabulário que apresenta maior dificuldade "
            "e pode exigir maior reforço."
        )


        if idioma != "Todos":
            df = filtrar_idioma(
                words,
                idioma
            )
        else:
            df = words


        palavra_col = obter_nome_palavra(df)
        recall_col = obter_recall_col(df)


        if (
            not df.empty
            and palavra_col
            and recall_col
        ):

            res = (
                df
                .sort_values(recall_col)
                .head(quantidade_prioridades)
            )


            fig = px.bar(
                res,
                x=recall_col,
                y=palavra_col,
                orientation="h",
                text_auto=".1%",
                title=(
                    f"Top {len(res)} Palavras Mais "
                    f"Difíceis — {idioma}"
                ),
                color=recall_col,
                color_continuous_scale="Reds_r",
                template="plotly_dark"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickformat=".0%",
                xaxis_title=(
                    "Taxa de Acerto "
                    "(Menor = Mais Difícil)"
                ),
                yaxis_title="Palavra",
                yaxis={
                    "categoryorder": "total descending"
                }
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.warning(
                "Dados não encontrados para o filtro selecionado."
            )


    # ========================================================
    # PERGUNTA 4
    # ========================================================

    elif pergunta == "Quais classes gramaticais geram mais erros?":

        explicacao_grafico(
            "Distribuição de Erro por Gramática",
            "Este gráfico mostra a proporção de erros "
            "por categoria gramatical, como verbos, "
            "substantivos e adjetivos. A maior fatia "
            "representa a categoria com maior concentração "
            "de erros."
        )


        if idioma != "Todos":
            df = filtrar_idioma(
                words,
                idioma
            )
        else:
            df = words


        recall_col = obter_recall_col(df)


        if (
            not df.empty
            and "classe_gramatical" in df.columns
            and recall_col
        ):

            res = (
                df
                .groupby(
                    "classe_gramatical",
                    as_index=False
                )[recall_col]
                .mean()
            )


            res["taxa_erro"] = (
                1 - res[recall_col]
            )


            res = res.sort_values(
                "taxa_erro",
                ascending=False
            )


            fig = px.pie(
                res,
                names="classe_gramatical",
                values="taxa_erro",
                title=(
                    "Concentração de Erros por "
                    f"Categoria Gramatical — {idioma}"
                ),
                hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=(
                    px.colors.qualitative.Pastel
                )
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.warning(
                "Dados não encontrados para o filtro selecionado."
            )


# ============================================================
# ANÁLISE POR IDIOMA
# ============================================================

elif pagina == "Análise por Idioma":

    cabecalho(
        "Análise por Idioma",
        "Desempenho comparativo e detalhado do idioma selecionado."
    )


    idioma = st.selectbox(
        "Idioma",
        idiomas if idiomas else ["German"]
    )


    # --------------------------------------------------------
    # FILTRO DOS DADOS
    # --------------------------------------------------------

    c_df = filtrar_idioma(
        courses,
        idioma
    )

    w_df = filtrar_idioma(
        words,
        idioma
    )


    # --------------------------------------------------------
    # RECALL DO IDIOMA
    # --------------------------------------------------------

    r_col = (
        obter_recall_col(c_df)
        or obter_recall_col(w_df)
    )


    if (
        not c_df.empty
        and r_col
    ):

        recall_id = c_df[r_col].mean()

    elif (
        not w_df.empty
        and r_col
    ):

        recall_id = w_df[r_col].mean()

    else:

        recall_id = np.nan


    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    c1, c2 = st.columns(2)


    with c1:

        caixa_metrica(
            f"Recall em {idioma}",
            percentual(recall_id),
            "Média calculada"
        )


    with c2:

        caixa_metrica(
            "Meta Estabelecida",
            percentual(meta_recall),
            "Parâmetro global"
        )


    # --------------------------------------------------------
    # VOCABULÁRIO CRÍTICO
    # --------------------------------------------------------

    if not w_df.empty:

        p_col = obter_nome_palavra(w_df)
        r_col = obter_recall_col(w_df)


        if p_col and r_col:

            secao(
                "Vocabulário Mais Crítico no Idioma"
            )


            top_crit = (
                w_df
                .sort_values(r_col)
                .head(quantidade_prioridades)
            )


            fig = px.bar(
                top_crit,
                x=r_col,
                y=p_col,
                orientation="h",
                color=r_col,
                text_auto=".1%",
                color_continuous_scale="Purples_r",
                template="plotly_dark",
                title=(
                    f"Top {len(top_crit)} Palavras "
                    f"com Menor Retenção em {idioma}"
                )
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickformat=".0%",
                xaxis_title="Taxa de Retenção",
                yaxis_title="Palavra",
                yaxis={
                    "categoryorder": "total descending"
                }
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Dados de palavras indisponíveis "
                "para o idioma selecionado."
            )

    else:

        st.info(
            "Não existem dados de vocabulário "
            "para o idioma selecionado."
        )


# ============================================================
# RODAPÉ
# ============================================================

render_html("""
    <div class="footer">
        Duolingo Learning Insights — Sistema de Apoio à Decisão<br>
        Ana Leticia · Denise Matos · Lana Liz
    </div>
""")