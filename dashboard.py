"""Dashboard do laboratório: testes de hipótese por dentro (t de Welch x Mann-Whitney).

Uso: streamlit run dashboard.py

Mostra os dados gerados por código do repositório: os dados reais (scripts/coletar_prs.py) e os
simulados (scripts/gerar_dados_simulados.py, via python main.py). As seções seguem a ordem da seção 4
do enunciado. G1 está pronto; G2 a G4 entram nas Issues seguintes, usando as cores definidas aqui.
"""
import csv
import os
import sys
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import aplicar_testes  # noqa: E402

DADOS_REAIS = os.path.join(RAIZ, "dados", "tempo-ate-merge-langflow.csv")
DADOS_SIMULADOS = os.path.join(RAIZ, "dados", "tempo-ate-merge-simulado.csv")

# Cenário simulado mostrado ao lado dos dados reais: é o que reproduz a diferença observada neles.
CENARIO_REAL = "diferenca_real"

LINK_REPOSITORIO = "https://github.com/Paulooassis/Laboratorio-04-medicao-de-software"
LINK_PROJECTS = "https://github.com/users/Paulooassis/projects/4"
# Preencher com o endereço público quando o dashboard for publicado (ex.: Streamlit Community Cloud).
LINK_DASHBOARD = ""

# Cores fixas: cada teste e cada grupo tem sempre a mesma cor em todos os gráficos.
# Pares validados para daltonismo (diferença perceptual ΔE > 24) e contraste >= 3:1 no fundo claro.
CORES_TESTES = {"t de Welch": "#2a78d6", "Mann-Whitney": "#eb6834"}
CORES_GRUPOS = {"sem_bot": "#008300", "com_bot": "#6250d6"}
NOMES_GRUPOS = {"sem_bot": "Sem bot", "com_bot": "Com bot"}


@st.cache_data
def carregar_dados_reais():
    """Tempo até o merge (h) de cada PR real, por grupo, a partir dos horários exatos."""
    formato = "%Y-%m-%dT%H:%M:%SZ"
    grupos = {}
    with open(DADOS_REAIS, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            delta = datetime.strptime(linha["mergeado_em"], formato) - datetime.strptime(linha["criado_em"], formato)
            grupos.setdefault(linha["grupo"], []).append(delta.total_seconds() / 3600)
    return {grupo: np.array(x) for grupo, x in grupos.items()}


@st.cache_data
def carregar_dados_simulados():
    """Tempo até o merge (h) por cenário e grupo, do CSV gerado com semente fixa (42)."""
    return aplicar_testes.ler_dados(DADOS_SIMULADOS)


def grafico_g1(reais, simulados, bins_por_decada=4):
    """G1: um histograma por grupo, com os dados reais ao lado dos simulados, nos mesmos bins.

    O tempo até o merge vai de segundos a semanas, então os bins têm largura constante em décadas e
    o eixo é desenhado em log10 das horas: em escala linear quase todo PR cairia na primeira barra.
    """
    valores = [x for dados in (reais, simulados) for x in dados.values()]
    inicio = np.floor(np.log10(min(x.min() for x in valores)))
    fim = np.ceil(np.log10(max(x.max() for x in valores)))
    arestas = np.linspace(inicio, fim, int((fim - inicio) * bins_por_decada) + 1)
    centros = (arestas[:-1] + arestas[1:]) / 2
    faixas = np.stack([10 ** arestas[:-1], 10 ** arestas[1:]], axis=1)  # o hover mostra horas

    paineis = (
        (1, reais, f"Dados reais: {sum(len(x) for x in reais.values())} PRs do langflow"),
        (2, simulados, "Dados simulados: Weibull, cenário com diferença real"),
    )
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
                        subplot_titles=[titulo for _, _, titulo in paineis])
    for coluna, dados, _ in paineis:
        for grupo in NOMES_GRUPOS:
            contagem, _ = np.histogram(np.log10(dados[grupo]), bins=arestas)
            fig.add_trace(
                go.Bar(
                    x=centros, y=contagem, width=0.45 / bins_por_decada, customdata=faixas,
                    name=NOMES_GRUPOS[grupo], legendgroup=grupo, showlegend=coluna == 1,
                    marker_color=CORES_GRUPOS[grupo],
                    hovertemplate="%{y} PRs entre %{customdata[0]:.2f} h e %{customdata[1]:.2f} h"
                                  "<extra>%{fullData.name}</extra>",
                ),
                row=1, col=coluna,
            )
    decadas = np.arange(inicio, fim + 1)
    fig.update_layout(
        title=f"G1 — Tempo até o merge dos Pull Requests ({bins_por_decada} bins por década)",
        barmode="group", bargap=0.25, height=430, legend_title_text="Grupo", margin={"t": 90},
    )
    fig.update_xaxes(
        title_text="Tempo até o merge (horas, escala logarítmica)", range=[inicio, fim],
        tickmode="array", tickvals=decadas,
        ticktext=[f"{10.0 ** d:g}".replace(".", ",") for d in decadas],
    )
    fig.update_yaxes(title_text="Número de PRs", row=1, col=1)
    return fig


