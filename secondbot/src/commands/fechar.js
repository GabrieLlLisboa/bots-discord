const { SlashCommandBuilder, PermissionFlagsBits, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('fechar')
    .setDescription('Fecha e deleta o tíquete atual.')
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),

  async execute(interaction) {
    const channel = interaction.channel;

    // Verifica se o canal é realmente um tíquete
    if (!channel.name.startsWith('ticket-')) {
      return interaction.reply({
        content: '❌ Este comando só pode ser usado dentro de um canal de tíquete.',
        ephemeral: true,
      });
    }

    // Envia log se LOG_CHANNEL_ID estiver configurado
    if (process.env.LOG_CHANNEL_ID) {
      const logChannel = interaction.guild.channels.cache.get(process.env.LOG_CHANNEL_ID);
      if (logChannel) {
        const logEmbed = new EmbedBuilder()
          .setTitle('🗑️  Tíquete Fechado')
          .addFields(
            { name: 'Canal', value: channel.name, inline: true },
            { name: 'Fechado por', value: `${interaction.user.tag}`, inline: true },
            { name: 'Data', value: `<t:${Math.floor(Date.now() / 1000)}:F>`, inline: true }
          )
          .setColor(0xed4245)
          .setTimestamp();

        await logChannel.send({ embeds: [logEmbed] });
      }
    }

    await interaction.reply({ content: '🗑️ Fechando o tíquete em **3 segundos**...' });

    setTimeout(async () => {
      try {
        await channel.delete();
      } catch (err) {
        console.error('Erro ao deletar canal:', err);
      }
    }, 3000);
  },
};
