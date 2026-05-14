import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from views.whitelist_button import WhitelistView

load_dotenv()
TOKEN = os.getenv("WHITELIST_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user} (ID: {bot.user.id})")
    print("----------------------------------------------")


@bot.command(name="form")
@commands.has_permissions(administrator=True)
async def form(ctx: commands.Context):
    """Envia o embed de abertura de whitelist com botão."""
    embed = discord.Embed(
        title="📋 Sistema de Whitelist",
        description=(
            "Bem-vindo ao processo de **Whitelist**!\n\n"
            "Para ingressar em nosso servidor de Roleplay, você precisa responder "
            "algumas perguntas e criar o perfil do seu personagem.\n\n"
            "🔒 **Canal privado** será aberto exclusivamente para você.\n"
            "⏱️ Você terá **5 minutos** para responder cada pergunta.\n\n"
            "Clique no botão abaixo para começar."
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="Sistema de Whitelist • Powered by Discord Bot")
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)

    view = WhitelistView()
    await ctx.send(embed=embed, view=view)


@form.error
async def form_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando.", delete_after=5)


bot.run(TOKEN)
