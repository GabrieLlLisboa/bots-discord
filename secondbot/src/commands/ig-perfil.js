const {
  SlashCommandBuilder,
  ModalBuilder,
  ActionRowBuilder,
  TextInputBuilder,
  TextInputStyle,
  EmbedBuilder,
} = require('discord.js');
const { getPerfil, savePerfil, getPerfilByUsername } = require('../utils/igDb');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ig-perfil')
    .setDescription('Cria ou edita o seu perfil do Instagram do RP.'),

  async execute(interaction) {
    const perfil = getPerfil(interaction.user.id);

    const modal = new ModalBuilder()
      .setCustomId('ig_modal_perfil')
      .setTitle('📸 Criar Perfil');

    const usernameInput = new TextInputBuilder()
      .setCustomId('ig_username')
      .setLabel('Nome de usuário (sem @)')
      .setStyle(TextInputStyle.Short)
      .setPlaceholder('Ex: joao_silva')
      .setRequired(true)
      .setMaxLength(30)
      .setValue(perfil?.username || '');

    modal.addComponents(
      new ActionRowBuilder().addComponents(usernameInput),
    );

    await interaction.showModal(modal);
  },
};
