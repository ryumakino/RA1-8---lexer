from lexer import parseExpressao

CASOS_VALIDOS = [
    "(3.14 2.0 +)",
    "(5 RES)",
    "(1.0 2.0 *)",
    "((3.0 4.0 +) 2.0 /)",
    "(10 3 //)",
    "(10 3 %)",
    "(2 3 ^)",
    "(4.5 2.0 -)",
    "(-3.5 2 +)",
    "(0.5 1.5 +)",
    "(100 200 +)",
    "(1 2 +)",
    "((1 2 +) (3 4 +) *)",
    "(10 -2 +)",
    "((-3 4 +) 2 *)",
    "(10 5 /)",
    "(8 2 //)",
    "(2 3 4 +)"  # depende do enunciado (pode aceitar como tokens)
]

CASOS_INVALIDOS = [
    "(3.14.5 2.0 +)",   # múltiplos pontos
    "(3,45 2.0 +)",     # vírgula inválida
    "(3.14 2.0 &)",     # caractere inválido
    "(3.14 @ 2.0 +)",   # caractere inválido
    "(var 2.0 +)",      # palavra inválida
    "(10 2 ///)",       # operador inválido
    "(.5 2 +)",         # decimal inválido
    "(3. 2 +)",         # decimal inválido
    "(- 3.5 2 +)",      # negativo mal formado
    # letras minúsculas
    "(res 2 +)",
    "(Mem 2 +)",
]

def avaliar_casos(casos):
    for caso in casos:
        try:
            tokens = parseExpressao(caso)
            print(f"{caso} -> {tokens}")
        except Exception as e:
            print(f"{caso} -> ERRO: {e}")

def testar_lexer():
    print("=== TESTES VÁLIDOS ===")
    avaliar_casos(CASOS_VALIDOS)
    print("\n" + "-" * 40)
    print("=== TESTES INVÁLIDOS ===")
    avaliar_casos(CASOS_INVALIDOS)

if __name__ == "__main__":
    testar_lexer()
