import discord
from discord.ui import View, Button

from .ticket_flow import run_whitelist_flow

# IDs de cargo da staff — ajuste conforme seu servidor
STAFF_ROLE_NAMES = ["Staff", "Admin", "Moderador", "Whitelist"]


class WhitelistView(View):
    """View persistente com o botão de abrir whitelist."""

    def __init__(self):
        super().__init__(timeout=None)  # Persistente

    @discord.ui.button(
        label="📋 Abrir Whitelist",
        style=discord.ButtonStyle.primary,
        custom_id="open_whitelist",
    )
    async def open_whitelist(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        # Verifica se já existe ticket aberto para este usuário
        existing = discord.utils.get(
            guild.text_channels, name=f"whitelist-{member.name.lower()}"
        )
        if existing:
            await interaction.response.send_message(
                f"❌ Você já possui um ticket aberto: {existing.mention}",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        # --- Permissões do canal ---
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
        }

        # Adicionar acesso à staff
        for role in guild.roles:
            if role.name in STAFF_ROLE_NAMES:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                )

        # Tenta criar em categoria "Tickets" se existir
        category = discord.utils.get(guild.categories, name="Tickets")

        try:
            channel = await guild.create_text_channel(
                name=f"whitelist-{member.name}",
                overwrites=overwrites,
                category=category,
                topic=f"Whitelist de {member.display_name} ({member.id})",
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Não tenho permissão para criar canais. Contate um administrador.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"✅ Seu ticket foi aberto: {channel.mention}", ephemeral=True
        )

        # Inicia o fluxo de whitelist no canal criado
        await run_whitelist_flow(channel, member)
