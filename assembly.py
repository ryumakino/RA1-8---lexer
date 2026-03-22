def gerarAssembly(tokens):

    assembly = []

    assembly.append(".global _start")
    assembly.append("")
    assembly.append(".text")
    assembly.append("_start:")

    stack = []
    freg = 0 
    label_id = 0
    memoria = {}

    for token in tokens:

        if token in ["(", ")"]:
            continue

        # Carrega numero em registrador
        if token.replace('.', '', 1).isdigit():

            assembly.append(f"    VMOV.F64 D{freg}, #{token}")
            stack.append(f"D{freg}")
            freg += 1
            continue

        # Operações basicas
        if token in ["+", "-", "*", "/"]:

            r2 = stack.pop()
            r1 = stack.pop()

            if token == "+":
                assembly.append(f"    VADD.F64 {r1}, {r1}, {r2}")
            elif token == "-":
                assembly.append(f"    VSUB.F64 {r1}, {r1}, {r2}")
            elif token == "*":
                assembly.append(f"    VMUL.F64 {r1}, {r1}, {r2}")
            elif token == "/":
                assembly.append(f"    VDIV.F64 {r1}, {r1}, {r2}")

            stack.append(r1)
            continue

        # Potencia via loop
        if token == "^":

            r2 = stack.pop()
            r1 = stack.pop()

            start = f"pow_loop_{label_id}"
            end = f"pow_end_{label_id}"
            label_id += 1

            assembly.append(f"    VMOV R1, {r1}")
            assembly.append(f"    VMOV R2, {r2}")
            assembly.append("    MOV R3, #1")

            assembly.append(f"{start}:")
            assembly.append("    CMP R2, #0")
            assembly.append(f"    BEQ {end}")
            assembly.append("    MUL R3, R3, R1")
            assembly.append("    SUB R2, R2, #1")
            assembly.append(f"    B {start}")
            assembly.append(f"{end}:")
            assembly.append("    VMOV D0, R3")

            stack.append("D0")
            continue

        # Variaveis
        if token.isalpha():

            if token in memoria:
                stack.append(memoria[token])
            else:
                r = stack.pop()
                memoria[token] = f"D{20 + len(memoria)}"
                assembly.append(f"    VMOV.F64 {memoria[token]}, {r}")

            continue

    # Finalização do programa
    assembly.append("")
    assembly.append("    @ Exibir resultado final nos LEDs")
    assembly.append("    VMOV R1, D0")
    assembly.append("    MOV R0, #0xFF200000")
    assembly.append("    STR R1, [R0]")
    assembly.append("    B .")

    return assembly

# Salva o codigo assembly em arquivo
def salvarAssembly(codigo):

    try:
        with open("program.s", "w") as f:
            for linha in codigo:
                f.write(linha + "\n")

        print("Assembly salvo em program.s")

    except Exception as e:
        print(f"Erro ao salvar assembly: {e}")