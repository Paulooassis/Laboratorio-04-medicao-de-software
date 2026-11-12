"""Dashboard do laboratório: testes de hipótese por dentro (t de Welch x Mann-Whitney).

Uso: streamlit run dashboard.py

Mostra os dados gerados por código do repositório: os dados reais (scripts/coletar_prs.py), os
simulados (scripts/gerar_dados_simulados.py) e os resultados dos testes e das simulações, todos
regenerados por python main.py. As seções seguem a ordem da seção 4 do enunciado, e cada teste e
cada grupo têm sempre a cor definida aqui.
"""
import csv
import os
import sys
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy import stats

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import aplicar_testes  # noqa: E402
import gerar_dados_simulados  # noqa: E402
from scripts.poder import REPETITIONS  # noqa: E402

DADOS_REAIS = os.path.join(RAIZ, "dados", "tempo-ate-merge-langflow.csv")
DADOS_SIMULADOS = os.path.join(RAIZ, "dados", "tempo-ate-merge-simulado.csv")
RESULTADOS_SIMULACAO = os.path.join(RAIZ, "resultados", "simulacao.csv")

# Cenário simulado usado no G1 e no exemplo do G2: é o que reproduz a diferença observada nos reais.
CENARIO_REAL = "diferenca_real"
ALFA = aplicar_testes.ALFA

LINK_REPOSITORIO = "https://github.com/Paulooassis/Laboratorio-04-medicao-de-software"
LINK_PROJECTS = "https://github.com/users/Paulooassis/projects/4"
# Preencher com o endereço público quando o dashboard for publicado (ex.: Streamlit Community Cloud).
LINK_DASHBOARD = ""

# Cores fixas: cada teste e cada grupo tem sempre a mesma cor em todos os gráficos.
# Pares validados para daltonismo (diferença perceptual ΔE > 24) e contraste >= 3:1 no fundo claro.
CORES_TESTES = {"t de Welch": "#2a78d6", "Mann-Whitney": "#eb6834"}
CORES_GRUPOS = {"sem_bot": "#008300", "com_bot": "#6250d6"}
NOMES_GRUPOS = {"sem_bot": "Sem bot", "com_bot": "Com bot"}
NOMES_SITUACOES = {"ideal": "Cenário ideal", "violada": "Cenário com outliers"}


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


@st.cache_data
def aplicar_os_testes(cenario):
    """Os dois testes aplicados ao mesmo par de amostras do cenário, por scripts/aplicar_testes.py."""
    grupos = carregar_dados_simulados()[cenario]
    sem_bot, com_bot = grupos["sem_bot"], grupos["com_bot"]
    return (aplicar_testes.teste_welch(sem_bot, com_bot),
            aplicar_testes.teste_mann_whitney(sem_bot, com_bot),
            (len(sem_bot), len(com_bot)))


def br(valor, casas=2):
    """Número com a vírgula decimal usada no resto do dashboard."""
    return f"{valor:.{casas}f}".replace(".", ",")


