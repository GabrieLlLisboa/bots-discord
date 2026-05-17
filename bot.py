import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

from views.whitelist_button import WhitelistView
from views.id_view import IdView
from utils.ticket_store import ticket_store
from utils import nick_store

load_dotenv()
TOKEN = os.getenv("WHITELIST_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# { channel_id: message_id } — rastreia mensagem do !id
id_messages: dict[int, int] = {}


@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user} (ID: {bot.user.id})")
    print("----------------------------------------------")


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Monitora mudanças de nick e corrige se a pessoa tentou trocar."""
    # Só age se o nick mudou E foi o próprio membro quem alterou (não o bot)
    if before.nick == after.nick:
        return

    member_id = after.id
    correct_nick = nick_store.get(member_id)

    if not correct_nick:
        return  # Membro não tem nick registrado pelo bot

    # Se o novo nick é diferente do registrado, corrige
    if after.nick != correct_nick:
        try:
            await after.edit(
                nick=correct_nick,
                reason="Correção automática de nickname — alteração não autorizada",
            )
        except discord.Forbidden:
            pass  # Bot sem permissão (ex: dono do servidor)


@bot.event
async def on_message(message: discord.Message):
    """Fiscaliza se a mensagem do !id ainda é a última no canal."""
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    channel_id = message.channel.id
    if channel_id not in id_messages:
        return

    msg_id = id_messages[channel_id]

    try:
        last = [m async for m in message.channel.history(limit=1)][0]
    except Exception:
        return

    if last.id == msg_id:
        return

    try:
        old_msg = await message.channel.fetch_message(msg_id)
        await old_msg.delete()
    except (discord.NotFound, discord.Forbidden):
        pass

    embed = _build_id_embed()
    view = IdView(message.channel)
    new_msg = await message.channel.send(embed=embed, view=view)
    id_messages[channel_id] = new_msg.id
    view.message_id = new_msg.id


# ─────────────────────────────────────────────
#  !form
# ─────────────────────────────────────────────
@bot.command(name="form")
@commands.has_permissions(administrator=True)
async def form(ctx: commands.Context):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📋 Whitelist",
        description=(
            "Bem-vindo ao processo de **Whitelist**!\n\n"
            "Para ingressar em nosso servidor, você precisa responder "
            "algumas perguntas e criar o perfil do seu personagem.\n\n"
            "🔒 **Canal privado** será aberto exclusivamente para você.\n"
            "⏱️ Você terá **5 minutos** para responder cada pergunta.\n\n"
            "Clique no botão abaixo para começar."
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="Sistema de Whitelist • Powered by Discord Bot")
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=WhitelistView())


@form.error
async def form_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão.", delete_after=5)


# ─────────────────────────────────────────────
#  !id
# ─────────────────────────────────────────────
def _build_id_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🪪 Central de Identidades",
        description=(
            "Bem-vindo à **Central de Identidades** do servidor!\n\n"
            "Aqui você pode buscar a identidade de qualquer membro cadastrado.\n\n"
            "Clique no botão abaixo e informe o número da identidade que deseja consultar."
        ),
        color=discord.Color.dark_gold(),
    )
    embed.set_footer(text="Sistema de IDs • Digite o número da identidade")
    return embed


@bot.command(name="id")
@commands.has_permissions(administrator=True)
async def id_cmd(ctx: commands.Context):
    await ctx.message.delete()

    channel_id = ctx.channel.id
    if channel_id in id_messages:
        try:
            old = await ctx.channel.fetch_message(id_messages[channel_id])
            await old.delete()
        except (discord.NotFound, discord.Forbidden):
            pass

    view = IdView(ctx.channel)
    msg = await ctx.send(embed=_build_id_embed(), view=view)
    id_messages[channel_id] = msg.id
    view.message_id = msg.id


@id_cmd.error
async def id_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão.", delete_after=5)


# ─────────────────────────────────────────────
#  !aprovar
# ─────────────────────────────────────────────
@bot.command(name="aprovar")
@commands.has_permissions(manage_channels=True)
async def aprovar(ctx: commands.Context):
    channel = ctx.channel
    ticket_data = ticket_store.get(channel.id)

    if not ticket_data:
        await ctx.send(
            "❌ Ticket não encontrado no sistema. A whitelist pode não ter sido concluída ainda.",
            delete_after=8,
        )
        return

    member: discord.Member = ticket_data["member"]
    summary: discord.Embed = ticket_data["summary"]
    await ctx.message.delete()

    dm_embed = discord.Embed(
        title="✅ Whitelist Aprovada!",
        description=(
            "Parabéns! Sua whitelist foi **aprovada** pela equipe.\n\n"
            "Aqui está um resumo da sua whitelist:"
        ),
        color=discord.Color.green(),
    )
    dm_embed.set_footer(text="Sistema de Whitelist")

    try:
        await member.send(embed=dm_embed)
        await member.send(embed=summary)
    except discord.Forbidden:
        await channel.send(
            "⚠️ Não consegui enviar DM ao usuário (DMs fechadas).", delete_after=6
        )

    await channel.send(
        embed=discord.Embed(
            title="✅ Whitelist aprovada!",
            description=f"{member.mention} foi notificado no privado. Fechando em 5s...",
            color=discord.Color.green(),
        )
    )
    await asyncio.sleep(5)
    ticket_store.pop(channel.id, None)
    await channel.delete(reason=f"Whitelist aprovada por {ctx.author}")


@aprovar.error
async def aprovar_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão.", delete_after=5)


# ─────────────────────────────────────────────
#  !reprovar <motivo>
# ─────────────────────────────────────────────
@bot.command(name="reprovar")
@commands.has_permissions(manage_channels=True)
async def reprovar(ctx: commands.Context, *, motivo: str = None):
    channel = ctx.channel

    # Motivo obrigatório
    if not motivo:
        await ctx.send(
            "❌ Informe o motivo: `!reprovar <motivo>`\nExemplo: `!reprovar Respostas muito curtas`",
            delete_after=8,
        )
        return

    ticket_data = ticket_store.get(channel.id)

    if not ticket_data:
        await ctx.send(
            "❌ Ticket não encontrado no sistema. A whitelist pode não ter sido concluída ainda.",
            delete_after=8,
        )
        return

    member: discord.Member = ticket_data["member"]
    summary: discord.Embed = ticket_data["summary"]
    await ctx.message.delete()

    dm_embed = discord.Embed(
        title="❌ Whitelist Recusada",
        description=(
            "Infelizmente sua whitelist foi **recusada** pela equipe.\n\n"
            f"**Motivo:** {motivo}\n\n"
            "Aqui está um resumo da sua whitelist:"
        ),
        color=discord.Color.red(),
    )
    dm_embed.set_footer(text="Sistema de Whitelist • Você pode tentar novamente")

    try:
        await member.send(embed=dm_embed)
        await member.send(embed=summary)
    except discord.Forbidden:
        await channel.send(
            "⚠️ Não consegui enviar DM ao usuário (DMs fechadas).", delete_after=6
        )

    await channel.send(
        embed=discord.Embed(
            title="❌ Whitelist recusada",
            description=f"{member.mention} foi notificado no privado. Fechando em 5s...",
            color=discord.Color.red(),
        )
    )
    await asyncio.sleep(5)
    ticket_store.pop(channel.id, None)
    await channel.delete(reason=f"Whitelist reprovada por {ctx.author} — {motivo}")


@reprovar.error
async def reprovar_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão.", delete_after=5)


bot.run(TOKEN)
