# 🎭 Bot do Servidor — Roleplay

Bot completo para servidores de Roleplay no Discord, com sistema de **tíquetes**, **avaliação de staff** e **Instagram do RP**.

---

## 📦 Índice

1. [Instalação (Administradores)](#instalação)
2. [Configuração do .env](#configuração-do-env)
3. [Sistema de Tíquetes](#sistema-de-tíquetes)
4. [Sistema de Avaliação de Staff](#sistema-de-avaliação-de-staff)
5. [Instagram do RP](#instagram-do-rp)
6. [Todos os Comandos](#todos-os-comandos)
7. [Estrutura de Arquivos](#estrutura-de-arquivos)
8. [Permissões do Bot](#permissões-do-bot)

---

## Instalação

> Requisitos: **Node.js v18+** e **npm**

```bash
# 1. Instale as dependências
npm install

# 2. Preencha o arquivo .env com suas configurações (veja abaixo)

# 3. Registre os comandos slash no servidor (faça isso uma vez, ou ao adicionar novos comandos)
npm run deploy

# 4. Ligue o bot
npm start
```

---

## Configuração do .env

Abra o arquivo `.env` na raiz do projeto e preencha cada campo:

```env
TOKEN=          # Token do bot
CLIENT_ID=      # ID da aplicação
GUILD_ID=       # ID do servidor
```

> **Como encontrar IDs:** Ative o Modo Desenvolvedor em **Configurações do Discord → Avançado → Modo Desenvolvedor**, depois clique com o botão direito em qualquer servidor, canal ou cargo para copiar o ID.

### Tíquetes

```env
CATEGORY_ID=        # ID da categoria do Discord onde os canais de tíquete serão criados
STAFF_ROLE_ID=      # ID do cargo de Staff/Suporte (quem vê e responde tíquetes)
LOG_CHANNEL_ID=     # ID do canal de logs de tíquetes fechados (opcional)
```

### Avaliações

```env
AVALIACOES_CHANNEL_ID=   # Canal onde as avaliações de staff são postadas
```

### Instagram do RP

```env
IG_FEED_CHANNEL_ID=      # Canal do feed de posts
IG_STORIES_CHANNEL_ID=   # Canal dos stories (somem em 24h)
```

---

## Sistema de Tíquetes

O sistema de tíquetes permite que os membros abram um canal privado para ser atendido pelo staff.

### Como funciona (membros)

1. Vá ao canal de atendimento onde o painel foi postado
2. Clique no menu **"Selecione uma categoria..."**
3. Escolha a categoria correspondente ao seu problema:

| Categoria | Quando usar |
|---|---|
| 🛠️ **Suporte** | Dúvidas, problemas técnicos ou ajuda geral no servidor |
| 🚨 **Denúncia** | Reportar um jogador por comportamento inadequado |
| 🪪 **Criar RG** | Solicitar a criação do documento de identidade do seu personagem |
| 🏢 **Assumir Organização** | Solicitar a liderança de uma organização do RP |

4. Um canal privado será criado automaticamente só para você e o staff
5. Descreva seu caso com o máximo de detalhes
6. Quando o atendimento terminar, o staff fechará o tíquete

> ⚠️ Você só pode ter **um tíquete aberto por categoria** ao mesmo tempo.

### Como funciona (staff)

- Ao abrir um tíquete, o cargo de Staff é pingado automaticamente
- Use o botão **🗑️ Fechar Tíquete** dentro do canal para encerrar o atendimento
- O canal é deletado automaticamente após 3 segundos
- Um log é registrado no canal de logs (se configurado)
- Para adicionar alguém extra ao tíquete, use `/adicionar @usuario`

### Comandos do sistema de tíquetes

| Comando | Permissão | O que faz |
|---|---|---|
| `/painel` | Administrador | Envia o painel de tíquetes no canal atual |
| `/fechar` | Staff | Fecha e deleta o tíquete atual |
| `/adicionar @usuario` | Staff | Adiciona um usuário ao canal do tíquete |

---

## Sistema de Avaliação de Staff

Permite que os membros avaliem o atendimento recebido de forma simples e opcionalmente anônima.

### Como funciona (membros)

1. Vá ao canal de avaliações onde o painel foi postado
2. Clique no botão **⭐ Avaliar Staff**
3. Preencha o formulário:
   - **Nome do Staff** — quem te atendeu
   - **Nota** — de 1 a 5
   - **Motivo** — descreva como foi o atendimento
   - **Anônimo?** — digite `sim` para ocultar seu nome, `não` para aparecer
4. A avaliação é postada automaticamente no canal de avaliações

A cor do embed muda conforme a nota: 🔴 1 • 🟠 2 • 🟡 3 • 🟢 4 • 🔵 5

### Comandos (admin)

| Comando | Permissão | O que faz |
|---|---|---|
| `/avaliar-staff` | Administrador | Envia o painel de avaliação no canal atual |

---

## Instagram do RP

Sistema que simula o Instagram dentro do Discord, com feed, stories, perfis, curtidas, comentários e seguidores — tudo no personagem do RP.

### Primeiros passos — crie seu perfil

Antes de postar qualquer coisa, crie seu perfil com:

```
/ig-perfil
```

Preencha no modal:
- **Nome de usuário** — será seu `@` no sistema (ex: `joao_silva`)
- **Bio** — descrição do personagem (até 150 caracteres)
- **Foto de perfil** — cole um link de imagem (URL)

> Você pode editar seu perfil a qualquer momento usando `/ig-perfil` novamente.

---

### Publicar no Feed

```
/ig-post
```

Preencha no modal:
- **Link da imagem** — URL da foto que quer postar
- **Legenda** — texto da publicação (opcional, até 300 caracteres)
- **Localização** — onde seu personagem está (opcional)

O post aparece no canal de feed com:
- Embed com sua foto, legenda e localização
- Botão ❤️ para curtir (clique de novo para descurtir)
- Botão 💬 para comentar (abre um modal para digitar)
- Botão ↩️ para responder um comentário específico
- Uma **thread** criada automaticamente para os comentários

---

### Publicar um Story

```
/ig-story
```

Stories somem automaticamente após **24 horas**.

Preencha no modal:
- **Link da imagem** — URL da foto do story
- **Legenda** — texto curto (opcional)

O story aparece no canal de stories com um contador regressivo mostrando quando expira.

Para ver todos os stories ativos do servidor:

```
/ig-stories
```

---

### Seguir perfis

```
/ig-seguir usuario:joao_silva
```

- Se ainda não segue → passa a seguir
- Se já segue → deixa de seguir

---

### Ver perfil

```
/ig-ver-perfil
```

Sem argumentos mostra o seu próprio perfil. Para ver o de outra pessoa:

```
/ig-ver-perfil usuario:joao_silva
```

O perfil exibe foto, bio, número de posts, seguidores e seguindo. Se for o perfil de outra pessoa, aparece um botão para seguir/deixar de seguir direto.

---

## Todos os Comandos

### Administradores

| Comando | Sistema | O que faz |
|---|---|---|
| `/painel` | Tíquetes | Envia o painel de tíquetes |
| `/avaliar-staff` | Avaliações | Envia o painel de avaliações |

### Staff

| Comando | Sistema | O que faz |
|---|---|---|
| `/fechar` | Tíquetes | Fecha e deleta o tíquete atual |
| `/adicionar @usuario` | Tíquetes | Adiciona alguém ao tíquete |

### Membros

| Comando | Sistema | O que faz |
|---|---|---|
| `/ig-perfil` | Instagram | Cria ou edita o perfil |
| `/ig-post` | Instagram | Publica foto no feed |
| `/ig-story` | Instagram | Publica story temporário |
| `/ig-stories` | Instagram | Vê todos os stories ativos |
| `/ig-seguir` | Instagram | Segue ou deixa de seguir |
| `/ig-ver-perfil` | Instagram | Vê um perfil |

---

## Estrutura de Arquivos

```
ticket-bot/
├── data/                        # Banco de dados local (gerado automaticamente)
│   ├── perfis.json              # Perfis do Instagram
│   ├── posts.json               # Posts publicados
│   ├── stories.json             # Stories ativos
│   └── seguidores.json          # Relações de seguir
├── src/
│   ├── commands/
│   │   ├── painel.js            # Painel de tíquetes
│   │   ├── fechar.js            # Fechar tíquete
│   │   ├── adicionar.js         # Adicionar ao tíquete
│   │   ├── avaliar-staff.js     # Painel de avaliações
│   │   ├── ig-perfil.js         # Criar/editar perfil
│   │   ├── ig-post.js           # Publicar no feed
│   │   ├── ig-story.js          # Publicar story
│   │   ├── ig-stories.js        # Listar stories
│   │   ├── ig-seguir.js         # Seguir/deixar de seguir
│   │   └── ig-ver-perfil.js     # Ver perfil
│   ├── events/
│   │   ├── ready.js             # Bot online
│   │   └── interactionCreate.js # Gerencia todas as interações
│   ├── utils/
│   │   ├── ticketConfig.js      # Configuração das categorias de tíquete
│   │   ├── igDb.js              # Banco de dados do Instagram
│   │   ├── igEmbeds.js          # Embeds do Instagram
│   │   └── igInteractions.js    # Lógica de botões e modais do Instagram
│   ├── deploy-commands.js       # Registra os slash commands
│   └── index.js                 # Entrada principal
├── .env                         # ⚠️ Suas configurações — NUNCA compartilhe
├── .gitignore
├── package.json
└── README.md
```

---

## Permissões do Bot

No [Portal de Desenvolvedores](https://discord.com/developers/applications), vá em **OAuth2 → Bot** e ative:

- ✅ Send Messages
- ✅ Send Messages in Threads
- ✅ Create Public Threads
- ✅ Manage Channels
- ✅ Read Message History
- ✅ View Channels
- ✅ Embed Links
- ✅ Use Slash Commands

**Escopos OAuth2:** `bot` + `applications.commands`

---

## Personalizando as categorias de tíquete

Edite o array `TICKET_CATEGORIES` em `src/utils/ticketConfig.js`:

```js
{
  id: 'minha-categoria',       // identificador único, sem espaços
  label: '🎯 Minha Categoria', // nome exibido no menu
  description: 'Descrição curta',
  emoji: '🎯',
  color: 0x5865f2,             // cor do embed em hexadecimal
  welcomeMessage: 'Mensagem exibida ao abrir o tíquete.',
}
```

---

> 💾 Os dados do Instagram ficam salvos na pasta `data/`. Faça backup dessa pasta regularmente para não perder os perfis e posts dos membros.
