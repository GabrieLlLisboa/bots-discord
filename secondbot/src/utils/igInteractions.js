const {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ModalBuilder,
  TextInputBuilder,
  TextInputStyle,
  EmbedBuilder,
} = require('discord.js');

const {
  getPerfil, savePerfil, getPerfilByUsername,
  getPost, savePost,
  getFollowData, follow, unfollow, isFollowing,
} = require('../utils/igDb');

const { buildPostEmbed, buildComentarioEmbed } = require('../utils/igEmbeds');

// Gera ID único simples
function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

// Botões de interação do post
function postActionRow(postId, curtidas = []) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`ig_curtir_${postId}`)
      .setLabel(`❤️ ${curtidas.length}`)
      .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setCustomId(`ig_comentar_${postId}`)
      .setLabel('💬 Comentar')
      .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setCustomId(`ig_responder_${postId}`)
      .setLabel('↩️ Responder')
      .setStyle(ButtonStyle.Secondary),
  );
}

// ============================================================
//  HANDLER DE MENSAGENS NO CANAL DO FEED
//  Chame isso no evento messageCreate quando o canal for o feed
// ============================================================
async function handleFeedMessage(message) {
  if (message.author.bot) return;

  const perfil = getPerfil(message.author.id);
  if (!perfil) {
    await message.delete().catch(() => {});
    const aviso = await message.channel.send(
      `${message.author} ❌ Você ainda não tem um perfil! Use **/ig-perfil** para criar antes de postar.`
    );
    setTimeout(() => aviso.delete().catch(() => {}), 5000);
    return;
  }

  // Pega imagem do anexo (se tiver)
  const anexo   = message.attachments.find(a => a.contentType?.startsWith('image/'));
  const imagem  = anexo?.url || null;
  const legenda = message.content.trim() || null;

  // Deleta a mensagem original para ficar limpo
  await message.delete().catch(() => {});

  const postId = uid();
  const post   = {
    id: postId,
    autorId: message.author.id,
    imagem,
    legenda,
    local: null,
    curtidas: [],
    comentarios: [],
    criadoEm: new Date().toISOString(),
    threadId: null,
  };

  savePost(postId, post);

  const embed = buildPostEmbed(post, perfil);
  const row   = postActionRow(postId, []);

  const msg = await message.channel.send({ embeds: [embed], components: [row] });

  // Cria thread para comentários
  const thread = await msg.startThread({
    name: `💬 @${perfil.username}`,
    autoArchiveDuration: 1440,
  });
  await thread.send({ content: '💬 **Comentários** — use os botões no post acima para comentar!' });

  savePost(postId, { ...post, threadId: thread.id, messageId: msg.id });
}

