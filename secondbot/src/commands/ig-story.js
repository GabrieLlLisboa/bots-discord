const { SlashCommandBuilder, ModalBuilder, ActionRowBuilder, TextInputBuilder, TextInputStyle } = require('discord.js');
const { getPerfil } = require('../utils/igDb');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ig-story')
    .setDescription('Publica um Story (some em 24h).'),

  async execute(interaction) {
    const perfil = getPerfil(interaction.user.id);
    if (!perfil) {
      return interaction.reply({
        content: '❌ Você ainda não tem um perfil! Use **/ig-perfil** para criar.',
        ephemeral: true,
      });
    }

    const modal = new ModalBuilder()
      .setCustomId('ig_modal_story')
      .setTitle('📖 Novo Story');

    const imagemInput = new TextInputBuilder()
      .setCustomId('ig_story_imagem')
      .setLabel('Link da imagem (URL)')
      .setStyle(TextInputStyle.Short)
      .setPlaceholder('https://...')
      .setRequired(true);

    const legendaInput = new TextInputBuilder()
      .setCustomId('ig_story_legenda')
      .setLabel('Legenda do story (opcional)')
      .setStyle(TextInputStyle.Short)
      .setPlaceholder('O que está acontecendo?')
      .setRequired(false)
      .setMaxLength(150);

    modal.addComponents(
      new ActionRowBuilder().addComponents(imagemInput),
      new ActionRowBuilder().addComponents(legendaInput),
    );

    await interaction.showModal(modal);
  },
};
