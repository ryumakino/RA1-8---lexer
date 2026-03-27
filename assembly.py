def isNumero(token):
    try:
        float(token)
        return True
    except ValueError:
        return False

def gerarAssembly(linhas_tokens):

    assembly_data = []

    assembly_text = []

    constants = []

    const_map = {
        repr(0.0): "const_zero",
        repr(1.0): "const_one"
    }

    # palavras reservadas da linguagem
    palavras_reservadas = {"RES", "True", "False", "None"}

    assembly_data.append(".data")
    assembly_data.append("    .align 3")

    tamanho_historico = len(linhas_tokens) * 8

    if tamanho_historico == 0:
        tamanho_historico = 8

    assembly_data.append(f"historico: .space {tamanho_historico}")

    assembly_data.append("const_zero: .double 0.0")
    assembly_data.append("const_one: .double 1.0")

    variaveis = set()
    for tokens in linhas_tokens:
        for t in tokens:
            if t.isidentifier() and t not in palavras_reservadas:
                variaveis.add(t)

    # cria espaço para cada variavel na memória
    for v in sorted(variaveis):
        assembly_data.append(f"var_{v}: .double 0.0")

    assembly_text.append(".text")
    assembly_text.append(".global _start")
    assembly_text.append("_start:")

    label_id = 0

    for linha_idx, tokens in enumerate(linhas_tokens):

        # contador de elementos na pilha
        stack_count = 0 

        for i, token in enumerate(tokens):

            if token in ("(", ")"):
                continue

            if isNumero(token):

                val_float = float(token)
                val_str = repr(val_float)

                # adiciona constante ao pool caso ainda não exista
                if val_str not in const_map:
                    const_name = f"const_{len(const_map)}"
                    const_map[val_str] = const_name
                    constants.append(f"{const_name}: .double {val_float}")
                else:
                    const_name = const_map[val_str]

                # carrega constante para registrador
                assembly_text.append(f"    LDR R0, ={const_name}")
                assembly_text.append("    VLDR.F64 D0, [R0]")
                assembly_text.append("    VPUSH {D0}")

                stack_count += 1
                continue

            if token in ("+", "-", "*", "/"):

                # verifica se existem operandos suficientes
                if stack_count < 2:
                    raise ValueError(
                        f"Stack underflow no token '{token}' na linha {linha_idx}"
                    )

                assembly_text.append("    VPOP {D1}")
                assembly_text.append("    VPOP {D0}")
                stack_count -= 2

                if token == "+":
                    assembly_text.append("    VADD.F64 D0, D0, D1")

                elif token == "-":
                    assembly_text.append("    VSUB.F64 D0, D0, D1")

                elif token == "*":
                    assembly_text.append("    VMUL.F64 D0, D0, D1")

                elif token == "/":
                    assembly_text.append("    LDR R0, =const_zero")
                    assembly_text.append("    VLDR.F64 D2, [R0]")
                    assembly_text.append("    VCMP.F64 D1, D2")
                    assembly_text.append("    VMRS APSR_nzcv, FPSCR")
                    assembly_text.append("    BEQ throw_error")
                    assembly_text.append("    VDIV.F64 D0, D0, D1")

                # empilha resultado
                assembly_text.append("    VPUSH {D0}")
                stack_count += 1
                continue


            # implementação manual usando loop de subtração
            if token in ("//", "%"):

                if stack_count < 2:
                    raise ValueError(
                        f"Stack underflow no token '{token}' na linha {linha_idx}"
                    )

                assembly_text.append("    VPOP {D1}")
                assembly_text.append("    VPOP {D0}")
                stack_count -= 2

                # conversão para inteiro
                assembly_text.append("    VCVT.S32.F64 S30, D0")
                assembly_text.append("    VMOV R0, S30")
                assembly_text.append("    VCVT.S32.F64 S31, D1")
                assembly_text.append("    VMOV R1, S31")

                # codigo de divisão usando loop
                assembly_text.append("    MOV R2, #0")
                assembly_text.append("    MOV R3, R0")

                loop = f"div_loop_{label_id}"
                end = f"div_end_{label_id}"
                label_id += 1

                assembly_text.append(f"{loop}:")
                assembly_text.append("    CMP R3, R1")
                assembly_text.append(f"    BLT {end}")
                assembly_text.append("    SUB R3, R3, R1")
                assembly_text.append("    ADD R2, R2, #1")
                assembly_text.append(f"    B {loop}")
                assembly_text.append(f"{end}:")

                # escolhe quociente ou resto
                if token == "//":
                    assembly_text.append("    MOV R4, R2")
                else:
                    assembly_text.append("    MOV R4, R3")

                # converte novamente para float
                assembly_text.append("    VMOV S30, R4")
                assembly_text.append("    VCVT.F64.S32 D0, S30")
                assembly_text.append("    VPUSH {D0}")

                stack_count += 1
                continue

            if token == "^":

                if stack_count < 2:
                    raise ValueError(
                        f"Stack underflow no token '{token}' na linha {linha_idx}"
                    )

                assembly_text.append("    VPOP {D1}")
                assembly_text.append("    VPOP {D0}")
                stack_count -= 2

                start = f"pow_loop_{label_id}"
                end = f"pow_end_{label_id}"
                label_id += 1

                assembly_text.append("    VMOV.F64 D30, D0")

                assembly_text.append(f"{start}:")
                assembly_text.append("    CMP R2, #0")
                assembly_text.append(f"    BEQ {end}")
                assembly_text.append("    VMUL.F64 D30, D30, D0")
                assembly_text.append("    SUB R2, R2, #1")
                assembly_text.append(f"    B {start}")

                assembly_text.append(f"{end}:")
                assembly_text.append("    VMOV.F64 D0, D30")
                assembly_text.append("    VPUSH {D0}")

                stack_count += 1
                continue


            if token == "RES":

                if stack_count < 1:
                    raise ValueError(
                        f"Stack underflow: falta operando N para RES na linha {linha_idx}"
                    )

                assembly_text.append("    VPOP {D0}")
                stack_count -= 1

                assembly_text.append("    VCVT.S32.F64 S31, D0")
                assembly_text.append("    VMOV R1, S31")

                assembly_text.append(f"    LDR R2, ={linha_idx}")
                assembly_text.append("    SUB R2, R2, R1")
                assembly_text.append("    SUB R2, R2, #1")

                assembly_text.append("    MOV R3, #8")
                assembly_text.append("    MUL R2, R2, R3")

                assembly_text.append("    LDR R4, =historico")
                assembly_text.append("    ADD R4, R4, R2")

                assembly_text.append("    VLDR.F64 D0, [R4]")
                assembly_text.append("    VPUSH {D0}")

                stack_count += 1
                continue

            if token.isidentifier() and token not in palavras_reservadas:

                # verifica se é leitura ou escrita
                is_read = (i > 0 and tokens[i - 1] == "(")

                if is_read:

                    assembly_text.append(f"    LDR R0, =var_{token}")
                    assembly_text.append("    VLDR.F64 D0, [R0]")
                    assembly_text.append("    VPUSH {D0}")
                    stack_count += 1

                else:

                    if stack_count < 1:
                        raise ValueError(
                            f"Stack underflow ao salvar variável '{token}'"
                        )

                    assembly_text.append("    VPOP {D0}")
                    stack_count -= 1

                    assembly_text.append(f"    LDR R0, =var_{token}")
                    assembly_text.append("    VSTR.F64 D0, [R0]")

                    assembly_text.append("    VPUSH {D0}")
                    stack_count += 1

                continue

            # proteção contra tokens invalidos
            raise ValueError(
                f"Token sintatico invalido ou desconhecido: '{token}'"
            )


        if stack_count > 1:
            raise ValueError(
                f"Erro de sintaxe: múltiplos valores na pilha na linha {linha_idx}"
            )

        elif stack_count == 1:

            assembly_text.append("    VPOP {D0}")
            stack_count -= 1

            assembly_text.append("    LDR R0, =historico")
            assembly_text.append(f"    LDR R1, ={linha_idx * 8}")
            assembly_text.append("    ADD R0, R0, R1")
            assembly_text.append("    VSTR.F64 D0, [R0]")


    assembly_text.append("")
    ultima_linha_idx = max(0, len(linhas_tokens) - 1) * 8

    assembly_text.append("    LDR R0, =historico")
    assembly_text.append(f"    LDR R1, ={ultima_linha_idx}")
    assembly_text.append("    ADD R0, R0, R1")
    assembly_text.append("    VLDR.F64 D0, [R0]")

    assembly_text.append("    VCVT.S32.F64 S31, D0")
    assembly_text.append("    VMOV R1, S31")

    # envia resultado para display do simulador
    assembly_text.append("    LDR R0, =0xFF200000")
    assembly_text.append("    STR R1, [R0]")


    assembly_text.append("    B .")


    assembly_text.append("")
    assembly_text.append("throw_error:")
    assembly_text.append("    LDR R0, =0xFF200000")
    assembly_text.append("    LDR R1, =0xEEEEEEEE")
    assembly_text.append("    STR R1, [R0]")
    assembly_text.append("    B .")


    # adiciona constantes extras na seção .data
    for const in constants:
        assembly_data.append("    " + const)

    return assembly_data + [""] + assembly_text

def salvarAssembly(codigo):
    try:
        with open("program.s", "w") as f:
            for linha in codigo:
                f.write(linha + "\n")

        print("Assembly gerado com sucesso em 'program.s'")

    except Exception as e:
        print(f"Erro ao salvar assembly: {e}")