def rgba(cor_hex, opacidade):
    """Converte #rrggbb em rgba(), para as áreas sombreadas do G2."""
    r, g, b = (int(cor_hex[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {opacidade})"


def z_de_u(u, n_sem, n_com):
    """Padroniza U como o mannwhitneyu no p-valor assintótico, com a correção de continuidade de 0,5.

    Sem a correção, a área sombreada no G2 ficaria cerca de 1% menor que o p-valor exibido ao lado.
    """
    media = n_sem * n_com / 2
    desvio = np.sqrt(n_sem * n_com * (n_sem + n_com + 1) / 12)
    return np.sign(u - media) * max(abs(u - media) - 0.5, 0) / desvio


def caudas(x, y, corte, nome, cor, mostrar_legenda, ordem):
    """As duas caudas da densidade além de ±corte, sombreadas: os testes são bilaterais."""
    for i, mascara in enumerate((x <= -corte, x >= corte)):
        yield go.Scatter(
            x=x[mascara], y=y[mascara], fill="tozeroy", fillcolor=cor, line={"width": 0},
            name=nome, legendgroup=nome, showlegend=mostrar_legenda and i == 0,
            legendrank=ordem, hoverinfo="skip",
        )


def grafico_g2(welch, mann_whitney, n):
    """G2: a distribuição da estatística sob H0, com a região de rejeição e o p-valor de um exemplo."""
    paineis = (
        {"teste": "t de Welch", "distribuicao": stats.t(df=welch["gl"]), "simbolo": "t",
         "estatistica": welch["estatistica"], "p_valor": welch["p_valor"],
         "eixo": "Estatística t (adimensional)",
         "titulo": f"t de Welch: t de Student, {br(welch['gl'], 1)} graus de liberdade"},
        {"teste": "Mann-Whitney", "distribuicao": stats.norm(), "simbolo": "z",
         "estatistica": z_de_u(mann_whitney["estatistica"], *n), "p_valor": mann_whitney["p_valor"],
         "eixo": "Estatística U padronizada, z (adimensional)",
         "titulo": f"Mann-Whitney: normal padrão, U padronizado (n = {n[0]} + {n[1]})"},
    )
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
                        subplot_titles=[painel["titulo"] for painel in paineis])
    for coluna, painel in enumerate(paineis, start=1):
        distribuicao, cor = painel["distribuicao"], CORES_TESTES[painel["teste"]]
        critico = distribuicao.ppf(1 - ALFA / 2)
        observada = abs(painel["estatistica"])
        # os cortes entram no eixo para que as áreas fechem exatamente neles, sem degrau
        x = np.unique(np.concatenate([np.linspace(-4.2, 4.2, 600),
                                      [-critico, critico, -observada, observada]]))
        y = distribuicao.pdf(x)

        traces = [
            *caudas(x, y, observada, f"Área do p-valor ({painel['teste']})", rgba(cor, 0.45), True, 20 + coluna),
            *caudas(x, y, critico, f"Região de rejeição (α = {br(ALFA * 100, 0)}%)",
                    "rgba(80, 80, 80, 0.45)", coluna == 1, 30),
            go.Scatter(x=x, y=y, mode="lines", line={"color": cor, "width": 2.5},
                       name=f"Densidade sob H₀ ({painel['teste']})", legendrank=10 + coluna,
                       hovertemplate=f"{painel['simbolo']} = %{{x:.2f}} | densidade %{{y:.3f}}<extra></extra>"),
        ]
        for trace in traces:
            fig.add_trace(trace, row=1, col=coluna)
        fig.add_vline(
            x=painel["estatistica"], line={"color": cor, "width": 2, "dash": "dash"}, row=1, col=coluna,
            annotation={"text": f"{painel['simbolo']} = {br(painel['estatistica'])}"
                                f" | p = {br(painel['p_valor'], 3)}",
                        "font": {"color": cor}, "yshift": 2},
            annotation_position="top right",
        )
        fig.update_xaxes(title_text=painel["eixo"], range=[-4.2, 4.2], row=1, col=coluna)

    fig.update_layout(
        title="G2 — Distribuição da estatística sob H₀, região de rejeição e p-valor de um exemplo",
        height=440, margin={"t": 90}, legend={"traceorder": "normal"},
    )
    fig.update_yaxes(title_text="Densidade de probabilidade", row=1, col=1)
    return fig


@st.cache_data
def carregar_simulacao():
    """Taxa de rejeição por situação, teste e efeito, de resultados/simulacao.csv.

    Consolida resultados/erro_tipo1.csv, poder.csv e violacao.csv (scripts/consolidar_resultados.py);
    o efeito 0 de cada situação é o erro tipo I, e os demais formam a curva de poder.
    """
    with open(RESULTADOS_SIMULACAO, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    return [
        {"situacao": l["situacao"], "teste": l["teste"], "efeito": int(l["efeito"]),
         "n": int(l["n"]), "taxa_rejeicao": float(l["taxa_rejeicao"])}
        for l in linhas
    ]


def margem_simulacao(taxa, confianca=0.95):
    """Meia largura do intervalo de confiança de uma taxa estimada em REPETITIONS repetições."""
    return stats.norm.ppf(1 - (1 - confianca) / 2) * np.sqrt(taxa * (1 - taxa) / REPETITIONS)


def grafico_g3(linhas):
    """G3: a taxa de erro tipo I dos dois testes em cada situação, com a referência em α.

    Usa só o efeito 0 de resultados/simulacao.csv, em que os dois grupos vêm da mesma distribuição
    e toda rejeição é um erro tipo I. A barra de erro é a margem de 95% da própria simulação,
    ±1,96·√(p(1 − p)/repetições): cerca de ±0,4 p.p. perto de 5%.
    """
    situacoes = [s for s in NOMES_SITUACOES if any(l["situacao"] == s for l in linhas)]
    fig = go.Figure()
    for teste, cor in CORES_TESTES.items():
        taxas = {l["situacao"]: l["taxa_rejeicao"] for l in linhas if l["teste"] == teste and l["efeito"] == 0}
        margens = [margem_simulacao(taxas[s]) for s in situacoes]
        fig.add_trace(go.Bar(
            x=[NOMES_SITUACOES[s] for s in situacoes], y=[taxas[s] for s in situacoes], name=teste,
            marker_color=cor, text=[f"{taxas[s]:.1%}".replace(".", ",") for s in situacoes],
            textposition="outside", customdata=margens,
            error_y={"type": "data", "array": margens, "color": "rgba(40, 40, 40, 0.8)", "thickness": 1.5},
            hovertemplate=f"{teste}<br>%{{x}} | erro tipo I %{{y:.2%}} ± %{{customdata:.2%}}<extra></extra>",
        ))
    fig.add_hline(
        y=ALFA, line={"color": "rgba(80, 80, 80, 0.8)", "width": 2, "dash": "dash"},
        annotation={"text": f"α = {br(ALFA * 100, 0)}% (taxa esperada)",
                    "font": {"size": 11, "color": "rgba(80, 80, 80, 1)"}},
        annotation_position="top left",
    )
    fig.update_layout(
        title={"text": "G3 — Erro tipo I dos dois testes: proporção de rejeições com H₀ verdadeira",
               "subtitle": {"text": "Barras de erro: margem de 95% da simulação, ±1,96·√(p(1 − p)/"
                                    f"{REPETITIONS:_}) ≈ ±0,4 p.p.".replace("_", ".")}},
        barmode="group", bargap=0.35, height=440, margin={"t": 90}, legend_title_text="Teste",
    )
    n = linhas[0]["n"]
    fig.update_xaxes(title_text=f"Situação simulada (n = {n} por grupo, {REPETITIONS:_} repetições)".replace("_", "."))
    fig.update_yaxes(title_text="Taxa de erro tipo I (proporção de p < α)", range=[0, 0.08], tickformat=".0%")
    return fig


def grafico_g4(linhas):
    """G4: a taxa de rejeição dos dois testes por tamanho do efeito, no cenário ideal e com outliers.

    O efeito em 0 é o erro tipo I (G3): aparece aqui como o primeiro ponto de cada curva, para que a
    curva de poder comece exatamente onde o G3 termina, em vez de repetir uma simulação separada.
    """
    situacoes = [s for s in NOMES_SITUACOES if any(l["situacao"] == s for l in linhas)]
    fig = make_subplots(rows=1, cols=len(situacoes), shared_yaxes=True, horizontal_spacing=0.06,
                        subplot_titles=[NOMES_SITUACOES[s] for s in situacoes])
    for coluna, situacao in enumerate(situacoes, start=1):
        for teste, cor in CORES_TESTES.items():
            pontos = sorted((l["efeito"], l["taxa_rejeicao"]) for l in linhas
                            if l["situacao"] == situacao and l["teste"] == teste)
            efeitos, taxas = zip(*pontos)
            fig.add_trace(
                go.Scatter(
                    x=efeitos, y=taxas, mode="lines+markers", name=teste, legendgroup=teste,
                    showlegend=coluna == 1, line={"color": cor, "width": 2.5}, marker={"size": 7},
                    hovertemplate=f"{teste}<br>efeito %{{x}} h | rejeita %{{y:.1%}}<extra></extra>",
                ),
                row=1, col=coluna,
            )
        fig.add_hline(
            y=ALFA, line={"color": "rgba(80, 80, 80, 0.6)", "width": 1.5, "dash": "dash"}, row=1, col=coluna,
            annotation={"text": f"α = {br(ALFA * 100, 0)}%", "font": {"size": 11, "color": "rgba(80, 80, 80, 1)"}},
            annotation_position="bottom right",
        )
        fig.update_xaxes(title_text="Tamanho do efeito (diferença de mediana, horas)", row=1, col=coluna)

    fig.update_layout(
        title="G4 — Poder dos dois testes: proporção de rejeições × tamanho do efeito",
        height=440, margin={"t": 90}, legend_title_text="Teste",
    )
    fig.update_yaxes(title_text="Taxa de rejeição (proporção de p < α)", range=[0, 1], tickformat=".0%",
                     row=1, col=1)
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
    sem, com = gerar_dados_simulados.SEM_BOT, gerar_dados_simulados.COM_BOT
    maior = max(x.max() for x in reais.values())

    st.header("2. Os dados")
    st.plotly_chart(grafico_g1(reais, simulados))
    st.markdown(
        "**O que o gráfico mostra.** Nos dados reais e nos simulados, a maior parte dos PRs é mergeada em "
        f"poucas horas e uma cauda longa chega a centenas de horas (o maior caso real levou {br(maior, 1)} h): "
        f"a distribuição é muito assimétrica, com coeficiente de assimetria de {br(stats.skew(reais['sem_bot']))} "
        f"sem bot e {br(stats.skew(reais['com_bot']))} com bot, e o grupo **com bot** fica deslocado para "
        "a direita.\n\n"
        "**O que concluímos.** Os parâmetros da simulação vêm de um ajuste por máxima verossimilhança aos "
        "dados reais: entre Weibull, gamma e lognormal, a Weibull teve o menor AIC nos dois grupos "
        f"(sem bot: forma {br(sem['forma'])} e escala {br(sem['escala'], 1)} h; com bot: forma "
        f"{br(com['forma'])} e escala {br(com['escala'], 1)} h) e reproduz a mediana e a cauda observadas. "
        "Como as formas são quase iguais, o bot mudou a escala do tempo e não o formato, e por isso a "
        "simulação cria os efeitos mudando só a escala; o que a Weibull não reproduz são os poucos PRs "
        "mergeados em segundos. Com essa assimetria, mesmo com n = 30 por grupo o pressuposto de "
        "normalidade do t de Welch fica em dúvida, e é isso que as seções 4 e 5 testam."
    )
    st.caption(
        f"Dados reais: `dados/tempo-ate-merge-langflow.csv` (`scripts/coletar_prs.py`). Simulados: "
        f"`dados/tempo-ate-merge-simulado.csv`, cenário `{CENARIO_REAL}` com n = "
        f"{len(simulados['sem_bot'])} por grupo e semente fixa (`scripts/gerar_dados_simulados.py`). "
        f"Ajuste e comparação pelo AIC em "
        f"[cenario-e-hipoteses.md]({LINK_REPOSITORIO}/blob/main/docs/cenario-e-hipoteses.md)."
    )


def secao_testes():
    welch, mann_whitney, n = aplicar_os_testes(CENARIO_REAL)
    criticos = (stats.t(df=welch["gl"]).ppf(1 - ALFA / 2), stats.norm().ppf(1 - ALFA / 2))

    st.header("3. Como os testes funcionam")
    st.plotly_chart(grafico_g2(welch, mann_whitney, n))
    st.markdown(
        "**O que o gráfico mostra.** O t de Welch compara as **médias** dos dois grupos, dividindo a "
        "diferença pelo erro-padrão, e o Mann-Whitney compara os **postos**, contando em quantos dos "
        f"{n[0] * n[1]} pares possíveis o PR com bot foi o mais lento; cada curva é a distribuição dessa "
        "estatística quando H₀ é verdadeira (t de Student e normal padrão, respectivamente). A faixa cinza é "
        f"a região de rejeição, os {br(ALFA * 100, 0)}% de resultados mais extremos (|t| > {br(criticos[0])} "
        f"e |z| > {br(criticos[1])}), dividida entre as duas caudas porque os testes são bilaterais.\n\n"
        "**O que concluímos.** A área colorida é o **p-valor** do exemplo, o conjunto simulado com diferença "
        "real: a probabilidade de uma estatística tão ou mais extrema **se H₀ fosse verdadeira**, e não a "
        f"probabilidade de H₀ ser verdadeira; ela vale {br(welch['p_valor'], 3)} no t de Welch e "
        f"{br(mann_whitney['p_valor'], 3)} no Mann-Whitney, acima de {br(ALFA * 100, 0)}%, então nenhum dos "
        "dois rejeita H₀. Como geramos esses dados com diferença, sabemos que os dois cometeram um **erro "
        "tipo II**, e as seções 4 e 5 medem com que frequência isso acontece em 10.000 repetições."
    )
    st.caption(
        f"Estatísticas calculadas por `scripts/aplicar_testes.py` sobre o cenário `{CENARIO_REAL}` de "
        f"`dados/tempo-ate-merge-simulado.csv`. O Mann-Whitney é mostrado com U padronizado, "
        f"z = (|U − n₁n₂/2| − 0,5) / √(n₁n₂(n₁+n₂+1)/12), com a mesma correção de continuidade que o próprio "
        f"teste usa nesse tamanho de amostra; por isso a área sombreada é exatamente o p-valor exibido. "
        f"Detalhes em [testes-nos-dados-simulados.md]({LINK_REPOSITORIO}/blob/main/docs/testes-nos-dados-simulados.md)."
    )


def secao_erro_tipo_i():
    st.header("4. Erro tipo I")
    st.plotly_chart(grafico_g3(carregar_simulacao()))
    em_construcao("Texto interpretativo do G3", "Issue #25")
    repeticoes = f"{REPETITIONS:_}".replace("_", ".")
    st.caption(
        f"Taxas do efeito 0 de `resultados/simulacao.csv` ({repeticoes} repetições, semente 42), geradas por "
        "`scripts/poder.py` e `scripts/violacao.py`. Situação com outliers descrita em "
        f"[violacao-de-pressuposto.md]({LINK_REPOSITORIO}/blob/main/docs/violacao-de-pressuposto.md); "
        f"comparação com α = 0,01 em [nivel-de-significancia.md]({LINK_REPOSITORIO}/blob/main/docs/nivel-de-significancia.md)."
    )


def secao_poder():
    st.header("5. Poder")
    st.plotly_chart(grafico_g4(carregar_simulacao()))
    em_construcao("Texto interpretativo do G4", "Issue #25")
    st.caption(
        "Taxas de rejeição de `resultados/simulacao.csv`, uma curva por situação e teste, geradas por "
        "`scripts/poder.py` e `scripts/violacao.py`. O efeito é o aumento da mediana do grupo com bot, em "
        "horas; o de 10 h é próximo do observado nos dados reais. Outros tamanhos de amostra em "
        f"[tamanho-da-amostra.md]({LINK_REPOSITORIO}/blob/main/docs/tamanho-da-amostra.md)."
    )


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
