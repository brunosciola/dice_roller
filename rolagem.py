import random
import re


def extrair_dados(dice_string):
    padrao = re.compile(r'(\d+)[dD](\d+)([+-]\d+)?')
    match = padrao.match(dice_string)

    if not match:
        raise ValueError("Formato inválido. Use algo como 1d20+2")

    qtDados = int(match.group(1))
    tpDados = int(match.group(2))
    MdDados = int(match.group(3)[1:]) if match.group(3) else 0
    operador = match.group(3)[0] if match.group(3) else '+'

    return qtDados, tpDados, MdDados, operador


def roll_dice_complex(dice_string, modo_dinamico=False):
    try:
        qtDados, tpDados, MdDados, operador = extrair_dados(dice_string)
        resultados = []

        for _ in range(qtDados):
            rolagem = random.randint(1, tpDados)
            modificado = rolagem + MdDados if operador == '+' else rolagem - MdDados

            resultado = f"{modificado} ({rolagem}{operador}{MdDados})" if MdDados != 0 else str(rolagem)

            if modo_dinamico:
                if modificado <= 6:
                    resultado += " **[FALHA]**"
                elif 7 <= modificado <= 13:
                    resultado += " **[PARCIAL]**"
                else:
                    resultado += " **[ACERTO]**"

            resultados.append(resultado)

        return f"{dice_string}: " + " | ".join(resultados)

    except Exception as e:
        return f"Erro: {str(e)}"
