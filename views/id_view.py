import discord
from discord.ui import View, Button, Modal, TextInput
import re
import aiohttp
import io


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

        try:
            numero_int = int(numero_raw)
            numero_fmt = f"{numero_int:02d}"
        except ValueError:
            await interaction.followup.send(
                "❌ Número inválido. Use apenas números (ex: 01, 02...).",
                ephemeral=True,
            )
            return

        # Padrão flexível: RG 01, Identidade 01, ID 01, #01, etc.
        pattern = re.compile(
            rf"(?:rg|identidade|id|#)\s*0*{numero_int}\b",
            re.IGNORECASE,
        )

        alvo_msg: discord.Message | None = None
        async for msg in self.canal.history(limit=500):
            # Verifica texto da mensagem
            if pattern.search(msg.content):
                alvo_msg = msg
                break
            # Verifica embeds
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

        # ── Envia no PV ──────────────────────
        try:
            dm = await interaction.user.create_dm()

            # Cabeçalho simples (sem embed)
            await dm.send(f"**🪪 Identidade {numero_fmt}**")

            # Conteúdo de texto da mensagem original
            if alvo_msg.content:
                await dm.send(alvo_msg.content)

            # Conteúdo de embeds (como texto)
            for emb in alvo_msg.embeds:
                partes = []
                if emb.title:
                    partes.append(f"**{emb.title}**")
                if emb.description:
                    partes.append(emb.description)
                for field in emb.fields:
                    partes.append(f"**{field.name}**\n{field.value}")
                if partes:
                    await dm.send("\n".join(partes))

            # Foto(s) anexada(s) à mensagem original — baixa e reencaminha
            fotos_enviadas = 0
            for attachment in alvo_msg.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    file = discord.File(
                                        io.BytesIO(data),
                                        filename=attachment.filename,
                                    )
                                    await dm.send(file=file)
                                    fotos_enviadas += 1
                    except Exception:
                        pass  # Se falhar no download, ignora silenciosamente

            await interaction.followup.send(
                f"✅ A **Identidade {numero_fmt}** foi enviada para o seu privado!"
                + (f" ({fotos_enviadas} foto(s) incluída(s))" if fotos_enviadas else ""),
                ephemeral=True,
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Não consegui te enviar uma DM. Verifique se suas mensagens diretas estão abertas.",
                ephemeral=True,
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        try:
            await interaction.followup.send(
                "❌ Ocorreu um erro ao buscar a identidade.", ephemeral=True
            )
        except Exception:
            pass


class IdView(View):
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
