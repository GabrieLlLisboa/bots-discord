const { SlashCommandBuilder } = require('discord.js');
const { getAllStories, getPerfil, deleteStory } = require('../utils/igDb');
const { buildStoryEmbed } = require('../utils/igEmbeds');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ig-stories')
    .setDescription('Veja os stories ativos do servidor.'),

  async execute(interaction) {
    await interaction.deferReply();

    const todos  = getAllStories();
    const agora  = Date.now();
    const ativos = [];

    for (const [id, story] of Object.entries(todos)) {
      const criado = new Date(story.criadoEm).getTime();
      if (agora - criado > 24 * 60 * 60 * 1000) {
        deleteStory(id); // limpa expirados
        continue;
      }
      ativos.push({ id, ...story });
    }

    if (ativos.length === 0) {
      return interaction.editReply('📭 Nenhum story ativo no momento.');
    }

    const embeds = [];
    for (const story of ativos.slice(0, 10)) {
      const perfil = getPerfil(story.autorId);
      if (!perfil) continue;
      embeds.push(buildStoryEmbed(story, perfil));
    }

    await interaction.editReply({
      content: `📖 **${ativos.length} story(s) ativo(s):**`,
      embeds,
    });
  },
};
