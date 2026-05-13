import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

TOKEN = os.getenv('WHITELIST_TOKEN')
CANAL_WHITELIST = int(os.getenv('CANAL_WHITELIST', '0'))
CANAL_APROVACAO = int(os.getenv('CANAL_APROVACAO', '0'))
CARGO_WHITELIST = int(os.getenv('CARGO_WHITELIST', '0'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dicionário para armazenar respostas temporárias
respostas_temp = {}

class WhitelistFormulario:
    def __init__(self, usuario, canal_ticket):
        self.usuario = usuario
        self.canal_ticket = canal_ticket
        self.respostas = {}
        self.passo = 0  # Começa no 0, que é a primeira pergunta
        
        # Perguntas do formulário
        self.perguntas = [
            "📝 **Seu nickname no jogo:**",
            
            "❓ **O que é PowerGaming?**\n*(Responda com sua definição)*",
            
            "❓ **O que é MetaGaming?**\n*(Responda com sua definição)*",
            
            "❓ **O que é Combat Logging?**\n*(Responda com sua definição)*",
            
            "📖 **Gere uma história para o seu personagem:**\n*(Mínimo 5 linhas, fale sobre sua origem, motivações, etc.)*",
            
            "📋 **Crie a identidade do seu personagem. Preencha:**\n\n"
            "**Nome:** \n"
            "**Nascimento:** \n"
            "**Idade:** \n"
            "**CEP em que nasceu:** \n"
            "**CPF (fake):** \n"
            "**Profissão:**"
        ]
    
    def get_pergunta_atual(self):
        """Retorna a pergunta atual baseado no passo"""
        if self.passo < len(self.perguntas):
            return self.perguntas[self.passo]
        return None
    
    def salvar_resposta(self, resposta):
        """Salva a resposta e avança para a próxima pergunta"""
        self.respostas[self.passo] = resposta
        self.passo += 1
        return self.passo < len(self.perguntas)  # Retorna True se tem mais perguntas
    
    def esta_completo(self):
        return self.passo >= len(self.perguntas)
    
    async def enviar_pergunta_atual(self):
        """Envia a pergunta atual para o canal"""
        pergunta = self.get_pergunta_atual()
        if pergunta:
            embed = discord.Embed(
                title=f"📋 **Pergunta {self.passo + 1} de {len(self.perguntas)}**",
                description=pergunta,
                color=discord.Color.blue()
            )
            await self.canal_ticket.send(embed=embed)
            await self.canal_ticket.send("✏️ **Digite sua resposta abaixo:**")
    
    def get_respostas_formatadas(self):
        embed = discord.Embed(
            title="📋 Nova Whitelist",
            description=f"**Usuário:** {self.usuario.mention}\n**ID:** `{self.usuario.id}`\n**Tag:** {self.usuario.name}",
            color=discord.Color.blue()
        )
        
        # Formata cada resposta
        embed.add_field(
            name="📝 Nickname",
            value=self.respostas.get(0, "Não informado"),
            inline=False
        )
        
        embed.add_field(
            name="❓ PowerGaming",
            value=self.respostas.get(1, "Não informado")[:500],
            inline=False
        )
        
        embed.add_field(
            name="❓ MetaGaming",
            value=self.respostas.get(2, "Não informado")[:500],
            inline=False
        )
        
        embed.add_field(
            name="❓ Combat Logging",
            value=self.respostas.get(3, "Não informado")[:500],
            inline=False
        )
        
        embed.add_field(
            name="📖 História do Personagem",
            value=self.respostas.get(4, "Não informado")[:800],
            inline=False
        )
        
        embed.add_field(
            name="📋 Identidade",
            value=self.respostas.get(5, "Não informado")[:600],
            inline=False
        )
        
        embed.set_footer(text=f"Enviado em: {discord.utils.utcnow().strftime('%d/%m/%Y %H:%M')}")
        
        return embed

@bot.event
async def on_ready():
    print(f'✅ Bot de Whitelist online como {bot.user}')
    print(f'📢 Canal do formulário: {CANAL_WHITELIST}')
    print(f'📢 Canal de aprovação: {CANAL_APROVACAO}')

@bot.command()
@commands.has_permissions(administrator=True)
async def form(ctx):
    """Envia o formulário de whitelist no canal configurado"""
    canal = bot.get_channel(CANAL_WHITELIST)
    
    if not canal:
        await ctx.send(f"❌ Canal de whitelist com ID {CANAL_WHITELIST} não encontrado!")
        return
    
    embed = discord.Embed(
        title="🎮 **WHITELIST - Roleplay** 🎮",
        description="**Clique no botão abaixo para iniciar sua whitelist!**\n\n"
                   "📋 **O que você precisa saber:**\n"
                   "• Responda todas as perguntas com atenção\n"
                   "• Seja honesto e criativo\n"
                   "• Aguarde a análise da staff\n"
                   "• Você será notificado quando for aprovado\n\n"
                   "✨ **Boa sorte!** ✨",
        color=discord.Color.gold()
    )
    
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text="Clique no botão abaixo para começar")
    
    view = discord.ui.View()
    button = discord.ui.Button(label="📝 Abrir Whitelist", style=discord.ButtonStyle.green)
    
    async def button_callback(interaction):
        # Cria um canal privado para o usuário
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Adiciona permissão para staff
        cargo_staff = discord.utils.get(guild.roles, name="Staff")
        if cargo_staff:
            overwrites[cargo_staff] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        try:
            # Cria o canal
            canal_ticket = await guild.create_text_channel(
                f"whitelist-{interaction.user.name}",
                overwrites=overwrites
            )
            
            # Inicia o formulário
            formulario = WhitelistFormulario(interaction.user, canal_ticket)
            respostas_temp[f"{interaction.user.id}_{canal_ticket.id}"] = formulario
            
            # Mensagem de boas-vindas no ticket
            embed_welcome = discord.Embed(
                title="🎮 **Iniciando Whitelist** 🎮",
                description=f"Olá {interaction.user.mention}! Vamos começar sua whitelist.\n\n"
                           "**Regras:**\n"
                           "• Responda uma pergunta de cada vez\n"
                           "• Digite `!cancelar` a qualquer momento para cancelar\n"
                           "• Sua resposta será registrada após você enviar\n"
                           "• Seja criativo e honesto\n\n"
                           "**Vamos começar!** 🚀",
                color=discord.Color.green()
            )
            await canal_ticket.send(embed=embed_welcome)
            
            # Envia a primeira pergunta
            await formulario.enviar_pergunta_atual()
            
            await interaction.response.send_message(f"✅ Ticket criado! Acesse {canal_ticket.mention}", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao criar ticket: {e}", ephemeral=True)
            print(f"Erro: {e}")
    
    button.callback = button_callback
    view.add_item(button)
    
    await canal.send(embed=embed, view=view)
    await ctx.send("✅ Formulário enviado!")

@bot.event
async def on_message(message):
    # Ignora mensagens do próprio bot
    if message.author.bot:
        return
    
    # Processa comandos primeiro
    await bot.process_commands(message)
    
    # Verifica se é um ticket de whitelist
    if message.channel.name and message.channel.name.startswith("whitelist-"):
        
        # Comando para cancelar
        if message.content.lower() == '!cancelar':
            await message.channel.send("❌ **Whitelist cancelada!**")
            await asyncio.sleep(3)
            
            # Remove do dicionário
            chave = f"{message.author.id}_{message.channel.id}"
            if chave in respostas_temp:
                del respostas_temp[chave]
            
            await message.channel.delete()
            return
        
        # Processa resposta do formulário
        chave = f"{message.author.id}_{message.channel.id}"
        
        if chave in respostas_temp:
            formulario = respostas_temp[chave]
            
            # Verifica se o formulário já não está completo
            if formulario.esta_completo():
                await message.channel.send("❌ Você já completou o formulário! Aguarde a análise.")
                return
            
            # Salva a resposta atual
            resposta = message.content.strip()
            
            # Confirmação que recebeu a resposta
            embed_confirm = discord.Embed(
                title="✅ Resposta Registrada!",
                description=f"**Pergunta {formulario.passo + 1} respondida:**\n```{resposta[:100]}```",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed_confirm)
            
            # Salva e verifica se tem mais perguntas
            tem_mais = formulario.salvar_resposta(resposta)
            
            if tem_mais:
                # Tem mais perguntas, envia a próxima
                await asyncio.sleep(1)  # Pequena pausa para não floodar
                await formulario.enviar_pergunta_atual()
            else:
                # Formulário completo
                embed_concluido = discord.Embed(
                    title="✅ **WHITELIST CONCLUÍDA!** ✅",
                    description="**Parabéns! Você completou todas as perguntas!**\n\n"
                               "**Próximos passos:**\n"
                               "📨 Sua whitelist foi enviada para a equipe de staff\n"
                               "⏳ Aguarde a análise (pode levar alguns minutos)\n"
                               "📢 Você será notificado aqui neste ticket\n"
                               "🎉 Se aprovado, você receberá acesso ao servidor\n\n"
                               "**Obrigado pela paciência!** 🙏",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed_concluido)
                
                # Envia para o canal de aprovação
                canal_aprov = bot.get_channel(CANAL_APROVACAO)
                if canal_aprov:
                    embed_respostas = formulario.get_respostas_formatadas()
                    
                    # Botões de aprovação/reprovação
                    view = discord.ui.View(timeout=None)
                    
                    aprovar = discord.ui.Button(label="✅ Aprovar", style=discord.ButtonStyle.green)
                    reprovar = discord.ui.Button(label="❌ Reprovar", style=discord.ButtonStyle.red)
                    
                    async def aprovar_callback(interaction):
                        # Dá o cargo de whitelist se configurado
                        if CARGO_WHITELIST:
                            cargo = message.guild.get_role(CARGO_WHITELIST)
                            if cargo:
                                await message.author.add_roles(cargo)
                                await interaction.response.send_message(f"✅ Whitelist aprovada! Cargo {cargo.name} adicionado.", ephemeral=True)
                            else:
                                await interaction.response.send_message("✅ Whitelist aprovada! (Cargo não encontrado)", ephemeral=True)
                        else:
                            await interaction.response.send_message("✅ Whitelist aprovada!", ephemeral=True)
                        
                        # Envia mensagem no ticket
                        await message.channel.send(
                            embed=discord.Embed(
                                title="🎉 **WHITELIST APROVADA!** 🎉",
                                description="**Parabéns! Sua whitelist foi aprovada!**\n\n"
                                           "Bem-vindo ao servidor! Divirta-se e bom jogo! 🎮\n\n"
                                           "*O ticket será fechado em alguns segundos...*",
                                color=discord.Color.green()
                            )
                        )
                        
                        # Fecha o ticket após aprovação
                        await asyncio.sleep(5)
                        await message.channel.delete()
                        
                        # Remove do dicionário
                        chave_ticket = f"{message.author.id}_{message.channel.id}"
                        if chave_ticket in respostas_temp:
                            del respostas_temp[chave_ticket]
                    
                    async def reprovar_callback(interaction):
                        await interaction.response.send_message(
                            "❌ **Reprovar Whitelist**\n\nDigite o motivo da reprovação abaixo:",
                            ephemeral=True
                        )
                        
                        # Aguarda motivo
                        def check(m):
                            return m.author == interaction.user and m.channel == interaction.channel
                        
                        try:
                            msg_motivo = await bot.wait_for('message', timeout=120.0, check=check)
                            motivo = msg_motivo.content
                            
                            # Envia mensagem no ticket
                            await message.channel.send(
                                embed=discord.Embed(
                                    title="❌ **WHITELIST REPROVADA** ❌",
                                    description=f"**Motivo:** {motivo}\n\n"
                                               "Infelizmente sua whitelist não foi aprovada dessa vez.\n"
                                               "**Você pode tentar novamente** abrindo um novo formulário!\n\n"
                                               "Leia as regras com atenção e tente novamente.\n\n"
                                               "*O ticket será fechado em alguns segundos...*",
                                    color=discord.Color.red()
                                )
                            )
                            
                            await interaction.followup.send("✅ Motivo enviado ao usuário!", ephemeral=True)
                            
                            # Fecha o ticket
                            await asyncio.sleep(8)
                            await message.channel.delete()
                            
                            # Remove do dicionário
                            chave_ticket = f"{message.author.id}_{message.channel.id}"
                            if chave_ticket in respostas_temp:
                                del respostas_temp[chave_ticket]
                                
                        except asyncio.TimeoutError:
                            await interaction.followup.send("⏰ Tempo esgotado! Ticket será fechado sem motivo.", ephemeral=True)
                            await message.channel.send("⏰ Tempo esgotado para análise! Ticket será fechado.")
                            await asyncio.sleep(3)
                            await message.channel.delete()
                            
                            chave_ticket = f"{message.author.id}_{message.channel.id}"
                            if chave_ticket in respostas_temp:
                                del respostas_temp[chave_ticket]
                    
                    aprovar.callback = aprovar_callback
                    reprovar.callback = reprovar_callback
                    
                    view.add_item(aprovar)
                    view.add_item(reprovar)
                    
                    await canal_aprov.send(
                        content=f"📋 **NOVA WHITELIST**\nUsuário: {message.author.mention} | ID: `{message.author.id}`",
                        embed=embed_respostas,
                        view=view
                    )
                    
                    # Avisa no ticket que foi enviado
                    await message.channel.send("📨 **Sua whitelist foi enviada para a staff!**\nAguarde a análise em alguns momentos...")
                
                # Remove do dicionário
                if chave in respostas_temp:
                    del respostas_temp[chave]
        else:
            # Se não tem formulário ativo, avisa
            if not message.content.startswith('!'):
                await message.channel.send("❌ Você não tem um formulário ativo. Use o comando `!form` no canal de whitelist para começar!")

@bot.command()
@commands.has_permissions(administrator=True)
async def fechar_ticket(ctx):
    """Fecha o ticket atual (apenas staff)"""
    if ctx.channel.name and ctx.channel.name.startswith("whitelist-"):
        await ctx.send("🔒 Fechando ticket em 5 segundos...")
        
        # Remove do dicionário
        chave = f"{ctx.author.id}_{ctx.channel.id}"
        if chave in respostas_temp:
            del respostas_temp[chave]
        
        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        await ctx.send("❌ Este não é um canal de ticket!")

bot.run(TOKEN)