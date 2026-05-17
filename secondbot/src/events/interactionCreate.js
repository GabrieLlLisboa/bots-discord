const {
  PermissionFlagsBits,
  ChannelType,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ModalBuilder,
  TextInputBuilder,
  TextInputStyle,
  EmbedBuilder,
  StringSelectMenuBuilder,
} = require('discord.js');
const { TICKET_CATEGORIES, buildTicketWelcomeEmbed } = require('../utils/ticketConfig');
const { handleIgInteraction, handleFeedMessage } = require('../utils/igInteractions');

module.exports = {
  name: 'interactionCreate',

  async execute(interaction, client) {
    // ── Instagram — delega para handler próprio ─────────────
    const igCustomIds = ['ig_modal_perfil', 'ig_modal_post', 'ig_modal_story'];
    const isIg =
      (interaction.customId && (
        igCustomIds.includes(interaction.customId) ||
        interaction.customId.startsWith('ig_')
      ));

    if (isIg) {
      try { await handleIgInteraction(interaction); } catch (e) { console.error('IG error:', e); }
      return;
    }

    // ── Slash Commands ──────────────────────────────────────
    if (interaction.isChatInputCommand()) {
      const command = client.commands.get(interaction.commandName);
      if (!command) return;

      try {
        await command.execute(interaction);
      } catch (error) {
        console.error(`Erro no comando /${interaction.commandName}:`, error);
        const msg = { content: '❌ Ocorreu um erro ao executar este comando.', ephemeral: true };
        if (interaction.replied || interaction.deferred) {
          await interaction.followUp(msg);
        } else {
          await interaction.reply(msg);
        }
      }
      return;
    }

    // ── Select Menu — abrir tíquete ─────────────────────────
    if (interaction.isStringSelectMenu() && interaction.customId === 'ticket_select') {
      const selectedId = interaction.values[0];
      const category = TICKET_CATEGORIES.find(c => c.id === selectedId);
      if (!category) return;

      const guild = interaction.guild;
      const user = interaction.user;

      // Evita tíquetes duplicados
      const existingChannel = guild.channels.cache.find(
        ch => ch.name === `ticket-${selectedId}-${user.id}`
      );

      if (existingChannel) {
        return interaction.reply({
          content: `❌ Você já tem um tíquete aberto nessa categoria: ${existingChannel}`,
          ephemeral: true,
        });
      }

      // Permissões do canal
      const permissionOverwrites = [
        {
          id: guild.id, // @everyone não vê
          deny: [PermissionFlagsBits.ViewChannel],
        },
        {
          id: user.id, // dono do tíquete vê
          allow: [
            PermissionFlagsBits.ViewChannel,
            PermissionFlagsBits.SendMessages,
            PermissionFlagsBits.ReadMessageHistory,
          ],
        },
      ];

      // Staff vê o tíquete
      if (process.env.STAFF_ROLE_ID) {
        permissionOverwrites.push({
          id: process.env.STAFF_ROLE_ID,
          allow: [
            PermissionFlagsBits.ViewChannel,
            PermissionFlagsBits.SendMessages,
            PermissionFlagsBits.ReadMessageHistory,
            PermissionFlagsBits.ManageChannels,
          ],
        });
      }

      // Cria o canal
      const ticketChannel = await guild.channels.create({
        name: `ticket-${selectedId}-${user.id}`,
        type: ChannelType.GuildText,
        parent: process.env.CATEGORY_ID || null,
        permissionOverwrites,
        topic: `Tíquete de ${user.tag} | Categoria: ${category.label}`,
      });

      // Botão de fechar
      const closeButton = new ButtonBuilder()
        .setCustomId('ticket_close')
        .setLabel('🗑️  Fechar Tíquete')
        .setStyle(ButtonStyle.Danger);

      const row = new ActionRowBuilder().addComponents(closeButton);

      const welcomeEmbed = buildTicketWelcomeEmbed(category, user);
      await ticketChannel.send({
        content: `${user} ${process.env.STAFF_ROLE_ID ? `<@&${process.env.STAFF_ROLE_ID}>` : ''}`,
        embeds: [welcomeEmbed],
        components: [row],
      });

      await interaction.reply({
        content: `✅ Seu tíquete foi aberto em ${ticketChannel}!`,
        ephemeral: true,
      });
      return;
    }

    // ── Botão — abrir formulário de avaliação ───────────────
    if (interaction.isButton() && interaction.customId === 'abrir_avaliacao') {
      const modal = new ModalBuilder()
        .setCustomId('modal_avaliacao')
        .setTitle('⭐ Avaliar Staff');

      const nomeInput = new TextInputBuilder()
        .setCustomId('staff_nome')
        .setLabel('Nome do Staff')
        .setPlaceholder('Ex: João Silva')
        .setStyle(TextInputStyle.Short)
        .setRequired(true)
        .setMaxLength(50);

      const notaInput = new TextInputBuilder()
        .setCustomId('staff_nota')
        .setLabel('Nota (1 a 5 estrelas)')
        .setPlaceholder('Digite um número de 1 a 5')
        .setStyle(TextInputStyle.Short)
        .setRequired(true)
        .setMaxLength(1);

      const motivoInput = new TextInputBuilder()
        .setCustomId('staff_motivo')
        .setLabel('Motivo da avaliação')
        .setPlaceholder('Descreva como foi o atendimento...')
        .setStyle(TextInputStyle.Paragraph)
        .setRequired(true)
        .setMaxLength(500);

      const anonimoInput = new TextInputBuilder()
        .setCustomId('staff_anonimo')
        .setLabel('Deseja ser anônimo? (sim / não)')
        .setPlaceholder('Digite: sim  ou  não')
        .setStyle(TextInputStyle.Short)
        .setRequired(true)
        .setMaxLength(3);

      modal.addComponents(
        new ActionRowBuilder().addComponents(nomeInput),
        new ActionRowBuilder().addComponents(notaInput),
        new ActionRowBuilder().addComponents(motivoInput),
        new ActionRowBuilder().addComponents(anonimoInput),
      );

      await interaction.showModal(modal);
      return;
    }

    // ── Modal — processar avaliação ─────────────────────────
    if (interaction.isModalSubmit() && interaction.customId === 'modal_avaliacao') {
      const nomeStaff  = interaction.fields.getTextInputValue('staff_nome').trim();
      const notaRaw    = interaction.fields.getTextInputValue('staff_nota').trim();
      const motivo     = interaction.fields.getTextInputValue('staff_motivo').trim();
      const anonimoRaw = interaction.fields.getTextInputValue('staff_anonimo').trim().toLowerCase();

      // Valida nota
      const nota = parseInt(notaRaw);
      if (isNaN(nota) || nota < 1 || nota > 5) {
        return interaction.reply({
          content: '❌ Nota inválida! Digite um número **de 1 a 5**.',
          ephemeral: true,
        });
      }

      // Valida anônimo
      if (!['sim', 'não', 'nao'].includes(anonimoRaw)) {
        return interaction.reply({
          content: '❌ Para "anônimo" digite apenas **sim** ou **não**.',
          ephemeral: true,
        });
      }

      const isAnonimo = anonimoRaw === 'sim';
      const autor = isAnonimo ? '🕵️ Anônimo' : `${interaction.user.tag}`;
      const autorMencao = isAnonimo ? '**Anônimo**' : `${interaction.user}`;

      // Monta estrelas
      const estrelas = '⭐'.repeat(nota) + '▪️'.repeat(5 - nota);

      // Cores por nota
      const coresPorNota = [0xed4245, 0xe67e22, 0xfee75c, 0x57f287, 0x00b4d8];
      const cor = coresPorNota[nota - 1];

      const avaliacaoEmbed = new EmbedBuilder()
        .setTitle(`${estrelas}  Nova Avaliação de Staff`)
        .addFields(
          { name: '👤  Staff Avaliado',  value: nomeStaff,   inline: true  },
          { name: '⭐  Nota',            value: `**${nota}/5**`, inline: true },
          { name: '🕵️  Enviado por',     value: autorMencao, inline: true  },
          { name: '💬  Motivo',          value: motivo,      inline: false },
        )
        .setColor(cor)
        .setFooter({ text: `Avaliação enviada por ${autor}` })
        .setTimestamp();

      // Tenta postar no canal de avaliações ou no canal configurado
      const canalId = process.env.AVALIACOES_CHANNEL_ID;
      let canalDestino = null;

      if (canalId) {
        canalDestino = interaction.guild.channels.cache.get(canalId);
      }

      // Se não tiver canal configurado, posta no canal atual
      if (!canalDestino) {
        canalDestino = interaction.channel;
      }

      await canalDestino.send({ embeds: [avaliacaoEmbed] });

      await interaction.reply({
        content: `✅ Avaliação enviada com sucesso${isAnonimo ? ' (de forma anônima)' : ''}!`,
        ephemeral: true,
      });
      return;
    }

    // ── Botão — fechar tíquete ──────────────────────────────
    if (interaction.isButton() && interaction.customId === 'ticket_close') {
      const channel = interaction.channel;

      // Apenas staff ou dono pode fechar
      const isStaff =
        process.env.STAFF_ROLE_ID &&
        interaction.member.roles.cache.has(process.env.STAFF_ROLE_ID);
      const isOwner = channel.name.endsWith(interaction.user.id);

      if (!isStaff && !isOwner) {
        return interaction.reply({
          content: '❌ Apenas o staff ou o dono do tíquete pode fechá-lo.',
          ephemeral: true,
        });
      }

      // Log
      if (process.env.LOG_CHANNEL_ID) {
        const logChannel = interaction.guild.channels.cache.get(process.env.LOG_CHANNEL_ID);
        if (logChannel) {
          const { EmbedBuilder } = require('discord.js');
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
    }
  },
};
