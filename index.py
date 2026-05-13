import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do .env
TOKEN = os.getenv('DISCORD_TOKEN')
CARGO_IDS_STR = os.getenv('CARGO_IDS', '')
PREFIXO = os.getenv('COMMAND_PREFIX', '!')
GUILD_ID = os.getenv('GUILD_ID')
CANAL_BOAS_VINDAS = int(os.getenv('CANAL_BOAS_VINDAS', '0'))
CANAL_SAIDA = int(os.getenv('CANAL_SAIDA', '0'))

# Converte os IDs dos cargos para lista de inteiros
try:
    CARGO_IDS = [int(id.strip()) for id in CARGO_IDS_STR.split(',') if id.strip()]
except ValueError:
    print("❌ Erro: CARGO_IDS deve conter apenas números separados por vírgula!")
    CARGO_IDS = []

# Validação das configurações
if not TOKEN:
    raise ValueError("❌ TOKEN não encontrado no arquivo .env!")
if len(CARGO_IDS) < 2:
    print(f"⚠️ Aviso: Apenas {len(CARGO_IDS)} cargo(s) configurado(s). Mínimo recomendado: 2")
if CANAL_BOAS_VINDAS == 0:
    print("⚠️ Aviso: CANAL_BOAS_VINDAS não configurado!")
if CANAL_SAIDA == 0:
    print("⚠️ Aviso: CANAL_SAIDA não configurado!")

print(f"✅ Configuração carregada:")
print(f"   - Cargos: {len(CARGO_IDS)} cargo(s)")
print(f"   - Canal de boas-vindas: {CANAL_BOAS_VINDAS if CANAL_BOAS_VINDAS != 0 else 'Não configurado'}")
print(f"   - Canal de saída: {CANAL_SAIDA if CANAL_SAIDA != 0 else 'Não configurado'}")

# Configuração do bot
intents = discord.Intents.default()
intents.members = True  # Necessário para detectar entrada/saída de membros

bot = commands.Bot(command_prefix=PREFIXO, intents=intents)

def get_member_join_image(member):
    """Retorna uma imagem de avatar ou banner padrão"""
    return member.display_avatar.url if member.avatar else member.default_avatar.url

def format_time():
    """Retorna a hora atual formatada"""
    return datetime.now().strftime("%H:%M:%S")

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📝 Cargos configurados:')
    for i, cargo_id in enumerate(CARGO_IDS, 1):
        print(f'   - Cargo {i}: {cargo_id}')
    print(f'🌐 Conectado em {len(bot.guilds)} servidor(es)')
    print(f'📢 Monitorando canais...')

