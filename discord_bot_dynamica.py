import discord
from discord.ext import commands
import random
import re
from dotenv import load_dotenv
import os

# Configurações do bot
load_dotenv()
TOKEN = os.getenv('TOKEN')  # Substitua pelo token do seu bot
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia mensagens

# Cria uma instância do bot
bot = commands.Bot(command_prefix="!", intents=intents)  # Prefixo definido, mas não usado

# Dicionário para armazenar o estado do modo dinâmico por servidor
modo_dinamico_por_servidor = {}

# Função para extrair qtDados, tpDados e MdDados
def extrair_dados(dice_string):
    """
    Extrai qtDados, tpDados e MdDados de uma string no formato XdY+Z ou XdY-Z.
    """
    padrao = re.compile(r'(\d+)[dD](\d+)([+-]\d+)?')
    correspondencia = padrao.match(dice_string)

    if correspondencia:
        qtDados = int(correspondencia.group(1))  # Números antes do 'd'
        tpDados = int(correspondencia.group(2))  # Números depois do 'd'
        MdDados = int(correspondencia.group(3)) if correspondencia.group(3) else 0  # Modificador (+ ou -)
        return qtDados, tpDados, MdDados
    else:
        raise ValueError("Formato inválido. Use algo como 1d20+2 ou 2d6-1.")

# Função para rolar dados com 100 rolagens
def roll_dice_complex(dice_string, modo_dinamico_ativado=False):
    """
    Rola um dado no formato XdY+Z, gerando 100 rolagens e escolhendo uma aleatoriamente.
    Retorna o resultado e a expressão completa.
    """
    try:
        # Extrai qtDados, tpDados e MdDados
        qtDados, tpDados, MdDados = extrair_dados(dice_string)

        resultados = []
        for _ in range(qtDados):
            # Gera 100 rolagens
            rolagens = [random.randint(1, tpDados) for _ in range(200)]
            # Escolhe uma rolagem aleatória
            escolhido = random.choice(rolagens)
            # Aplica o modificador
            total = escolhido + MdDados
            # Formata o resultado
            if MdDados == 0:
                resultado = f"{escolhido}"
            elif MdDados > 0:
                resultado = f"{total} ({escolhido}+{MdDados})"
            else:
                resultado = f"{total} ({escolhido}{MdDados})"

            # Adiciona a tag dinâmica, se o modo estiver ativado
            if modo_dinamico_ativado:
                if total <= 7:
                    resultado += " [**FALHA**]"
                elif 8 <= total <= 13:
                    resultado += " [**ACERTO PARCIAL**]"
                else:
                    resultado += " [**ACERTO**]"

            resultados.append(resultado)

        # Retorna o resultado formatado
        return f"{dice_string}: {' | '.join(resultados)}"
    except ValueError as e:
        return f"Erro ao rolar {dice_string}: {e}"

# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} está online!")
    try:
        # Sincroniza os comandos com o Discord
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

# Comando para ativar/desativar o modo dinâmico por servidor
@bot.command(name="dynamica")
async def toggle_dynamica(ctx):
    """
    Ativa ou desativa o modo dinâmico para o servidor atual.
    """
    guild_id = ctx.guild.id  # ID do servidor
    if guild_id in modo_dinamico_por_servidor:
        modo_dinamico_por_servidor[guild_id] = not modo_dinamico_por_servidor[guild_id]  # Alterna o estado
    else:
        modo_dinamico_por_servidor[guild_id] = True  # Ativa o modo dinâmico

    estado = "ativado" if modo_dinamico_por_servidor[guild_id] else "desativado"
    await ctx.send(f"Modo dinâmico {estado} para este servidor.")

# Evento para detectar e responder a mensagens no formato XdY+Z
@bot.event
async def on_message(message):
    # Ignora mensagens enviadas pelo próprio bot
    if message.author == bot.user:
        return

    # Verifica se a mensagem contém uma expressão de dados (ex: 1d20+2)
    padrao = re.compile(r'\b(\d+[dD]\d+([+-]\d+)?)\b')
    correspondencias = padrao.findall(message.content)

    if correspondencias:
        resultados = []
        for match in correspondencias:
            dice_string = match[0]
            # Verifica se o modo dinâmico está ativado para o servidor atual
            guild_id = message.guild.id
            modo_dinamico_ativado = modo_dinamico_por_servidor.get(guild_id, False)
            resultado = roll_dice_complex(dice_string, modo_dinamico_ativado)
            resultados.append(resultado)

        # Envia todos os resultados em uma única mensagem
        await message.channel.send(f"{message.author.mention} rolou:\n" + "\n".join(resultados))

    # Permite que outros comandos funcionem (se houver)
    await bot.process_commands(message)

# Inicia o bot
bot.run(TOKEN)