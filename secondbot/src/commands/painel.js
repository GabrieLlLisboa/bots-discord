const { SlashCommandBuilder, ActionRowBuilder, StringSelectMenuBuilder, PermissionFlagsBits } = require('discord.js');
const { buildPanelEmbed, TICKET_CATEGORIES } = require('../utils/ticketConfig');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('painel')
    .setDescription('Envia o painel de tíquetes no canal atual.')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),

  async execute(interaction) {
    const embed = buildPanelEmbed();

    const selectMenu = new StringSelectMenuBuilder()
      .setCustomId('ticket_select')
      .setPlaceholder('📋  Selecione uma categoria...')
      .addOptions(
        TICKET_CATEGORIES.map(cat => ({
          label: cat.label,
          description: cat.description,
          value: cat.id,
          emoji: cat.emoji,
        }))
      );

    const row = new ActionRowBuilder().addComponents(selectMenu);

    await interaction.channel.send({ embeds: [embed], components: [row] });
    await interaction.reply({ content: '✅ Painel enviado!', ephemeral: true });
  },
};
