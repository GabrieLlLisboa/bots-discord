const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('adicionar')
    .setDescription('Adiciona um usuário ao tíquete atual.')
    .addUserOption(option =>
      option.setName('usuario').setDescription('Usuário para adicionar').setRequired(true)
    )
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),

  async execute(interaction) {
    const channel = interaction.channel;

    if (!channel.name.startsWith('ticket-')) {
      return interaction.reply({
        content: '❌ Este comando só pode ser usado dentro de um canal de tíquete.',
        ephemeral: true,
      });
    }

    const user = interaction.options.getUser('usuario');

    await channel.permissionOverwrites.create(user, {
      ViewChannel: true,
      SendMessages: true,
      ReadMessageHistory: true,
    });

    await interaction.reply({ content: `✅ ${user} foi adicionado ao tíquete.` });
  },
};
