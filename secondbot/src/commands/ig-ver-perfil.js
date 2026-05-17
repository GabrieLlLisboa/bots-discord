const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const { getPerfil, getPerfilByUsername, getFollowData, getAllPosts, isFollowing } = require('../utils/igDb');
const { buildPerfilEmbed } = require('../utils/igEmbeds');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ig-ver-perfil')
    .setDescription('Veja o perfil de um usuário do Instagram do RP.')
    .addStringOption(opt =>
      opt.setName('usuario')
        .setDescription('Nome de usuário (sem @). Deixe vazio para ver o seu próprio.')
        .setRequired(false)
    ),

  async execute(interaction) {
    const usernameArg = interaction.options.getString('usuario');
    let perfil;

    if (usernameArg) {
      perfil = getPerfilByUsername(usernameArg.replace('@', ''));
      if (!perfil) {
        return interaction.reply({
          content: `❌ Perfil **@${usernameArg}** não encontrado.`,
          ephemeral: true,
        });
      }
    } else {
      perfil = getPerfil(interaction.user.id);
      if (!perfil) {
        return interaction.reply({
          content: '❌ Você ainda não tem um perfil! Use **/ig-perfil** para criar.',
          ephemeral: true,
        });
      }
    }

    const followData = getFollowData(perfil.userId);
    const posts      = Object.values(getAllPosts()).filter(p => p.autorId === perfil.userId);
    const embed      = buildPerfilEmbed(perfil, followData, posts.length);

    // Botão de seguir/deixar de seguir (só aparece se não for o próprio perfil)
    const components = [];
    if (perfil.userId !== interaction.user.id) {
      const jaSegue = isFollowing(interaction.user.id, perfil.userId);
      const followBtn = new ButtonBuilder()
        .setCustomId(`ig_follow_${perfil.userId}`)
        .setLabel(jaSegue ? '➖ Deixar de Seguir' : '➕ Seguir')
        .setStyle(jaSegue ? ButtonStyle.Secondary : ButtonStyle.Primary);

      components.push(new ActionRowBuilder().addComponents(followBtn));
    }

    await interaction.reply({ embeds: [embed], components, ephemeral: false });
  },
};
