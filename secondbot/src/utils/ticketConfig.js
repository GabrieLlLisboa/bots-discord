const { EmbedBuilder } = require('discord.js');

// ============================================================
//  CATEGORIAS DE TÍQUETE — edite aqui para personalizar
// ============================================================
const TICKET_CATEGORIES = [
  {
    id: 'suporte',
    label: '🛠️ Suporte',
    description: 'Precisa de ajuda com algo no servidor?',
    emoji: '🛠️',
    color: 0x5865f2,
    welcomeMessage: '👋 Olá! Descreva seu problema com o máximo de detalhes possível. Nossa equipe irá te atender em breve.',
  },
  {
    id: 'denuncia',
    label: '🚨 Denúncia',
    description: 'Reporte um jogador ou situação suspeita.',
    emoji: '🚨',
    color: 0xed4245,
    welcomeMessage: '🚨 Tíquete de **denúncia** aberto!\nPor favor, informe:\n> • Nome do jogador denunciado\n> • Motivo da denúncia\n> • Provas (prints, vídeos)',
  },
  {
    id: 'criar-rg',
    label: '🪪 Criar RG',
    description: 'Solicite a criação do seu documento de identidade.',
    emoji: '🪪',
    color: 0x57f287,
    welcomeMessage: '🪪 Tíquete de **Criação de RG** aberto!\nPor favor, informe:\n> • Nome completo do personagem\n> • Data de nascimento do personagem\n> • Cidade natal\n> • Foto (print do personagem)',
  },
  {
    id: 'assumir-org',
    label: '🏢 Assumir Organização',
    description: 'Solicite a liderança de uma organização.',
    emoji: '🏢',
    color: 0xfee75c,
    welcomeMessage: '🏢 Tíquete de **Assumir Organização** aberto!\nPor favor, informe:\n> • Nome da organização desejada\n> • Motivo pelo qual deseja assumir\n> • Experiência prévia no RP',
  },
];

// ============================================================
//  EMBED DO PAINEL PRINCIPAL
// ============================================================
function buildPanelEmbed() {
  return new EmbedBuilder()
    .setTitle('🎭  Central de Atendimento')
    .setDescription(
      '> Bem-vindo ao sistema de suporte do servidor!\n> Selecione uma categoria abaixo para abrir um tíquete.\n\u200b'
    )
    .addFields(
      TICKET_CATEGORIES.map(cat => ({
        name: `${cat.emoji}  ${cat.label.replace(cat.emoji, '').trim()}`,
        value: cat.description,
        inline: true,
      }))
    )
    .setColor(0x2b2d31)
    .setFooter({ text: 'Apenas abra um tíquete se realmente necessário.' })
    .setTimestamp();
}

// ============================================================
//  EMBED DE BOAS-VINDAS DO TÍQUETE
// ============================================================
function buildTicketWelcomeEmbed(category, user) {
  return new EmbedBuilder()
    .setTitle(`${category.emoji}  ${category.label.replace(category.emoji, '').trim()}`)
    .setDescription(category.welcomeMessage)
    .setColor(category.color)
    .setFooter({ text: `Aberto por ${user.tag}` })
    .setTimestamp();
}

module.exports = { TICKET_CATEGORIES, buildPanelEmbed, buildTicketWelcomeEmbed };