def em_construcao(conteudo, onde):
    st.info(f"{conteudo}: em construção ({onde}).", icon=":material/construction:")


def cabecalho():
    st.title("Testes de hipótese por dentro")
    st.markdown("**t de Welch x Mann-Whitney** no tempo até o merge de Pull Requests, com e sem bot de revisão.")
    link_dashboard = (f"[Dashboard]({LINK_DASHBOARD})" if LINK_DASHBOARD
                      else "Dashboard: ainda não publicado; abra localmente com `streamlit run dashboard.py`")
    st.markdown(f"{link_dashboard} · [Repositório]({LINK_REPOSITORIO}) · [GitHub Projects]({LINK_PROJECTS})")


def secao_cenario():
    reais = carregar_dados_reais()
    n_sem, n_com = len(reais["sem_bot"]), len(reais["com_bot"])

    st.header("1. Cenário")
    st.markdown("**Pergunta:** a adoção do bot de revisão CodeRabbit mudou o tempo até o merge dos Pull Requests "
                "do [langflow](https://github.com/langflow-ai/langflow)?")
    st.markdown("Os testes são **bilaterais**, com **α = 0,05**: a pergunta é se o tempo mudou, em qualquer direção.")
    st.markdown(
        "| Teste | H₀ | H₁ |\n"
        "|---|---|---|\n"
        "| t de Welch | As médias do tempo até o merge são iguais: μ<sub>sem bot</sub> = μ<sub>com bot</sub> "
        "| As médias são diferentes: μ<sub>sem bot</sub> ≠ μ<sub>com bot</sub> |\n"
        "| Mann-Whitney | Um PR sorteado de cada grupo tem a mesma chance de ser o mais rápido: "
        "P(X<sub>sem bot</sub> < X<sub>com bot</sub>) = 0,5 "
        "| Um grupo tende a ter tempos maiores: P(X<sub>sem bot</sub> < X<sub>com bot</sub>) ≠ 0,5 |",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Dados reais:** {n_sem + n_com} PRs mergeados do langflow, coletados pela API de busca do GitHub: "
        f"**{n_sem} sem bot**, os últimos criados antes da adoção do CodeRabbit (29/05/2025), e "
        f"**{n_com} com bot**, os primeiros criados depois dela e revisados pelo bot. A variável é o tempo entre "
        "a abertura e o merge do PR, em horas. Detalhes em "
        f"[coleta-dos-dados.md]({LINK_REPOSITORIO}/blob/main/docs/coleta-dos-dados.md)."
    )


def secao_dados():
    reais = carregar_dados_reais()
    simulados = carregar_dados_simulados()[CENARIO_REAL]

    st.header("2. Os dados")
    st.plotly_chart(grafico_g1(reais, simulados))
    st.markdown(
        "**O que o gráfico mostra.** Com o eixo em escala logarítmica, os quatro histogramas têm o mesmo "
        "formato: a maior parte dos PRs é mergeada em poucas horas e uma cauda se estende até centenas de "
        "horas. Nas duas fontes, o grupo **com bot** está deslocado para a direita, ou seja, concentra os "
        "PRs mais demorados, que é a diferença que a simulação precisa reproduzir.\n\n"
        "**O que concluímos.** A Weibull ajustada reproduz a posição e a cauda dos dados reais e serve como "
        "substituta deles nas simulações das próximas seções; a diferença que sobra é que os dados reais "
        "têm alguns PRs mergeados em segundos, que a Weibull não gera. Esse formato, bem assimétrico mesmo "
        "com n = 30 por grupo, é justamente o caso em que o pressuposto de normalidade do t de Welch fica "
        "em dúvida — é o que as próximas seções vão testar."
    )
    st.caption(
        f"Dados reais: `dados/tempo-ate-merge-langflow.csv` (`scripts/coletar_prs.py`). Simulados: "
        f"`dados/tempo-ate-merge-simulado.csv`, cenário `{CENARIO_REAL}` com n = "
        f"{len(simulados['sem_bot'])} por grupo e semente fixa (`scripts/gerar_dados_simulados.py`)."
    )


def secao_testes():
    st.header("3. Como os testes funcionam")
    em_construcao("G2, distribuição da estatística sob H₀", "Issue #8")


def secao_erro_tipo_i():
    st.header("4. Erro tipo I")
    em_construcao("G3, erro tipo I dos dois testes em cada situação", "Lab04S02")


def secao_poder():
    st.header("5. Poder")
    em_construcao("G4, curvas de poder dos dois testes", "Lab04S02")


def secao_dados_reais():
    st.header("6. Dados reais")
    em_construcao("Tabela com os testes aplicados aos dados reais", "Entrega Final")


def secao_conclusao():
    st.header("7. Conclusão")
    em_construcao("O que o grupo esperava × o que encontrou, e a recomendação", "Entrega Final")


def main():
    st.set_page_config(page_title="Testes de hipótese por dentro", page_icon=":material/analytics:", layout="wide")
    cabecalho()
    secao_cenario()
    secao_dados()
    secao_testes()
    secao_erro_tipo_i()
    secao_poder()
    secao_dados_reais()
    secao_conclusao()


main()
