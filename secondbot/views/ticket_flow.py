import asyncio
import discord
from discord.ui import View, Button
from utils.roblox import fetch_roblox_user
from utils.ticket_store import ticket_store
from utils import nick_store

TIMEOUT = 300  # 5 minutos por pergunta

QUESTIONS = [
    {
        "number": 1,
        "title": "PowerGaming",
        "prompt": "O que é **PowerGaming**?",
    },
    {
        "number": 2,
        "title": "MetaGaming",
        "prompt": "O que é **MetaGaming**?",
    },
    {
        "number": 3,
        "title": "Combat Logging",
        "prompt": "O que é **Combat Logging**?",
    },
    {
        "number": 4,
        "title": "História do Personagem",
        "prompt": "Crie uma **história** para o seu personagem.\n\nSeja criativo! Inclua origem, motivações e eventos importantes da vida dele.",
    },
    {
        "number": 5,
        "title": "Identidade do Personagem",
        "prompt": (
            "Preencha a **identidade** do seu personagem com os campos abaixo:\n\n"
            "```\n"
            "Nome:\n"
            "Nascimento:\n"
            "Idade:\n"
            "CEP em que nasceu:\n"
            "CPF (fake):\n"
            "Profissão:\n"
            "```"
        ),
    },
]


def build_question_embed(question: dict, current: int, total: int) -> discord.Embed:
    return discord.Embed(
        title=f"📋 Sistema de Whitelist — Pergunta {current}/{total}",
        description=f"**{question['title']}**\n\n{question['prompt']}",
        color=discord.Color.gold(),
    )