@bot.event
async def on_member_join(member):
    """Atribui os cargos e envia mensagem de boas-vindas"""
    
    # Atribuição dos cargos
    cargos_atribuidos = []
    cargos_erro = []
    
    for cargo_id in CARGO_IDS:
        cargo = member.guild.get_role(cargo_id)
        
        if cargo:
            try:
                await member.add_roles(cargo)
                cargos_atribuidos.append(cargo.name)
                print(f'[{format_time()}] ✅ Cargo "{cargo.name}" atribuído a {member.name}')
            except discord.Forbidden:
                cargos_erro.append(f"{cargo.name} (sem permissão)")
                print(f'[{format_time()}] ❌ Sem permissão para atribuir cargo "{cargo.name}" a {member.name}')
            except discord.HTTPException as e:
                cargos_erro.append(f"{cargo.name} (erro HTTP)")
                print(f'[{format_time()}] ❌ Erro HTTP ao atribuir cargo "{cargo.name}": {e}')
        else:
            cargos_erro.append(f"ID {cargo_id} (não encontrado)")
            print(f'[{format_time()}] ⚠️ Cargo com ID {cargo_id} não encontrado em {member.guild.name}!')
    
    # Mensagem de boas-vindas
    canal_boas_vindas = member.guild.get_channel(CANAL_BOAS_VINDAS)
    
    if canal_boas_vindas:
        # Verifica permissões do bot no canal
        permissoes = canal_boas_vindas.permissions_for(member.guild.me)
        
        if not permissoes.send_messages:
            print(f'[{format_time()}] ❌ Sem permissão para enviar mensagens no canal {canal_boas_vindas.name}')
        else:
            # Cria embed de boas-vindas
            embed = discord.Embed(
                title="🎉 Bem-vindo(a) ao servidor! 🎉",
                description=f"**{member.mention}** acabou de entrar em **{member.guild.name}**!",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            # Adiciona thumbnail do avatar
            embed.set_thumbnail(url=get_member_join_image(member))
            
            # Adiciona campos de informação
            embed.add_field(
                name="📝 Informações",
                value=f"**Usuário:** {member.name}\n**ID:** `{member.id}`\n**Conta criada:** {member.created_at.strftime('%d/%m/%Y')}",
                inline=True
            )
            
            # Adiciona cargos atribuídos
            if cargos_atribuidos:
                embed.add_field(
                    name="🎖️ Cargos atribuídos",
                    value="\n".join([f"✅ {cargo}" for cargo in cargos_atribuidos]),
                    inline=True
                )
            
            # Adiciona contagem de membros
            embed.add_field(
                name="👥 Membros",
                value=f"Somos agora **{member.guild.member_count}** membros!",
                inline=False
            )
            
            # Adiciona mensagem de erro se houver
            if cargos_erro:
                embed.add_field(
                    name="⚠️ Aviso",
                    value="Alguns cargos não puderam ser atribuídos. Contate um administrador.",
                    inline=False
                )
                embed.color = discord.Color.orange()
            
            # Adiciona rodapé
            embed.set_footer(text=f"ID do usuário: {member.id}")
            
            # Mensagem adicional (opcional)
            mensagem_boas_vindas = (
                f"Seja muito bem-vindo(a) {member.mention}! 🎊\n"
                f"Leia as regras em <#{CANAL_BOAS_VINDAS}> e divirta-se!"
            )
            
            try:
                await canal_boas_vindas.send(mensagem_boas_vindas, embed=embed)
                print(f'[{format_time()}] 📨 Mensagem de boas-vindas enviada para {member.name}')
            except Exception as e:
                print(f'[{format_time()}] ❌ Erro ao enviar mensagem de boas-vindas: {e}')
    else:
        print(f'[{format_time()}] ⚠️ Canal de boas-vindas (ID: {CANAL_BOAS_VINDAS}) não encontrado!')

@bot.event
async def on_member_remove(member):
    """Envia mensagem quando um membro sai"""
    
    canal_saida = member.guild.get_channel(CANAL_SAIDA)
    
    if canal_saida:
        # Verifica permissões do bot no canal
        permissoes = canal_saida.permissions_for(member.guild.me)
        
        if not permissoes.send_messages:
            print(f'[{format_time()}] ❌ Sem permissão para enviar mensagens no canal de saída')
        else:
            # Cria embed de saída
            embed = discord.Embed(
                title="👋 Um membro saiu do servidor...",
                description=f"**{member.name}** saiu de **{member.guild.name}**",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            # Adiciona thumbnail do avatar
            embed.set_thumbnail(url=get_member_join_image(member))
            
            # Adiciona campos de informação
            embed.add_field(
                name="📝 Informações",
                value=f"**Usuário:** {member.name}\n**ID:** `{member.id}`\n**Apelido:** {member.nick if member.nick else 'Nenhum'}",
                inline=True
            )
            
            # Tempo que o membro ficou no servidor (se disponível)
            if hasattr(member, 'joined_at') and member.joined_at:
                tempo_no_servidor = datetime.utcnow() - member.joined_at
                dias = tempo_no_servidor.days
                horas = tempo_no_servidor.seconds // 3600
                
                if dias > 0:
                    tempo_texto = f"{dias} dia(s) e {horas} hora(s)"
                else:
                    tempo_texto = f"{horas} hora(s)"
                
                embed.add_field(
                    name="⏱️ Tempo no servidor",
                    value=tempo_texto,
                    inline=True
                )
            
            # Adiciona contagem de membros
            embed.add_field(
                name="👥 Membros restantes",
                value=f"Agora somos **{member.guild.member_count}** membros",
                inline=False
            )
            
            # Lista de cargos que o membro tinha (se houver e se for relevante)
            if member.roles and len(member.roles) > 1:
                cargos_membro = [role.name for role in member.roles if role != member.guild.default_role]
                if cargos_membro:
                    embed.add_field(
                        name="🎖️ Cargos que possuía",
                        value=", ".join(cargos_membro[:5]),  # Limita a 5 cargos
                        inline=False
                    )
            
            # Adiciona rodapé
            embed.set_footer(text=f"ID do usuário: {member.id}")
            
            try:
                await canal_saida.send(embed=embed)
                print(f'[{format_time()}] 📨 Mensagem de saída enviada para {member.name}')
            except Exception as e:
                print(f'[{format_time()}] ❌ Erro ao enviar mensagem de saída: {e}')
    else:
        print(f'[{format_time()}] ⚠️ Canal de saída (ID: {CANAL_SAIDA}) não encontrado!')

# Comando para testar manualmente (apenas admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def testar_cargos(ctx, membro: discord.Member = None):
    """Testa a atribuição dos cargos em um membro específico"""
    membro = membro or ctx.author
    cargos_adicionados = []
    cargos_ja_possui = []
    cargos_erro = []
    
    for cargo_id in CARGO_IDS:
        cargo = ctx.guild.get_role(cargo_id)
        
        if cargo:
            if cargo in membro.roles:
                cargos_ja_possui.append(cargo.name)
            else:
                try:
                    await membro.add_roles(cargo)
                    cargos_adicionados.append(cargo.name)
                except discord.Forbidden:
                    cargos_erro.append(cargo.name)
        else:
            cargos_erro.append(f"ID {cargo_id} (não encontrado)")
    
    # Cria embed com resultado
    embed = discord.Embed(
        title="🎯 Teste de Atribuição de Cargos",
        description=f"Membro: {membro.mention}",
        color=discord.Color.blue()
    )
    
    if cargos_adicionados:
        embed.add_field(
            name="✅ Cargos adicionados",
            value="\n".join([f"✓ {cargo}" for cargo in cargos_adicionados]),
            inline=False
        )
    
    if cargos_ja_possui:
        embed.add_field(
            name="ℹ️ Cargos já existentes",
            value="\n".join([f"• {cargo}" for cargo in cargos_ja_possui]),
            inline=False
        )
    
    if cargos_erro:
        embed.add_field(
            name="❌ Erros",
            value="\n".join([f"✗ {erro}" for erro in cargos_erro]),
            inline=False
        )
        embed.color = discord.Color.red()
    
    await ctx.send(embed=embed)

# Comando para testar mensagens (apenas admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def testar_mensagens(ctx):
    """Testa o envio de mensagens de boas-vindas e saída"""
    embed = discord.Embed(
        title="🧪 Teste de Sistema",
        description="Testando canais configurados...",
        color=discord.Color.blue()
    )
    
    # Testa canal de boas-vindas
    canal_bv = ctx.guild.get_channel(CANAL_BOAS_VINDAS)
    canal_saida = ctx.guild.get_channel(CANAL_SAIDA)
    
    embed.add_field(
        name="Canal de Boas-Vindas",
        value=f"ID: `{CANAL_BOAS_VINDAS}`\nStatus: {'✅ Encontrado' if canal_bv else '❌ Não encontrado'}\nMencionável: {canal_bv.mention if canal_bv else 'N/A'}",
        inline=False
    )
    
    embed.add_field(
        name="Canal de Saída",
        value=f"ID: `{CANAL_SAIDA}`\nStatus: {'✅ Encontrado' if canal_saida else '❌ Não encontrado'}\nMencionável: {canal_saida.mention if canal_saida else 'N/A'}",
        inline=False
    )
    
    if canal_bv:
        try:
            await canal_bv.send("🧪 Teste de boas-vindas executado!")
            embed.add_field(name="✅ Boas-Vindas", value="Mensagem de teste enviada!", inline=False)
        except Exception as e:
            embed.add_field(name="❌ Boas-Vindas", value=f"Erro: {e}", inline=False)
    
    if canal_saida:
        try:
            await canal_saida.send("🧪 Teste de saída executado!")
            embed.add_field(name="✅ Saída", value="Mensagem de teste enviada!", inline=False)
        except Exception as e:
            embed.add_field(name="❌ Saída", value=f"Erro: {e}", inline=False)
    
    await ctx.send(embed=embed)

# Comando para verificar configuração
@bot.command()
@commands.has_permissions(administrator=True)
async def verificar_config(ctx):
    """Verifica todas as configurações do bot no servidor"""
    embed = discord.Embed(
        title="🔧 Configuração do Bot",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    # Verifica cargos
    cargos_info = []
    posicao_bot = ctx.guild.get_member(bot.user.id).top_role.position
    hierarquia_ok = True
    
    for i, cargo_id in enumerate(CARGO_IDS, 1):
        cargo = ctx.guild.get_role(cargo_id)
        if cargo:
            posicao_cargo = cargo.position
            hierarquia_valida = posicao_bot > posicao_cargo
            
            if not hierarquia_valida:
                hierarquia_ok = False
            
            status_hierarquia = "✅ OK" if hierarquia_valida else "⚠️ Bot precisa estar acima"
            cargos_info.append(f"**Cargo {i}:** {cargo.mention}\n└ Hierarquia: {status_hierarquia}")
        else:
            cargos_info.append(f"**Cargo {i}:** ❌ ID {cargo_id} não encontrado")
    
    embed.add_field(
        name=f"📋 Cargos ({len(CARGO_IDS)})",
        value="\n\n".join(cargos_info) if cargos_info else "Nenhum cargo configurado",
        inline=False
    )
    
    # Verifica canais
    canal_bv = ctx.guild.get_channel(CANAL_BOAS_VINDAS)
    canal_saida = ctx.guild.get_channel(CANAL_SAIDA)
    
    embed.add_field(
        name="📢 Canais Configurados",
        value=f"**Boas-Vindas:** {canal_bv.mention if canal_bv else f'❌ ID {CANAL_BOAS_VINDAS}'}\n**Saída:** {canal_saida.mention if canal_saida else f'❌ ID {CANAL_SAIDA}'}",
        inline=False
    )
    
    # Informações do bot
    embed.add_field(
        name="🤖 Informações do Bot",
        value=f"**Nome:** {bot.user.name}\n**ID:** `{bot.user.id}`\n**Cargo mais alto:** {ctx.guild.get_member(bot.user.id).top_role.mention}",
        inline=False
    )
    
    if not hierarquia_ok:
        embed.add_field(
            name="⚠️ Atenção - Hierarquia de Cargos",
            value="O bot precisa estar com um cargo **acima** de todos os cargos que ele vai atribuir!\n\n💡 Solução: Vá em Configurações do Servidor → Cargos e arraste o cargo do bot para cima dos outros.",
            inline=False
        )
        embed.color = discord.Color.orange()
    
    await ctx.send(embed=embed)

# Comando para listar todos os cargos do servidor (útil para debug)
@bot.command()
@commands.has_permissions(administrator=True)
async def listar_cargos(ctx):
    """Lista todos os cargos do servidor com seus IDs"""
    cargos = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
    
    embed = discord.Embed(
        title=f"📋 Cargos do Servidor - {ctx.guild.name}",
        description=f"Total: {len(cargos)} cargos",
        color=discord.Color.purple()
    )
    
    cargos_texto = []
    for cargo in cargos[:25]:
        destaque = "⭐ " if cargo.id in CARGO_IDS else ""
        cargos_texto.append(f"{destaque}{cargo.name}: `{cargo.id}` (Posição: {cargo.position})")
    
    embed.add_field(
        name="Cargos (do maior para o menor)",
        value="\n".join(cargos_texto) if cargos_texto else "Nenhum cargo encontrado",
        inline=False
    )
    
    if len(cargos) > 25:
        embed.set_footer(text=f"Mostrando 25 de {len(cargos)} cargos")
    
    await ctx.send(embed=embed)

# Comando para recarregar configuração (útil para testes)
@bot.command()
@commands.has_permissions(administrator=True)
async def recarregar_config(ctx):
    """Recarrega as configurações do .env"""
    load_dotenv(override=True)
    await ctx.send("🔄 Configurações recarregadas do .env!")
    print("[RECARREGAR] Configurações recarregadas via comando")

# Tratamento de erros
@testar_cargos.error
async def testar_cargos_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você precisa ser administrador para usar este comando!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membro não encontrado!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignora comandos inexistentes
    print(f"Erro no comando {ctx.command}: {error}")

# Inicia o bot
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido! Verifique o DISCORD_TOKEN no arquivo .env")
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")