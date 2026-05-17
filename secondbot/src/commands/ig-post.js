const { SlashCommandBuilder } = require('discord.js');
const { getPerfil } = require('../utils/igDb');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ig-post')
    .setDescription('Como publicar no feed do Instagram do RP.'),

  async execute(interaction) {
    const perfil = getPerfil(interaction.user.id);
    if (!perfil) {
      return interaction.reply({
        content: '❌ Você ainda não tem um perfil! Use **/ig-perfil** para criar.',
        ephemeral: true,
      });
    }

    const feedChannelId = process.env.IG_FEED_CHANNEL_ID;
    const feedChannel   = feedChannelId
      ? interaction.guild.channels.cache.get(feedChannelId)
      : null;

    const mencaoCanal = feedChannel ? ` em ${feedChannel}` : ' no canal do feed';

    return interaction.reply({
      content:
        `📸 **Como postar, @${perfil.username}:**\n\n` +
        `Vá${mencaoCanal} e envie sua mensagem normalmente!\n\n` +
        `> • Só texto → vira legenda do post\n` +
        `> • Imagem anexada → vira foto do post\n` +
        `> • Imagem + texto → foto com legenda\n\n` +
        `O bot vai transformar sua mensagem em post automaticamente. ✅`,
      ephemeral: true,
    });
  },
};