# ─────────────────────────────────────────────
#  View: confirmar conta Roblox
# ─────────────────────────────────────────────
class ConfirmRobloxView(View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=TIMEOUT)
        self.member = member
        self.confirmed: bool | None = None

    @discord.ui.button(label="✅ Confirmar conta", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message("❌ Isso não é para você.", ephemeral=True)
            return
        self.confirmed = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="❌ Não é minha conta", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message("❌ Isso não é para você.", ephemeral=True)
            return
        self.confirmed = False
        self.stop()
        await interaction.response.defer()


# ─────────────────────────────────────────────
#  Embeds reutilizáveis
# ─────────────────────────────────────────────
def build_roblox_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(
        title="🎮 Conta Roblox",
        color=discord.Color.green(),
        url=data["profile_link"],
    )
    embed.add_field(name="👤 Username", value=data["username"], inline=True)
    embed.add_field(name="🏷️ Display Name", value=data["display_name"], inline=True)
    embed.add_field(name="🆔 ID", value=str(data["id"]), inline=True)
    embed.add_field(name="📅 Conta criada em", value=data["created"], inline=True)
    embed.add_field(name="🔗 Perfil", value=f"[Clique aqui]({data['profile_link']})", inline=True)
    if data["avatar_url"]:
        embed.set_thumbnail(url=data["avatar_url"])
    return embed


def build_summary_embed(
    member: discord.Member,
    chosen_nick: str,
    roblox_data: dict,
    answers: dict,
) -> discord.Embed:
    summary = discord.Embed(
        title="📋 Resumo da Whitelist",
        description=f"{member.mention} • `{member.id}`",
        color=discord.Color.purple(),
    )
    summary.add_field(name="🏷️ Nickname escolhido", value=f"`{chosen_nick}`", inline=False)
    for title, answer in answers.items():
        value = answer[:1000] + "..." if len(answer) > 1000 else answer
        summary.add_field(name=f"❓ {title}", value=value, inline=False)
    summary.set_footer(text="Use !aprovar ou !reprovar <motivo>")
    return summary


# ─────────────────────────────────────────────
#  Pergunta — aguarda resposta e limpa o canal
# ─────────────────────────────────────────────
async def ask_question(
    channel: discord.TextChannel,
    member: discord.Member,
    question: dict,
    question_num: int,
    total: int,
) -> str | None:
    question_msg = await channel.send(embed=build_question_embed(question, question_num, total))

    def check(m: discord.Message):
        return m.author == member and m.channel == channel

    try:
        reply = await member._state._get_client().wait_for(
            "message", check=check, timeout=TIMEOUT
        )
    except asyncio.TimeoutError:
        return None

    text = reply.content
    try:
        await question_msg.delete()
        await reply.delete()
    except (discord.NotFound, discord.Forbidden):
        pass
    return text


# ─────────────────────────────────────────────
#  Timeout
# ─────────────────────────────────────────────
async def _timeout_close(channel: discord.TextChannel):
    await channel.send(
        embed=discord.Embed(
            title="⏰ Tempo esgotado",
            description="Você demorou muito para responder. O ticket será fechado em 10 segundos.",
            color=discord.Color.red(),
        )
    )
    await asyncio.sleep(10)
    ticket_store.pop(channel.id, None)
    await channel.delete(reason="Timeout na whitelist")


# ─────────────────────────────────────────────
#  Fluxo principal
# ─────────────────────────────────────────────
async def run_whitelist_flow(channel: discord.TextChannel, member: discord.Member):
    client = member._state._get_client()
    temp_msgs: list[discord.Message] = []

    # ── Boas-vindas ───────────────────────────
    welcome = await channel.send(
        embed=discord.Embed(
            title="📋 Sistema de Whitelist",
            description=(
                f"Olá, {member.mention}!\n\n"
                "Seja bem-vindo jogador! Para começar sua whitelist, envie seu **nickname do Roblox**."
            ),
            color=discord.Color.blurple(),
        )
    )
    temp_msgs.append(welcome)

    def check_member(m: discord.Message):
        return m.author == member and m.channel == channel

    # ── Coleta nickname + confirma conta ─────
    roblox_data = None
    attempts = 0

    while attempts < 3:
        try:
            msg = await client.wait_for("message", check=check_member, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            await _timeout_close(channel)
            return

        temp_msgs.append(msg)

        loading = await channel.send(
            embed=discord.Embed(
                description=f"🔍 Buscando conta Roblox: **{msg.content.strip()}**...",
                color=discord.Color.light_grey(),
            )
        )
        temp_msgs.append(loading)

        roblox_data = await fetch_roblox_user(msg.content.strip())

        if not roblox_data:
            attempts += 1
            await loading.edit(
                embed=discord.Embed(
                    title="❌ Conta não encontrada",
                    description=(
                        f"Nenhuma conta encontrada com **{msg.content.strip()}**.\n"
                        f"Tente novamente. ({attempts}/3)"
                    ),
                    color=discord.Color.red(),
                )
            )
            if attempts >= 3:
                await channel.send(
                    embed=discord.Embed(
                        title="🚫 Limite de tentativas atingido",
                        description="O ticket será fechado em 10 segundos.",
                        color=discord.Color.dark_red(),
                    )
                )
                await asyncio.sleep(10)
                await channel.delete(reason="Limite de tentativas Roblox")
                return
            continue

        await loading.delete()
        temp_msgs.remove(loading)

        confirm_view = ConfirmRobloxView(member)
        roblox_confirm_msg = await channel.send(embed=build_roblox_embed(roblox_data), view=confirm_view)
        temp_msgs.append(roblox_confirm_msg)
        await confirm_view.wait()

        if confirm_view.confirmed is True:
            break

        elif confirm_view.confirmed is False:
            attempts += 1
            roblox_data = None
            if attempts >= 3:
                await channel.send(
                    embed=discord.Embed(
                        description="🚫 Limite de tentativas atingido. O ticket será fechado.",
                        color=discord.Color.dark_red(),
                    )
                )
                await asyncio.sleep(10)
                await channel.delete(reason="Limite de tentativas Roblox")
                return
            retry = await channel.send(
                embed=discord.Embed(
                    description=f"Tudo bem! Envie o nickname correto. ({attempts}/3)",
                    color=discord.Color.orange(),
                )
            )
            temp_msgs.append(retry)
        else:
            await _timeout_close(channel)
            return

    # ── Define nickname automático ───────────
    # Formato: "DisplayName (username)" ou só "username" se não tiver display name diferente
    roblox_username = roblox_data["username"]
    roblox_display = roblox_data["display_name"]

    if roblox_display and roblox_display.lower() != roblox_username.lower():
        chosen_nick = f"{roblox_display} ({roblox_username})"
    else:
        chosen_nick = roblox_username

    try:
        await member.edit(nick=chosen_nick)
    except discord.Forbidden:
        pass

    # Registra o nick correto para monitoramento (persiste em JSON)
    nick_store.set(member.id, chosen_nick)

    # ── Perguntas com timer ───────────────────
    answers = {}
    total = len(QUESTIONS)

    for question in QUESTIONS:
        response = await ask_question(channel, member, question, question["number"], total)

        if response is None:
            await channel.send(
                embed=discord.Embed(
                    title="⏰ Tempo esgotado",
                    description="Você demorou para responder. O ticket será encerrado.",
                    color=discord.Color.red(),
                )
            )
            await asyncio.sleep(10)
            ticket_store.pop(channel.id, None)
            await channel.delete(reason="Timeout nas perguntas da whitelist")
            return

        answers[question["title"]] = response

    # ── Limpa TODO o canal ────────────────────
    try:
        await channel.purge(limit=500)
    except (discord.Forbidden, discord.HTTPException):
        # Fallback: apaga mensagem por mensagem
        for m in temp_msgs:
            try:
                await m.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

    # ── Canal final: conta Roblox + resumo ────
    await channel.send(embed=build_roblox_embed(roblox_data))

    summary_embed = build_summary_embed(member, chosen_nick, roblox_data, answers)
    await channel.send(embed=summary_embed)

    # Salva para !aprovar / !reprovar
    ticket_store[channel.id] = {
        "member": member,
        "summary": summary_embed,
        "roblox_data": roblox_data,
    }

    # ── Notifica o usuário no PV ──────────────
    final_embed = discord.Embed(
        title="✅ Whitelist Enviada!",
        description=(
            "Sua whitelist foi enviada com sucesso!\n\n"
            "**Aguarde a equipe analisar suas respostas.**\n\n"
            "Você será notificado por aqui quando a análise for concluída."
        ),
        color=discord.Color.green(),
    )
    final_embed.set_footer(text="Sistema de Whitelist • Obrigado pela participação!")
    if roblox_data["avatar_url"]:
        final_embed.set_thumbnail(url=roblox_data["avatar_url"])

    try:
        await member.send(embed=final_embed)
    except discord.Forbidden:
        fallback = await channel.send(content=member.mention, embed=final_embed)
        await asyncio.sleep(15)
        try:
            await fallback.delete()
        except discord.NotFound:
            pass
