import sys
from lexer import parseExpressao
from executor import executarExpressao
from assembly import gerarAssembly

def lerArquivo(nomeArquivo):
    try:
        with open(nomeArquivo, "r") as arquivo:
            return arquivo.readlines()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nomeArquivo}' não foi encontrado.")
        sys.exit(1)


def salvarTokens(tokens):
    try:
        with open("tokens.txt", "w") as arquivo:
            for token in tokens:
                arquivo.write(str(token) + "\n")
    except Exception as e:
        print(f"Erro ao salvar tokens: {e}")


def salvarAssembly(codigo):
    try:
        with open("program.s", "w") as arquivo:
            if isinstance(codigo, list):
                arquivo.write("\n".join(codigo) + "\n")
            else:
                arquivo.write(str(codigo) + "\n")
    except Exception as e:
        print(f"Erro ao salvar assembly: {e}")


def exibirResultados(resultados):
    if not resultados:
        print("\nNenhuma expressão válida foi executada.")
        return

    print("\nResultados:")
    for linha, resultado in resultados:
        print(f"Linha {linha}: {resultado}")


def main():

    # verifica se o usuario passou o arquivo de entrada
    if len(sys.argv) < 2:
        print("Uso: python main.py teste1.txt")
        sys.exit(1)

    nomeArquivo = sys.argv[1]

    linhas = lerArquivo(nomeArquivo)

    resultados = []
    linha_atual = 1

    # guarda tokens da ultima execução válida
    tokensUltimaExecucao = []

    # guarda os tokens de todas as linhas validas
    linhas_tokens = []

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            linha_atual += 1
            continue

        try:
            tokens = parseExpressao(linha)

            resultado = executarExpressao(tokens)

            resultados.append((linha_atual, resultado))

            # guarda tokens para geração de arquivos
            tokensUltimaExecucao = tokens
            linhas_tokens.append(tokens)

        except Exception as e:
            # caso ocorra erro em alguma linha
            print(f"Erro na linha {linha_atual}: {e}")

        linha_atual += 1

    # salva os tokens da ultima expressão válida
    if tokensUltimaExecucao:
        salvarTokens(tokensUltimaExecucao)

    # gera o assembly apenas se houver expressões validas
    if linhas_tokens:
        codigoAssembly = gerarAssembly(linhas_tokens)

        if codigoAssembly:
            salvarAssembly(codigoAssembly)

    # mostra os resultados no terminal
    exibirResultados(resultados)

if __name__ == "__main__":
    main()