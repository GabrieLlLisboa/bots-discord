const {
  SlashCommandBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  EmbedBuilder,
  PermissionFlagsBits,
} = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('avaliar-staff')
    .setDescription('Envia o painel de avaliação de staff no canal atual.')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),

  async execute(interaction) {
    const embed = new EmbedBuilder()
      .setTitle('⭐  Avalie nosso Staff')
      .setDescription(
        '> Sua opinião é muito importante para melhorarmos o atendimento!\n> Clique no botão abaixo para enviar sua avaliação.\n\u200b'
      )
      .addFields(
        { name: '📝  Como funciona?', value: 'Preencha o formulário com o nome do staff, uma nota de 1 a 5 e o motivo da avaliação. Você pode escolher ser anônimo ou não.', inline: false }
      )
      .setColor(0xfee75c)
      .setFooter({ text: 'Avaliações falsas ou de má-fé serão removidas.' })
      .setTimestamp();

    const button = new ButtonBuilder()
      .setCustomId('abrir_avaliacao')
      .setLabel('⭐  Avaliar Staff')
      .setStyle(ButtonStyle.Primary);

    const row = new ActionRowBuilder().addComponents(button);

    await interaction.channel.send({ embeds: [embed], components: [row] });
    await interaction.reply({ content: '✅ Painel de avaliação enviado!', ephemeral: true });
  },
};
