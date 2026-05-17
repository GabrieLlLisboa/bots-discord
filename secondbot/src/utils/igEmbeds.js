const { EmbedBuilder } = require('discord.js');

function starsToHearts(n) {
  return n > 0 ? `❤️ **${n}**` : '🤍 0';
}

// ── Post embed ───────────────────────────────────────────────
function buildPostEmbed(post, perfil) {
  const embed = new EmbedBuilder()
    .setAuthor({
      name: `@${perfil.username}${perfil.verificado ? '  ✅' : ''}`,
      iconURL: perfil.fotoPerfil || null,
    })
    .setDescription(post.legenda || null)
    .setColor(0xe1306c)
    .setTimestamp(new Date(post.criadoEm))
    .setFooter({ text: `📍 ${post.local || 'Sem localização'} • ${starsToHearts(post.curtidas?.length || 0)} curtidas` });

  if (post.imagem) embed.setImage(post.imagem);

  return embed;
}

// ── Perfil embed ─────────────────────────────────────────────
function buildPerfilEmbed(perfil, followData, postCount) {
  const embed = new EmbedBuilder()
    .setTitle(`@${perfil.username}${perfil.verificado ? '  ✅' : ''}`)
    .setDescription(perfil.bio || '*Sem bio*')
    .setColor(0xe1306c)
    .addFields(
      { name: '📸  Posts',      value: `**${postCount}**`,                        inline: true },
      { name: '👥  Seguidores', value: `**${followData.seguidores?.length || 0}**`, inline: true },
      { name: '➡️  Seguindo',   value: `**${followData.seguindo?.length    || 0}**`, inline: true },
    )
    .setTimestamp();

  if (perfil.fotoPerfil) embed.setThumbnail(perfil.fotoPerfil);

  return embed;
}

// ── Comentário embed ─────────────────────────────────────────
function buildComentarioEmbed(comentario, autorPerfil) {
  return new EmbedBuilder()
    .setAuthor({
      name: `@${autorPerfil.username}`,
      iconURL: autorPerfil.fotoPerfil || null,
    })
    .setDescription(comentario.texto)
    .setColor(0x833ab4)
    .setTimestamp(new Date(comentario.criadoEm));
}

module.exports = { buildPostEmbed, buildPerfilEmbed, buildComentarioEmbed };
