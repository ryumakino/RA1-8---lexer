"""
Gerador de Assembly ARMv7 (CPULATOR) com suporte a IEEE754 64 bits

Integrantes (ordem alfabética):
Murilo Chandelier Pedrazzani - https://github.com/MuriloPedrazzani
Ricardo Ryu Magalhães Makino - https://github.com/ryumakino
Ricardo Vinicius Moreira Vianna - https://github.com/ricaprof

Grupo no Canvas: RA1 8
Disciplina: Construção de Interpretadores
Professor: Frank Alcantara

"""

OPERADORES_SIMPLES = {"+", "-", "*", "/", "%", "^"}

OPERADORES_COMPOSTOS = {"//"} 

PREFIXOS_OPERADORES = {op[0] for op in OPERADORES_SIMPLES.union(OPERADORES_COMPOSTOS)} 

PARENTESES = {"(", ")"}

def erro(msg, linha, pos):

    raise ValueError(f"Erro léxico na posição {pos}: {msg}\n{linha}")

def checar_delimitador(linha, i):

    if i < len(linha):
        c = linha[i]
        if not (c.isspace() or c in PARENTESES):
            erro("Falta de espaçamento ou token inválido colado (Boundary Error)", linha, i)

def estadoNumero(linha, i):

    numero = ""
    tem_ponto = False
    tem_digito = False

    if linha[i] == "-":
        numero += "-"
        i += 1

    while i < len(linha):
        c = linha[i]

        if c.isdigit():
            numero += c
            tem_digito = True
            i += 1

        elif c == ".":

            if tem_ponto:
                erro("Número malformado (múltiplos pontos decimais)", linha, i)

            tem_ponto = True
            numero += c
            i += 1

        else:
            break

    # Validações finais da formação do numero
    if not tem_digito:
        erro("Número inválido (sem dígitos)", linha, i)

    if numero.endswith("."):
        erro("Número malformado (não pode terminar com ponto)", linha, i)

    if numero.startswith(".") or numero.startswith("-."):
        erro("Número malformado (não pode iniciar com ponto)", linha, i)

    # Verifica se há delimitador correto após o numero
    checar_delimitador(linha, i)

    return numero, i

def estadoPalavra(linha, i):

    inicio = i
    palavra = ""

    while i < len(linha) and linha[i].isalpha():
        palavra += linha[i]
        i += 1

    # Garante padrão da linguagem
    if not palavra.isupper():
        erro("Variáveis e comandos (RES/MEM) devem conter apenas letras maiúsculas", linha, inicio)

    checar_delimitador(linha, i)

    return palavra, i

def estadoOperador(linha, i):

    # Operador composto
    if linha[i:i+2] == "//":
        i += 2
        token = "//"

    # Operadores simples
    elif linha[i] in OPERADORES_SIMPLES:
        token = linha[i]
        i += 1

    else:
        erro("Operador inválido ou caractere desconhecido", linha, i)

    checar_delimitador(linha, i)

    return token, i

def estadoParenteses(linha, i):

    return linha[i], i + 1

def validarParenteses(tokens, linha):

    count = 0

    for t in tokens:

        if t == "(":
            count += 1

        elif t == ")":
            count -= 1

        if count < 0:
            raise ValueError(f"Erro: Parênteses fechado sem ter sido aberto.\n{linha}")

    if count != 0:
        raise ValueError(f"Erro: Parênteses abertos não foram fechados.\n{linha}")

def parseExpressao(linha):

    tokens = []
    i = 0

    while i < len(linha):

        c = linha[i]

        if c.isspace():
            i += 1
            continue

        # Reconhecimento de parenteses
        if c in PARENTESES:
            token, i = estadoParenteses(linha, i)
            tokens.append(token)
            continue

        # Reconhecimento de numeros
        if c.isdigit() or (c == "-" and i + 1 < len(linha) and (linha[i+1].isdigit() or linha[i+1] == ".")):
            token, i = estadoNumero(linha, i)
            tokens.append(token)
            continue

        # Reconhecimento de palavras
        if c.isalpha():
            token, i = estadoPalavra(linha, i)
            tokens.append(token)
            continue

        # Reconhecimento de operadores
        if c in PREFIXOS_OPERADORES:
            token, i = estadoOperador(linha, i)
            tokens.append(token)
            continue

        # Caso nenhum token seja reconhecido
        erro("Caractere inválido na linguagem", linha, i)

    validarParenteses(tokens, linha)

    return tokens
