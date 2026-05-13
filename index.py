import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

# Carrega as configurações do .env
load_dotenv()

# Pega as configurações
TOKEN = os.getenv('DISCORD_TOKEN')
CARGO_IDS = [int(id.strip()) for id in os.getenv('CARGO_IDS', '').split(',') if id.strip()]
CANAL_BOAS_VINDAS = int(os.getenv('CANAL_BOAS_VINDAS', '0'))
CANAL_SAIDA = int(os.getenv('CANAL_SAIDA', '0'))

# Configura o bot
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')
    print(f'📝 {len(CARGO_IDS)} cargo(s) configurado(s)')
    print('🎉 Pronto para receber membros!')

@bot.event
async def on_member_join(member):
    # Atribui os cargos automaticamente
    for cargo_id in CARGO_IDS:
        cargo = member.guild.get_role(cargo_id)
        if cargo:
            try:
                await member.add_roles(cargo)
                print(f'✅ {cargo.name} atribuído para {member.name}')
            except:
                print(f'❌ Erro ao atribuir {cargo.name} para {member.name}')
    
    # Mensagem de boas-vindas
    canal = member.guild.get_channel(CANAL_BOAS_VINDAS)
    if canal:
        embed = discord.Embed(
            title="🌟 Bem-vindo(a)! 🌟",
            description=f"**{member.mention}** entrou no servidor",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 Usuário", value=member.name, inline=True)
        embed.add_field(name="📅 Entrou em", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="👥 Membros", value=f"{member.guild.member_count}", inline=False)
        embed.set_footer(text=f"ID: {member.id}")
        
        await canal.send(embed=embed)
        print(f'📨 Boas-vindas enviada para {member.name}')

@bot.event
async def on_member_remove(member):
    # Mensagem de saída
    canal = member.guild.get_channel(CANAL_SAIDA)
    if canal:
        embed = discord.Embed(
            title="👋 Até mais! 👋",
            description=f"**{member.name}** saiu do servidor",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 Usuário", value=member.name, inline=True)
        embed.add_field(name="📅 Entrou em", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
        embed.add_field(name="👥 Membros restantes", value=f"{member.guild.member_count}", inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        
        await canal.send(embed=embed)
        print(f'📨 Mensagem de saída enviada para {member.name}')

@bot.command()
@commands.has_permissions(administrator=True)
async def testar(ctx, membro: discord.Member = None):
    """Testa a atribuição de cargos em um membro"""
    membro = membro or ctx.author
    
    for cargo_id in CARGO_IDS:
        cargo = ctx.guild.get_role(cargo_id)
        if cargo and cargo not in membro.roles:
            try:
                await membro.add_roles(cargo)
                await ctx.send(f'✅ Cargo {cargo.name} adicionado a {membro.mention}')
            except:
                await ctx.send(f'❌ Erro ao adicionar {cargo.name}')
    
    if not CARGO_IDS:
        await ctx.send('❌ Nenhum cargo configurado no .env')

@bot.command()
@commands.has_permissions(administrator=True)
async def config(ctx):
    """Mostra a configuração atual do bot"""
    embed = discord.Embed(
        title="⚙️ Configuração do Bot",
        color=discord.Color.blue()
    )
    
    # Mostra os cargos configurados
    cargos_texto = []
    for cargo_id in CARGO_IDS:
        cargo = ctx.guild.get_role(cargo_id)
        if cargo:
            cargos_texto.append(f"• {cargo.mention}")
        else:
            cargos_texto.append(f"• ❌ Cargo não encontrado (ID: {cargo_id})")
    
    if cargos_texto:
        embed.add_field(
            name="🎖️ Cargos que serão atribuídos",
            value="\n".join(cargos_texto),
            inline=False
        )
    else:
        embed.add_field(
            name="🎖️ Cargos",
            value="❌ Nenhum cargo configurado",
            inline=False
        )
    
    # Mostra os canais configurados
    canal_bv = ctx.guild.get_channel(CANAL_BOAS_VINDAS)
    canal_saida = ctx.guild.get_channel(CANAL_SAIDA)
    
    embed.add_field(
        name="📢 Canal de Boas-vindas",
        value=canal_bv.mention if canal_bv else f"❌ ID: {CANAL_BOAS_VINDAS}",
        inline=True
    )
    
    embed.add_field(
        name="👋 Canal de Saída",
        value=canal_saida.mention if canal_saida else f"❌ ID: {CANAL_SAIDA}",
        inline=True
    )
    
    # Informação do bot
    embed.set_footer(text=f"Bot: {bot.user.name}")
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def status(ctx):
    """Mostra o status do bot"""
    embed = discord.Embed(
        title="📊 Status do Bot",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="🤖 Nome",
        value=bot.user.name,
        inline=True
    )
    
    embed.add_field(
        name="🟢 Online há",
        value=f"{round(bot.latency * 1000)}ms",
        inline=True
    )
    
    embed.add_field(
        name="📝 Comandos",
        value="`!testar`, `!config`, `!status`",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Inicia o bot
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")