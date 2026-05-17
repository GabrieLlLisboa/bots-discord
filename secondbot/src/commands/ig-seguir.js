const { SlashCommandBuilder } = require('discord.js');
const { getPerfil, getPerfilByUsername, follow, unfollow, isFollowing } = require('../utils/igDb');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ig-seguir')
    .setDescription('Segue ou deixa de seguir um perfil do Instagram do RP.')
    .addStringOption(opt =>
      opt.setName('usuario')
        .setDescription('Nome de usuário (sem @)')
        .setRequired(true)
    ),

  async execute(interaction) {
    const meuPerfil = getPerfil(interaction.user.id);
    if (!meuPerfil) {
      return interaction.reply({
        content: '❌ Você ainda não tem um perfil! Use **/ig-perfil** para criar.',
        ephemeral: true,
      });
    }

    const usernameAlvo = interaction.options.getString('usuario').replace('@', '');
    const perfilAlvo   = getPerfilByUsername(usernameAlvo);

    if (!perfilAlvo) {
      return interaction.reply({
        content: `❌ Perfil **@${usernameAlvo}** não encontrado.`,
        ephemeral: true,
      });
    }

    if (perfilAlvo.userId === interaction.user.id) {
      return interaction.reply({ content: '❌ Você não pode se seguir.', ephemeral: true });
    }

    if (isFollowing(interaction.user.id, perfilAlvo.userId)) {
      unfollow(interaction.user.id, perfilAlvo.userId);
      return interaction.reply({
        content: `✅ Você deixou de seguir **@${perfilAlvo.username}**.`,
        ephemeral: true,
      });
    } else {
      follow(interaction.user.id, perfilAlvo.userId);
      return interaction.reply({
        content: `✅ Você começou a seguir **@${perfilAlvo.username}**!`,
        ephemeral: true,
      });
    }
  },
};
