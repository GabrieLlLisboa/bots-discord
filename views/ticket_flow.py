import asyncio
import discord
from discord.ui import View, Button, Select
from utils.roblox import fetch_roblox_user

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


# ─────────────────────────────────────────────
#  View: botão de confirmar conta Roblox
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
#  View: enquete de nickname via Select
# ─────────────────────────────────────────────
class NicknameSelectView(View):
    def __init__(self, member: discord.Member, options: list[discord.SelectOption]):
        super().__init__(timeout=TIMEOUT)
        self.member = member
        self.chosen: str | None = None
        select = Select(
            placeholder="Escolha como quer aparecer no servidor...",
            options=options,
        )
        select.callback = self._callback
        self.add_item(select)

    async def _callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message("❌ Isso não é para você.", ephemeral=True)
            return
        self.chosen = interaction.data["values"][0]
        self.stop()
        await interaction.response.defer()


# ─────────────────────────────────────────────
#  Helpers de embed
# ─────────────────────────────────────────────
def build_question_embed(question: dict, current: int, total: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"📋 Sistema de Whitelist — Pergunta {current}/{total}",
        description=f"**{question['title']}**\n\n{question['prompt']}",
        color=discord.Color.gold(),
    )
    embed.set_footer(text=f"⏱️ Você tem {TIMEOUT // 60} minutos para responder.")
    return embed


def build_roblox_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(
        title="🎮 Conta Roblox Encontrada!",
        description="Verifique se as informações abaixo são **suas**.",
        color=discord.Color.green(),
        url=data["profile_link"],
    )
    embed.add_field(name="👤 Username", value=data["username"], inline=True)
    embed.add_field(name="🏷️ Display Name", value=data["display_name"], inline=True)
    embed.add_field(name="🆔 ID", value=str(data["id"]), inline=True)
    embed.add_field(name="📅 Conta criada em", value=data["created"], inline=True)
    embed.add_field(
        name="🔗 Perfil",
        value=f"[Clique aqui]({data['profile_link']})",
        inline=True,
    )
    if data["avatar_url"]:
        embed.set_thumbnail(url=data["avatar_url"])
    embed.set_footer(text="Roblox API • Dados públicos")
    return embed


# ─────────────────────────────────────────────
#  Pergunta simples (aguarda msg do usuário)
# ─────────────────────────────────────────────
async def ask_question(
    channel: discord.TextChannel,
    member: discord.Member,
    question: dict,
    question_num: int,
    total: int,
) -> str | None:
    embed = build_question_embed(question, question_num, total)
    await channel.send(embed=embed)

    def check(m: discord.Message):
        return m.author == member and m.channel == channel

    try:
        msg = await member._state._get_client().wait_for(
            "message", check=check, timeout=TIMEOUT
        )
        return msg.content
    except asyncio.TimeoutError:
        return None


# ─────────────────────────────────────────────
#  Helper: fechar por timeout
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
    await channel.delete(reason="Timeout na whitelist")


