"""Roda o laboratório do início ao fim com um único comando e regenera todos os CSV.

Uso: python main.py

1. Gera os dados simulados com semente fixa (scripts/gerar_dados_simulados.py).
2. Aplica o t de Welch e o Mann-Whitney a esses dados (scripts/aplicar_testes.py).
3. Mede o erro tipo I no cenário ideal (scripts/erro_tipo1.py).
4. Mede o poder no cenário ideal, com efeitos crescentes (scripts/poder.py).
5. Repete o erro tipo I e o poder na situação com outliers (scripts/violacao.py).
6. Consolida os resultados da simulação em resultados/simulacao.csv (scripts/consolidar_resultados.py).
7. Mede o poder com outros tamanhos de amostra (scripts/tamanho_amostra.py).

As etapas 3 a 5 e 7 rodam 10.000 repetições por combinação, então a execução completa leva cerca de
12 minutos.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
os.chdir(RAIZ)

import aplicar_testes  # noqa: E402
import gerar_dados_simulados  # noqa: E402
from scripts import consolidar_resultados, erro_tipo1, poder, tamanho_amostra, violacao  # noqa: E402


def main():
    sys.argv = sys.argv[:1]  # cada etapa usa os caminhos padrão
    print("# 1. Gerando os dados simulados")
    gerar_dados_simulados.main()
    print("\n# 2. Aplicando os testes aos dados simulados")
    aplicar_testes.main()
    print("\n# 3. Medindo o erro tipo I no cenário ideal")
    erro_tipo1.main()
    print("\n# 4. Medindo o poder no cenário ideal")
    poder.main()
    print("\n# 5. Medindo o erro tipo I e o poder na situação com outliers")
    violacao.main()
    print("\n# 6. Consolidando os resultados da simulação")
    consolidar_resultados.main()
    print("\n# 7. Medindo o poder com outros tamanhos de amostra")
    tamanho_amostra.main()


if __name__ == "__main__":
    main()
