from lexer import parseExpressao


def testar_entradas_validas():
    print("Testando entradas válidas:\n")

    # lista de expressões validas da linguagem
    testes = [
        "(3.14 2.0 +)",
        "(5 RES)",
        "(10.5 CONTADOR)",
        "(1.0 2.0 *)",
        "((3.0 4.0 +) 2.0 /)",
        "(10 3 //)",
        "(10 3 %)",
        "(2 3 ^)",
        "(4.5 2.0 -)",
        "(VARIAVEL 5 +)",
        "(-3.5 2 +)" 
    ]

    aprovados = 0

    # percorre todos os testes validos
    for teste in testes:
        try:
            tokens = parseExpressao(teste)

            print(f"✓ '{teste}' -> {tokens}")
            aprovados += 1

        except Exception as e:

            print(f"✗ '{teste}' -> Erro inesperado: {e}")

    print(f"\n{aprovados}/{len(testes)} testes válidos passaram.\n")



# Esta função testa expressões que devem gerar erro
def testar_entradas_invalidas():
    print("Testando entradas inválidas:\n")

    # lista de expressões invalidas
    testes = [
        "(3.14.5 2.0 +)",   
        "(3,45 2.0 +)",    
        "(3.14 2.0 &)",     
        "(3.14 2.0 +",     
        ")3.14 2.0 +(",    
        "(3.14 @ 2.0 +)",   
        "(var 2.0 +)",    
    ]

    aprovados = 0

    # percorre todos os testes invalidos
    for teste in testes:
        try:
            tokens = parseExpressao(teste)

            print(f"✗ '{teste}' -> {tokens} (deveria falhar)")

        except Exception as e:
            print(f"✓ '{teste}' -> Erro esperado: {e}")
            aprovados += 1

    print(f"\n{aprovados}/{len(testes)} testes inválidos detectados.\n")


if __name__ == "__main__":
    testar_entradas_validas()

    print("-" * 40 + "\n")

    testar_entradas_invalidas()
