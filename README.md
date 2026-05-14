# 🤖 Bot de Whitelist — Discord

Bot de whitelist com ticket privado, integração com a API do Roblox e embeds modernas.

---

## 📁 Estrutura do Projeto

```
discord_whitelist_bot/
├── bot.py                  # Arquivo principal — inicializa o bot
├── requirements.txt        # Dependências Python
├── .env                    # Token do bot (NÃO commitar)
├── .env.example            # Modelo do arquivo .env
├── views/
│   ├── __init__.py
│   ├── whitelist_button.py # Botão "Abrir Whitelist" e criação do ticket
│   └── ticket_flow.py      # Fluxo de perguntas e integração Roblox
└── utils/
    ├── __init__.py
    └── roblox.py           # Funções de busca na API do Roblox
```

---

## ⚙️ Instalação

### 1. Clone / baixe o projeto

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

```
DISCORD_TOKEN=seu_token_aqui
```

### 4. Configure as permissões do bot no Discord Developer Portal

No portal [discord.com/developers](https://discord.com/developers/applications):

- **Bot Intents obrigatórias:**
  - ✅ `SERVER MEMBERS INTENT`
  - ✅ `MESSAGE CONTENT INTENT`

- **Permissões necessárias no servidor:**
  - `Manage Channels` — para criar tickets
  - `Send Messages`
  - `Embed Links`
  - `Read Message History`
  - `View Channels`

### 5. Inicie o bot

```bash
python bot.py
```

---

## 🚀 Uso

| Comando | Quem pode usar | Descrição |
|---------|---------------|-----------|
| `!form` | Administradores | Envia o embed com o botão de abrir whitelist |

---

## 🔧 Personalização

### Cargos da Staff

Em `views/whitelist_button.py`, edite a lista:

```python
STAFF_ROLE_NAMES = ["Staff", "Admin", "Moderador", "Whitelist"]
```

### Timeout das perguntas

Em `views/ticket_flow.py`:

```python
TIMEOUT = 300  # segundos (padrão: 5 minutos)
```

### Categoria dos tickets

O bot procura automaticamente uma categoria chamada `Tickets`. Crie-a no seu servidor ou ajuste o nome em `views/whitelist_button.py`.

---

## 📌 Fluxo Completo

```
Admin usa !form
    └─> Embed com botão "📋 Abrir Whitelist"
            └─> Usuário clica
                    └─> Canal privado criado (whitelist-nome)
                            └─> Solicita nickname do Roblox
                                    └─> Busca na API e exibe perfil
                                            └─> 5 perguntas (uma por vez, timeout de 5min)
                                                    └─> Embed de resumo para staff
                                                            └─> Mensagem final ✅
```

---

## 📦 Dependências

- [discord.py](https://discordpy.readthedocs.io/) >= 2.3.2
- [python-dotenv](https://pypi.org/project/python-dotenv/) >= 1.0.0
- [aiohttp](https://docs.aiohttp.org/) >= 3.9.0
