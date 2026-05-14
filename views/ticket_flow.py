import asyncio
import discord
from utils.roblox import fetch_roblox_user

TIMEOUT = 300  # 5 minutos por pergunta

QUESTIONS = [
    {
        "number": 1,
        "title": "PowerGaming",
        "prompt": "O que é **PowerGaming**?",
        "hint": "Dica: Consulte as regras no canal regras-roleplay.",
    },
    {
        "number": 2,
        "title": "MetaGaming",
        "prompt": "O que é **MetaGaming**?",
        "hint": "Dica: Consulte as regras no canal regras-roleplay.",
    },
    {
        "number": 3,
        "title": "Combat Logging",
        "prompt": "O que é **Combat Logging**?",
        "hint": "Dica: Consulte as regras no canal regras-roleplay.",
    },
    {
        "number": 4,
        "title": "História do Personagem",
        "prompt": "Crie uma **história** para o seu personagem.\n\nSeja criativo! Inclua origem, motivações e eventos importantes da vida dele.",
        "hint": None,
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
            "CPF:\n"
            "Profissão:\n"
            "```"
        ),
        "hint": "Use um CPF fictício, não utilize dados reais.",
    },
]


def build_question_embed(question: dict, current: int, total: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"❓ Pergunta {current}/{total} — {question['title']}",
        description=question["prompt"],
        color=discord.Color.gold(),
    )
    if question["hint"]:
        embed.add_field(name="💡 Dica", value=question["hint"], inline=False)
    embed.set_footer(text=f"⏱️ Você tem {TIMEOUT // 60} minutos para responder.")
    return embed


def build_roblox_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(
        title="🎮 Conta Roblox Encontrada!",
        description=f"Verifique se as informações abaixo são **suas**.",
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


async def ask_question(
    channel: discord.TextChannel,
    member: discord.Member,
    question: dict,
    question_num: int,
    total: int,
) -> str | None:
    """Envia uma pergunta e aguarda a resposta do usuário. Retorna None em timeout."""
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


async def run_whitelist_flow(channel: discord.TextChannel, member: discord.Member):
    """Executa o fluxo completo de whitelist no canal do ticket."""

    # --- Boas-vindas ---
    welcome_embed = discord.Embed(
        title="👋 Bem-vindo à Whitelist!",
       description=(
    f"Olá, {member.mention}!\n\n"
    "Seja bem-vindo, jogador!\n"
    "Para começar sua whitelist, envie seu **nickname do Roblox**.\n\n"
    "Brincadeiras não serão toleradas. Mantenha-se respeitoso."
),
        color=discord.Color.blurple(),
    )
    welcome_embed.set_footer(text="Digite apenas o nickname e aguarde.")
    await channel.send(embed=welcome_embed)

    client = member._state._get_client()

    def check_member(m: discord.Message):
        return m.author == member and m.channel == channel

    # --- Coleta nickname Roblox ---
    roblox_data = None
    attempts = 0
    while attempts < 3:
        try:
            msg = await client.wait_for("message", check=check_member, timeout=TIMEOUT)
            nickname = msg.content.strip()
        except asyncio.TimeoutError:
            await channel.send(
                embed=discord.Embed(
                    title="⏰ Tempo esgotado",
                    description="Você demorou muito para responder. O ticket será fechado em 10 segundos.",
                    color=discord.Color.red(),
                )
            )
            await asyncio.sleep(10)
            await channel.delete(reason="Timeout na whitelist")
            return

        loading = await channel.send(
            embed=discord.Embed(
                description=f"🔍 Buscando conta Roblox: **{nickname}**...",
                color=discord.Color.light_grey(),
            )
        )

        roblox_data = await fetch_roblox_user(nickname)

        if roblox_data:
            await loading.delete()
            await channel.send(embed=build_roblox_embed(roblox_data))
            break
        else:
            attempts += 1
            await loading.edit(
                embed=discord.Embed(
                    title="❌ Conta não encontrada",
                    description=(
                        f"Nenhuma conta Roblox foi encontrada com o nickname **{nickname}**.\n"
                        f"Verifique o nome e tente novamente. ({attempts}/3 tentativas)"
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

    # Pequena pausa antes de começar as perguntas
    await asyncio.sleep(2)

    start_embed = discord.Embed(
        title="📝 Iniciando Perguntas da Whitelist",
        description=(
            "Ótimo! Agora responda as perguntas abaixo **uma de cada vez**.\n"
            f"Você tem **{TIMEOUT // 60} minutos** para responder cada uma."
        ),
        color=discord.Color.blurple(),
    )
    await channel.send(embed=start_embed)
    await asyncio.sleep(1)

    # --- Perguntas ---
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

        # Confirmação visual de resposta recebida
        confirm_embed = discord.Embed(
            description=f"✅ Resposta recebida! Continuando...",
            color=discord.Color.green(),
        )
        confirm_msg = await channel.send(embed=confirm_embed)
        await asyncio.sleep(1.5)
        await confirm_msg.delete()

    # --- Embed de resumo das respostas (visível para staff) ---
    summary_embed = discord.Embed(
        title="📋 Resumo da Whitelist",
        description=f"Respostas de {member.mention} (`{member.id}`)",
        color=discord.Color.purple(),
    )
    if roblox_data:
        summary_embed.add_field(
            name="🎮 Roblox",
            value=(
                f"**Username:** {roblox_data['username']}\n"
                f"**ID:** {roblox_data['id']}\n"
                f"**Criado em:** {roblox_data['created']}"
            ),
            inline=False,
        )
    for title, answer in answers.items():
        # Trunca respostas longas no embed (limite de 1024 chars por field)
        value = answer[:1000] + "..." if len(answer) > 1000 else answer
        summary_embed.add_field(name=f"❓ {title}", value=value, inline=False)
    summary_embed.set_footer(text="Análise pendente pela staff")

    await channel.send(embed=summary_embed)

    # --- Embed final para o usuário ---
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
