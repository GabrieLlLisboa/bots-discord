module.exports = {
  name: 'ready',
  once: true,
  execute(client) {
    console.log(`✅ Bot online como: ${client.user.tag}`);
    client.user.setActivity('🎭 Roleplay', { type: 3 }); // 3 = Watching
  },
};
