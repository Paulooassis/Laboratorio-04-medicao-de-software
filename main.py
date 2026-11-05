"""Roda o laboratório do início ao fim com um único comando.

Uso: python main.py

1. Gera os dados simulados com semente fixa (scripts/gerar_dados_simulados.py).
2. Aplica o t de Welch e o Mann-Whitney a esses dados (scripts/aplicar_testes.py).
"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
os.chdir(RAIZ)

import aplicar_testes  # noqa: E402
import gerar_dados_simulados  # noqa: E402


def main():
    sys.argv = sys.argv[:1]  # cada etapa usa os caminhos padrão
    print("# 1. Gerando os dados simulados")
    gerar_dados_simulados.main()
    print("\n# 2. Aplicando os testes aos dados simulados")
    aplicar_testes.main()


if __name__ == "__main__":
    main()
