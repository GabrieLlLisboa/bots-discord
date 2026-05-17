const { handleFeedMessage } = require('../utils/igInteractions');

module.exports = {
  name: 'messageCreate',

  async execute(message) {
    if (message.author.bot) return;

    const feedChannelId = process.env.IG_FEED_CHANNEL_ID;
    if (!feedChannelId) return;

    // Só age se a mensagem for no canal do feed
    if (message.channelId !== feedChannelId) return;

    await handleFeedMessage(message);
  },
};