// ============================================================
//  HANDLER DE INTERAÇÕES (modais + botões)
// ============================================================
async function handleIgInteraction(interaction) {

  // ── Modal: salvar perfil (só username) ───────────────────
  if (interaction.isModalSubmit() && interaction.customId === 'ig_modal_perfil') {
    const username    = interaction.fields.getTextInputValue('ig_username').trim().replace(/\s+/g, '_');
    const isNovaConta = !getPerfil(interaction.user.id);

    // Verifica username duplicado
    const existente = getPerfilByUsername(username);
    if (existente && existente.userId !== interaction.user.id) {
      return interaction.reply({ content: `❌ O nome **@${username}** já está em uso!`, ephemeral: true });
    }

    savePerfil(interaction.user.id, {
      userId: interaction.user.id,
      username,
      bio: getPerfil(interaction.user.id)?.bio || '',
      fotoPerfil: getPerfil(interaction.user.id)?.fotoPerfil || null,
      verificado: false,
      criadoEm: getPerfil(interaction.user.id)?.criadoEm || new Date().toISOString(),
    });

    // Se for conta nova, anuncia no canal de feed
    if (isNovaConta) {
      const feedChannelId = process.env.IG_FEED_CHANNEL_ID;
      const feedChannel   = feedChannelId
        ? interaction.guild.channels.cache.get(feedChannelId)
        : null;

      if (feedChannel) {
        const embed = new EmbedBuilder()
          .setDescription(`👤 Conta **@${username}** criada!`)
          .setColor(0xe1306c)
          .setTimestamp();
        await feedChannel.send({ embeds: [embed] });
      }
    }

    return interaction.reply({
      content: isNovaConta
        ? `✅ Perfil **@${username}** criado! Já pode postar no feed. 📸`
        : `✅ Usuário atualizado para **@${username}**!`,
      ephemeral: true,
    });
  }

  // ── Modal: comentar ──────────────────────────────────────
  if (interaction.isModalSubmit() && interaction.customId.startsWith('ig_modal_comentar_')) {
    const postId = interaction.customId.replace('ig_modal_comentar_', '');
    const texto  = interaction.fields.getTextInputValue('ig_comentario_texto').trim();

    const post   = getPost(postId);
    const perfil = getPerfil(interaction.user.id);

    if (!post || !perfil) return interaction.reply({ content: '❌ Post ou perfil não encontrado.', ephemeral: true });

    const comentario = { texto, autorId: interaction.user.id, criadoEm: new Date().toISOString() };
    savePost(postId, { ...post, comentarios: [...(post.comentarios || []), comentario] });

    if (post.threadId) {
      const thread = interaction.guild.channels.cache.get(post.threadId);
      if (thread) {
        const embed = buildComentarioEmbed(comentario, perfil);
        await thread.send({ embeds: [embed] });
      }
    }

    return interaction.reply({ content: '✅ Comentário enviado!', ephemeral: true });
  }

  // ── Modal: responder ─────────────────────────────────────
  if (interaction.isModalSubmit() && interaction.customId.startsWith('ig_modal_responder_')) {
    const postId    = interaction.customId.replace('ig_modal_responder_', '');
    const texto     = interaction.fields.getTextInputValue('ig_resposta_texto').trim();
    const mencaoRaw = interaction.fields.getTextInputValue('ig_resposta_mencao').trim().replace('@', '');

    const post         = getPost(postId);
    const meuPerfil    = getPerfil(interaction.user.id);
    const perfilMencao = mencaoRaw ? getPerfilByUsername(mencaoRaw) : null;

    if (!post || !meuPerfil) return interaction.reply({ content: '❌ Post ou perfil não encontrado.', ephemeral: true });

    if (post.threadId) {
      const thread = interaction.guild.channels.cache.get(post.threadId);
      if (thread) {
        const embed = new EmbedBuilder()
          .setAuthor({ name: `@${meuPerfil.username}`, iconURL: meuPerfil.fotoPerfil || null })
          .setDescription(
            (perfilMencao ? `↩️ respondendo **@${perfilMencao.username}**\n` : '') + texto
          )
          .setColor(0x833ab4)
          .setTimestamp();
        await thread.send({ embeds: [embed] });
      }
    }

    return interaction.reply({ content: '✅ Resposta enviada!', ephemeral: true });
  }

  // ── Botão: curtir ────────────────────────────────────────
  if (interaction.isButton() && interaction.customId.startsWith('ig_curtir_')) {
    const postId   = interaction.customId.replace('ig_curtir_', '');
    const post     = getPost(postId);
    if (!post) return interaction.reply({ content: '❌ Post não encontrado.', ephemeral: true });

    const curtidas = [...(post.curtidas || [])];
    const idx      = curtidas.indexOf(interaction.user.id);
    if (idx === -1) curtidas.push(interaction.user.id);
    else curtidas.splice(idx, 1);

    const updated = { ...post, curtidas };
    savePost(postId, updated);

    const perfil = getPerfil(post.autorId);
    const embed  = buildPostEmbed(updated, perfil);
    const row    = postActionRow(postId, curtidas);

    await interaction.update({ embeds: [embed], components: [row] });
    return;
  }

  // ── Botão: comentar ──────────────────────────────────────
  if (interaction.isButton() && interaction.customId.startsWith('ig_comentar_')) {
    const postId = interaction.customId.replace('ig_comentar_', '');
    const perfil = getPerfil(interaction.user.id);
    if (!perfil) return interaction.reply({ content: '❌ Crie seu perfil com /ig-perfil para comentar.', ephemeral: true });

    const modal = new ModalBuilder()
      .setCustomId(`ig_modal_comentar_${postId}`)
      .setTitle('💬 Comentar');

    modal.addComponents(
      new ActionRowBuilder().addComponents(
        new TextInputBuilder()
          .setCustomId('ig_comentario_texto')
          .setLabel('Seu comentário')
          .setStyle(TextInputStyle.Paragraph)
          .setPlaceholder('Escreva seu comentário...')
          .setRequired(true)
          .setMaxLength(200)
      )
    );
    await interaction.showModal(modal);
    return;
  }

  // ── Botão: responder ─────────────────────────────────────
  if (interaction.isButton() && interaction.customId.startsWith('ig_responder_')) {
    const postId = interaction.customId.replace('ig_responder_', '');
    const perfil = getPerfil(interaction.user.id);
    if (!perfil) return interaction.reply({ content: '❌ Crie seu perfil com /ig-perfil para responder.', ephemeral: true });

    const modal = new ModalBuilder()
      .setCustomId(`ig_modal_responder_${postId}`)
      .setTitle('↩️ Responder comentário');

    modal.addComponents(
      new ActionRowBuilder().addComponents(
        new TextInputBuilder()
          .setCustomId('ig_resposta_mencao')
          .setLabel('Responder para (@ do usuário)')
          .setStyle(TextInputStyle.Short)
          .setPlaceholder('Ex: joao_silva')
          .setRequired(false)
          .setMaxLength(30)
      ),
      new ActionRowBuilder().addComponents(
        new TextInputBuilder()
          .setCustomId('ig_resposta_texto')
          .setLabel('Sua resposta')
          .setStyle(TextInputStyle.Paragraph)
          .setPlaceholder('Escreva sua resposta...')
          .setRequired(true)
          .setMaxLength(200)
      ),
    );
    await interaction.showModal(modal);
    return;
  }

  // ── Botão: seguir via perfil ─────────────────────────────
  if (interaction.isButton() && interaction.customId.startsWith('ig_follow_')) {
    const targetId  = interaction.customId.replace('ig_follow_', '');
    const meuPerfil = getPerfil(interaction.user.id);
    if (!meuPerfil) return interaction.reply({ content: '❌ Crie seu perfil com /ig-perfil.', ephemeral: true });

    if (isFollowing(interaction.user.id, targetId)) {
      unfollow(interaction.user.id, targetId);
      await interaction.reply({ content: '✅ Você deixou de seguir esse perfil.', ephemeral: true });
    } else {
      follow(interaction.user.id, targetId);
      await interaction.reply({ content: '✅ Você começou a seguir esse perfil!', ephemeral: true });
    }
    return;
  }
}

module.exports = { handleIgInteraction, handleFeedMessage };
