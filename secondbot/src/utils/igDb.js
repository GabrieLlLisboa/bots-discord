const fs   = require('fs');
const path = require('path');

const DB_DIR  = path.join(__dirname, '../../data');
const PATHS   = {
  perfis:     path.join(DB_DIR, 'perfis.json'),
  posts:      path.join(DB_DIR, 'posts.json'),
  stories:    path.join(DB_DIR, 'stories.json'),
  seguidores: path.join(DB_DIR, 'seguidores.json'),
};

// Garante que a pasta e os arquivos existem
if (!fs.existsSync(DB_DIR)) fs.mkdirSync(DB_DIR, { recursive: true });
for (const [, filePath] of Object.entries(PATHS)) {
  if (!fs.existsSync(filePath)) fs.writeFileSync(filePath, '{}');
}

function read(key) {
  try {
    return JSON.parse(fs.readFileSync(PATHS[key], 'utf-8'));
  } catch {
    return {};
  }
}

function write(key, data) {
  fs.writeFileSync(PATHS[key], JSON.stringify(data, null, 2));
}

// ── Perfis ──────────────────────────────────────────────────
function getPerfil(userId) {
  return read('perfis')[userId] || null;
}

function savePerfil(userId, data) {
  const db = read('perfis');
  db[userId] = { ...db[userId], ...data };
  write('perfis', db);
  return db[userId];
}

function getPerfilByUsername(username) {
  const db = read('perfis');
  return Object.values(db).find(p => p.username.toLowerCase() === username.toLowerCase()) || null;
}

// ── Posts ───────────────────────────────────────────────────
function getPost(postId) {
  return read('posts')[postId] || null;
}

function savePost(postId, data) {
  const db = read('posts');
  db[postId] = { ...db[postId], ...data };
  write('posts', db);
  return db[postId];
}

function getAllPosts() {
  return read('posts');
}

// ── Stories ─────────────────────────────────────────────────
function getStory(storyId) {
  return read('stories')[storyId] || null;
}

function saveStory(storyId, data) {
  const db = read('stories');
  db[storyId] = data;
  write('stories', db);
}

function deleteStory(storyId) {
  const db = read('stories');
  delete db[storyId];
  write('stories', db);
}

function getAllStories() {
  return read('stories');
}

// ── Seguidores ───────────────────────────────────────────────
// db = { userId: { seguindo: [id,...], seguidores: [id,...] } }
function getFollowData(userId) {
  return read('seguidores')[userId] || { seguindo: [], seguidores: [] };
}

function follow(followerId, targetId) {
  const db = read('seguidores');
  if (!db[followerId]) db[followerId] = { seguindo: [], seguidores: [] };
  if (!db[targetId])   db[targetId]   = { seguindo: [], seguidores: [] };

  if (!db[followerId].seguindo.includes(targetId)) {
    db[followerId].seguindo.push(targetId);
    db[targetId].seguidores.push(followerId);
  }
  write('seguidores', db);
}

function unfollow(followerId, targetId) {
  const db = read('seguidores');
  if (!db[followerId]) return;
  db[followerId].seguindo   = (db[followerId].seguindo   || []).filter(id => id !== targetId);
  if (db[targetId]) {
    db[targetId].seguidores = (db[targetId].seguidores || []).filter(id => id !== followerId);
  }
  write('seguidores', db);
}

function isFollowing(followerId, targetId) {
  const data = getFollowData(followerId);
  return data.seguindo.includes(targetId);
}

module.exports = {
  getPerfil, savePerfil, getPerfilByUsername,
  getPost, savePost, getAllPosts,
  getStory, saveStory, deleteStory, getAllStories,
  getFollowData, follow, unfollow, isFollowing,
};
