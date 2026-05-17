import discord
from discord.ui import View, Button, Modal, TextInput
import re


class BuscarIdModal(Modal, title="🔍 Buscar Identidade"):
    numero = TextInput(
        label="Número da Identidade",
        placeholder="Ex: 01, 02, 15...",
        min_length=1,
        max_length=4,
        required=True,
    )

    def __init__(self, canal: discord.TextChannel):
        super().__init__()
        self.canal = canal

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        numero_raw = self.numero.value.strip()

        # Normaliza para formato com zero à esquerda (ex: "2" → "02")
        try:
            numero_int = int(numero_raw)
            numero_fmt = f"{numero_int:02d}"
        except ValueError:
            await interaction.followup.send(
                "❌ Número inválido. Use apenas números (ex: 01, 02...).",
                ephemeral=True,
            )
            return

        # Padrão flexível: aceita "RG 01", "Identidade 01", "ID 01", "#01", etc.
        # Qualquer palavra/prefixo seguido do número (com ou sem zero à esquerda)
        pattern = re.compile(
            rf"(?:rg|identidade|id|#)\s*0*{numero_int}\b",
            re.IGNORECASE,
        )

        alvo_msg = None
        async for msg in self.canal.history(limit=500):
            # Verifica no conteúdo de texto da mensagem
            if pattern.search(msg.content):
                alvo_msg = msg
                break
            # Verifica também nos embeds
            for embed in msg.embeds:
                texto = " ".join(filter(None, [
                    embed.title,
                    embed.description,
                    *(f.name + " " + f.value for f in embed.fields),
                ]))
                if pattern.search(texto):
                    alvo_msg = msg
                    break
            if alvo_msg:
                break

        if not alvo_msg:
            await interaction.followup.send(
                f"❌ Identidade **{numero_fmt}** não encontrada neste canal.",
                ephemeral=True,
            )
            return

        # Envia a mensagem encontrada no DM do usuário
        try:
            dm = await interaction.user.create_dm()

            header = discord.Embed(
                title=f"🪪 Identidade {numero_fmt} encontrada!",
                description=f"Aqui está o registro da **Identidade {numero_fmt}**:",
                color=discord.Color.dark_gold(),
            )
            await dm.send(embed=header)

            # Encaminha embeds da mensagem original, se houver
            if alvo_msg.embeds:
                for emb in alvo_msg.embeds:
                    await dm.send(embed=emb)
            # Encaminha conteúdo de texto, se houver
            if alvo_msg.content:
                content_embed = discord.Embed(
                    description=alvo_msg.content,
                    color=discord.Color.gold(),
                )
                content_embed.set_footer(
                    text=f"Enviado por {alvo_msg.author.display_name}",
                )
                await dm.send(embed=content_embed)

            await interaction.followup.send(
                f"✅ A **Identidade {numero_fmt}** foi enviada para o seu privado!",
                ephemeral=True,
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Não consegui te enviar uma DM. Verifique se suas mensagens diretas estão abertas.",
                ephemeral=True,
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.followup.send(
            "❌ Ocorreu um erro ao buscar a identidade.", ephemeral=True
        )


class IdView(View):
    """View persistente com o botão de busca de ID."""

    def __init__(self, canal: discord.TextChannel):
        super().__init__(timeout=None)
        self.canal = canal
        self.message_id: int | None = None

    @discord.ui.button(
        label="🔍 Procurar por ID",
        style=discord.ButtonStyle.secondary,
        custom_id="buscar_id",
    )
    async def buscar_id(self, interaction: discord.Interaction, button: Button):
        modal = BuscarIdModal(self.canal)
        await interaction.response.send_modal(modal)
