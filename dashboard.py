"""Dashboard do laboratório: testes de hipótese por dentro (t de Welch x Mann-Whitney).

Uso: streamlit run dashboard.py

Mostra os dados gerados por código do repositório: os dados reais (scripts/coletar_prs.py) e, nas
próximas Issues, os simulados e os resultados (python main.py). As seções seguem a ordem da seção 4
do enunciado. Os gráficos G1 a G4 entram nas Issues seguintes, usando as cores definidas aqui.
"""
import csv
import os
from datetime import datetime

import numpy as np
import streamlit as st

RAIZ = os.path.dirname(os.path.abspath(__file__))
DADOS_REAIS = os.path.join(RAIZ, "dados", "tempo-ate-merge-langflow.csv")

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
    st.header("2. Os dados")
    em_construcao("G1, dados reais ao lado dos simulados", "Issue #7")


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
