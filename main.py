import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import re
from rolagem import roll_dice_complex, extrair_dados
from reacao import ReacaoManager

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
modo_dinamico_por_servidor = {}
reacao_manager = ReacaoManager()


@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} está online!")


@bot.command(name="dynamica")
async def toggle_dynamica(ctx):
    guild_id = ctx.guild.id
    modo_dinamico_por_servidor[guild_id] = not modo_dinamico_por_servidor.get(guild_id, False)
    estado = "ativado" if modo_dinamico_por_servidor[guild_id] else "desativado"
    await ctx.send(f"Modo dinâmico {estado}!")


@bot.command(name="joga_reacao")
async def iniciar_reacao(ctx):
    reacao_manager.limpar_reacao()
    reacao_manager.iniciar_reacao()
    await ctx.send("Modo reação ativado! Comecem a rolar os dados no formato `XdY NOME` (ex: 1d20 Goblin)")


@bot.command(name="fim")
async def finalizar_reacao(ctx):
    ordem = reacao_manager.finalizar_reacao()
    if not ordem:
        await ctx.send("Nenhuma rolagem registrada!")
        return

    mensagem = "**Ordem de Reação:**\n"
    for idx, (nome, resultado) in enumerate(ordem, 1):
        mensagem += f"{idx}. {nome} ({resultado})\n"

    await ctx.send(mensagem)



@bot.command(name="vez")
async def mostrar_vez(ctx):
    ordem = reacao_manager.obter_ordem_vez()
    if not ordem:
        await ctx.send("Nenhuma ordem salva!")
        return

    mensagem = "**Ordem Salva:**\n"
    for idx, (nome, resultado) in enumerate(ordem, 1):
        mensagem += f"{idx}. {nome} ({resultado})\n"

    await ctx.send(mensagem)


# main.py atualizado
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Processar comandos primeiro
    await bot.process_commands(message)

    # Verificar rolagens normais
    padrao_normal = re.compile(r'\b(\d+[dD]\d+([+-]\d+)?)\b')
    if not reacao_manager.modo_reacao_ativado:
        correspondencias = padrao_normal.findall(message.content)
        if correspondencias:
            resultados = []
            for match in correspondencias:
                dice_string = match[0]
                guild_id = message.guild.id
                modo_dinamico = modo_dinamico_por_servidor.get(guild_id, False)
                resultado = roll_dice_complex(dice_string, modo_dinamico)
                resultados.append(resultado)

            await message.channel.send(f"{message.author.mention} rolou:\n" + "\n".join(resultados))

    # Modo reação ativo
    else:
        padrao_reacao = re.compile(r'(\d+[dD]\d+([+-]\d+)?)\s*(.*)')
        match = padrao_reacao.search(message.content)

        if match:
            dice_string = match.group(1).strip()
            nome = match.group(3).strip() or message.author.display_name

            try:
                # Rolagem técnica para extrair apenas o valor
                guild_id = message.guild.id
                modo_dinamico = modo_dinamico_por_servidor.get(guild_id, False)
                resultado_bruto = roll_dice_complex(dice_string, modo_dinamico)

                # Extrair primeiro valor numérico do resultado
                valor = int(re.findall(r'\d+', resultado_bruto.split(":")[1])[0])
                reacao_manager.adicionar_rolagem_reacao(nome, valor)

                await message.channel.send(f"✅ {message.author.mention}: {dice_string} para {nome} ({valor})")
            except Exception as e:
                await message.channel.send(f"❌ Erro na rolagem: {str(e)}")


bot.run(TOKEN)