# ─────────────────────────────────────────────
#  Fluxo principal
# ─────────────────────────────────────────────
async def run_whitelist_flow(channel: discord.TextChannel, member: discord.Member):
    client = member._state._get_client()

    # ── Boas-vindas ──────────────────────────
    welcome_embed = discord.Embed(
        title="📋 Sistema de Whitelist",
        description=(
            f"Olá, {member.mention}!\n\n"
            "Seja bem-vindo jogador! Para começar sua whitelist, envie seu **nickname do Roblox**."
        ),
        color=discord.Color.blurple(),
    )
    welcome_embed.set_footer(text="Digite apenas o nickname e aguarde.")
    await channel.send(embed=welcome_embed)

    def check_member(m: discord.Message):
        return m.author == member and m.channel == channel

    # ── Coleta nickname + confirma conta ─────
    roblox_data = None
    attempts = 0

    while attempts < 3:
        # Aguarda o usuário digitar o nickname
        try:
            msg = await client.wait_for("message", check=check_member, timeout=TIMEOUT)
            nickname = msg.content.strip()
        except asyncio.TimeoutError:
            await _timeout_close(channel)
            return

        loading = await channel.send(
            embed=discord.Embed(
                description=f"🔍 Buscando conta Roblox: **{nickname}**...",
                color=discord.Color.light_grey(),
            )
        )

        roblox_data = await fetch_roblox_user(nickname)

        if not roblox_data:
            attempts += 1
            await loading.edit(
                embed=discord.Embed(
                    title="❌ Conta não encontrada",
                    description=(
                        f"Nenhuma conta Roblox encontrada com o nickname **{nickname}**.\n"
                        f"Verifique o nome e tente novamente. ({attempts}/3)"
                    ),
                    color=discord.Color.red(),
                )
            )
            if attempts >= 3:
                await channel.send(
                    embed=discord.Embed(
                        title="🚫 Limite de tentativas atingido",
                        description="O ticket será fechado. Entre em contato com a staff.",
                        color=discord.Color.dark_red(),
                    )
                )
                await asyncio.sleep(10)
                await channel.delete(reason="Limite de tentativas Roblox")
                return
            continue  # pede o nickname de novo

        # Conta encontrada — mostra embed + botões de confirmar
        await loading.delete()
        confirm_view = ConfirmRobloxView(member)
        await channel.send(embed=build_roblox_embed(roblox_data), view=confirm_view)
        await confirm_view.wait()

        if confirm_view.confirmed is True:
            break  # segue para a enquete de nickname

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
            await channel.send(
                embed=discord.Embed(
                    description=f"Tudo bem! Envie o nickname correto. ({attempts}/3)",
                    color=discord.Color.orange(),
                )
            )

        else:
            # Timeout no botão
            await _timeout_close(channel)
            return

    # ── Enquete de nickname ───────────────────
    roblox_name = roblox_data["username"]
    display_name = roblox_data["display_name"]
    discord_name = member.name

    opt1 = roblox_name
    opt2 = f"{roblox_name} ({discord_name})"
    opt3 = f"{display_name} ({roblox_name})"

    options = [
        discord.SelectOption(label=opt1, value=opt1, emoji="1️⃣"),
        discord.SelectOption(label=opt2, value=opt2, emoji="2️⃣"),
        discord.SelectOption(label=opt3, value=opt3, emoji="3️⃣"),
    ]

    poll_embed = discord.Embed(
        title="🏷️ Como você quer aparecer no servidor?",
        description=(
            f"**1️⃣** `{opt1}`\n"
            f"**2️⃣** `{opt2}`\n"
            f"**3️⃣** `{opt3}`\n\n"
            "Selecione uma opção no menu abaixo."
        ),
        color=discord.Color.blurple(),
    )
    poll_embed.set_footer(text=f"⏱️ Você tem {TIMEOUT // 60} minutos para escolher.")

    nick_view = NicknameSelectView(member, options)
    await channel.send(embed=poll_embed, view=nick_view)
    await nick_view.wait()

    if nick_view.chosen is None:
        await _timeout_close(channel)
        return

    chosen_nick = nick_view.chosen

    # Renomeia o membro no servidor
    try:
        await member.edit(nick=chosen_nick)
    except discord.Forbidden:
        pass  # Bot sem permissão (ex: dono do servidor)

    confirm_nick = await channel.send(
        embed=discord.Embed(
            description=f"✅ Nickname definido para **{chosen_nick}**! Continuando...",
            color=discord.Color.green(),
        )
    )
    await asyncio.sleep(2)
    await confirm_nick.delete()

    # ── Início das perguntas ──────────────────
    start_embed = discord.Embed(
        title="📋 Sistema de Whitelist — Perguntas",
        description=(
            "Ótimo! Agora responda as perguntas abaixo **uma de cada vez**.\n"
            f"Você tem **{TIMEOUT // 60} minutos** para responder cada uma."
        ),
        color=discord.Color.blurple(),
    )
    await channel.send(embed=start_embed)
    await asyncio.sleep(1)

    answers = {}
    total = len(QUESTIONS)

    for question in QUESTIONS:
        response = await ask_question(
            channel, member, question, question["number"], total
        )

        if response is None:
            await channel.send(
                embed=discord.Embed(
                    title="⏰ Tempo esgotado",
                    description="Você demorou para responder. O ticket será encerrado.",
                    color=discord.Color.red(),
                )
            )
            await asyncio.sleep(10)
            await channel.delete(reason="Timeout nas perguntas da whitelist")
            return

        answers[question["title"]] = response

        confirm_msg = await channel.send(
            embed=discord.Embed(
                description="✅ Resposta recebida! Continuando...",
                color=discord.Color.green(),
            )
        )
        await asyncio.sleep(1.5)
        await confirm_msg.delete()

    # ── Resumo para a staff ───────────────────
    summary_embed = discord.Embed(
        title="📋 Sistema de Whitelist — Resumo",
        description=f"Respostas de {member.mention} (`{member.id}`)",
        color=discord.Color.purple(),
    )
    summary_embed.add_field(
        name="🏷️ Nickname escolhido",
        value=f"`{chosen_nick}`",
        inline=False,
    )
    if roblox_data:
        summary_embed.add_field(
            name="🎮 Roblox",
            value=(
                f"**Username:** {roblox_data['username']}\n"
                f"**Display Name:** {roblox_data['display_name']}\n"
                f"**ID:** {roblox_data['id']}\n"
                f"**Criado em:** {roblox_data['created']}"
            ),
            inline=False,
        )
    for title, answer in answers.items():
        value = answer[:1000] + "..." if len(answer) > 1000 else answer
        summary_embed.add_field(name=f"❓ {title}", value=value, inline=False)
    summary_embed.set_footer(text="Análise pendente pela staff")
    await channel.send(embed=summary_embed)

    # ── Mensagem final ────────────────────────
    final_embed = discord.Embed(
        title="✅ Whitelist Concluída!",
        description=(
            f"{member.mention}, sua whitelist foi enviada com sucesso!\n\n"
            "**✅ Sua whitelist foi concluída! Aguarde a equipe analisar suas respostas.**\n\n"
            "Nossa equipe irá avaliar suas respostas em breve. "
            "Fique de olho nas notificações do servidor!"
        ),
        color=discord.Color.green(),
    )
    final_embed.set_footer(text="Sistema de Whitelist • Obrigado pela participação!")
    if roblox_data and roblox_data["avatar_url"]:
        final_embed.set_thumbnail(url=roblox_data["avatar_url"])
    await channel.send(embed=final_embed)
