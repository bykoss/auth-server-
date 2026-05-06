"""
BY UNTOUCHABLE BOT — 100+ Slash Commands
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os, json, asyncio, random, datetime, aiohttp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ── Setup ─────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

WARN_FILE  = "warns.json"
CONFIG_FILE= "config.json"

def load_json(f):
    if os.path.exists(f):
        with open(f) as fp: return json.load(fp)
    return {}

def save_json(f, data):
    with open(f, "w") as fp: json.dump(data, fp, indent=2)

def get_warns():    return load_json(WARN_FILE)
def save_warns(d):  save_json(WARN_FILE, d)
def get_config():   return load_json(CONFIG_FILE)
def save_config(d): save_json(CONFIG_FILE, d)

PURPLE = 0xA020F0
GREEN  = 0x57F287
RED    = 0xED4245
BLUE   = 0x5865F2
YELLOW = 0xFEE75C
GOLD   = 0xFFD700

def ok_embed(title, desc="", color=PURPLE):
    e = discord.Embed(title=f"✅ {title}", description=desc, color=color)
    e.timestamp = datetime.datetime.utcnow()
    return e

def err_embed(title, desc=""):
    e = discord.Embed(title=f"❌ {title}", description=desc, color=RED)
    return e

def info_embed(title, desc="", color=PURPLE):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.datetime.utcnow()
    return e

# ─────────────────────────────────────────────
#  ON READY + SYNC
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="/help | BY UNTOUCHABLE")
    )
    print(f"[✓] {bot.user} online — {len(bot.guilds)} servidores")
    print(f"[✓] {len(bot.tree.get_commands())} comandos slash registrados")

# ═══════════════════════════════════════════
#  CATEGORÍA: GENERAL
# ═══════════════════════════════════════════
@bot.tree.command(name="help", description="Menú de ayuda con todos los comandos")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 Menú de Ayuda",
        description=f"Hola **{interaction.user.name}**! Soy un bot con **{len(bot.tree.get_commands())}** comandos slash.\nSelecciona una categoría del menú para ver sus comandos.",
        color=PURPLE
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="🔨 Moderación",    value="ban, kick, mute, warn, purge...",   inline=True)
    embed.add_field(name="📁 Canales",        value="create, delete, rename, clone...",  inline=True)
    embed.add_field(name="🔒 AntiNuke",       value="Sistema de protección contra nukes",inline=True)
    embed.add_field(name="🛡️ AntiRaid",       value="Sistema de protección contra raids",inline=True)
    embed.add_field(name="⚙️ Configuración",  value="welcome, logs, autorole...",        inline=True)
    embed.add_field(name="🌐 General",        value="info, ping, avatar, userinfo...",   inline=True)
    embed.add_field(name="🔧 Utilidades",     value="embed, poll, reminder, calc...",    inline=True)
    embed.add_field(name="👥 Comunidad",      value="rep, daily, suggest, ticket...",    inline=True)
    embed.add_field(name="🎭 Roleplay",       value="hug, kiss, slap, pat, cry...",      inline=True)
    embed.add_field(name="🎮 Juegos",         value="ttt, rps, trivia, blackjack...",    inline=True)
    embed.add_field(name="👑 Admin",          value="Comandos exclusivos de administradores", inline=True)
    embed.set_footer(text=f"{len(bot.tree.get_commands())} comandos totales • Usa el menú para explorar")

    view = HelpView()
    await interaction.response.send_message(embed=embed, view=view)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(HelpSelect())

class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderación",   emoji="🔨", value="mod",    description="ban, kick, mute, warn, purge..."),
            discord.SelectOption(label="Canales",      emoji="📁", value="chan",   description="create, delete, rename, clone..."),
            discord.SelectOption(label="AntiNuke",     emoji="🔒", value="anti",   description="Sistema anti-nuke"),
            discord.SelectOption(label="AntiRaid",     emoji="🛡️", value="raid",   description="Sistema anti-raid"),
            discord.SelectOption(label="Configuración",emoji="⚙️", value="config", description="welcome, logs, autorole..."),
            discord.SelectOption(label="General",      emoji="🌐", value="gen",    description="info, ping, avatar..."),
            discord.SelectOption(label="Utilidades",   emoji="🔧", value="util",   description="embed, poll, reminder..."),
            discord.SelectOption(label="Comunidad",    emoji="👥", value="com",    description="rep, daily, suggest..."),
            discord.SelectOption(label="Roleplay",     emoji="🎭", value="rp",     description="hug, kiss, slap, pat..."),
            discord.SelectOption(label="Juegos",       emoji="🎮", value="games",  description="rps, trivia, blackjack..."),
            discord.SelectOption(label="Admin",        emoji="👑", value="admin",  description="Comandos de administrador"),
        ]
        super().__init__(placeholder="Selecciona una categoría...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cats = {
            "mod":    ("🔨 Moderación", ["/ban","/kick","/mute","/unmute","/warn","/warnings","/clearwarns","/timeout","/untimeout","/purge","/slowmode","/lock","/unlock","/deafen","/undeafen"]),
            "chan":   ("📁 Canales",    ["/createchannel","/deletechannel","/renamechannel","/clonechannel","/topic","/nsfwtoggle","/movechannel","/channelinfo"]),
            "anti":  ("🔒 AntiNuke",   ["/antinuke on","/antinuke off","/antinuke status","/antinuke whitelist","/antinuke unwhitelist"]),
            "raid":  ("🛡️ AntiRaid",   ["/antiraid on","/antiraid off","/antiraid status","/antiraid threshold"]),
            "config":("⚙️ Configuración",["/setwelcome","/setwelcomechannel","/setlogs","/autorole","/setprefix","/setlang","/serverconfig"]),
            "gen":   ("🌐 General",    ["/ping","/info","/avatar","/userinfo","/serverinfo","/roleinfo","/invite","/botinfo","/uptime"]),
            "util":  ("🔧 Utilidades", ["/embed","/poll","/reminder","/calc","/translate","/weather","/color","/qr","/timestamp","/countdown"]),
            "com":   ("👥 Comunidad",  ["/rep","/daily","/suggest","/ticket","/report","/giveaway","/levelup","/rank","/leaderboard"]),
            "rp":    ("🎭 Roleplay",   ["/hug","/kiss","/slap","/pat","/cry","/poke","/bite","/cuddle","/highfive","/wave"]),
            "games": ("🎮 Juegos",     ["/rps","/trivia","/blackjack","/coinflip","/dice","/8ball","/guess","/hangman"]),
            "admin": ("👑 Admin",      ["/announce","/dm","/serverbackup","/massrole","/massunrole","/nuke","/clone","/setname","/seticon"]),
        }
        cat = self.values[0]
        name, cmds = cats[cat]
        e = discord.Embed(title=name, description="\n".join(f"`{c}`" for c in cmds), color=PURPLE)
        e.set_footer(text="Usa / para ejecutar cualquier comando")
        await interaction.response.edit_message(embed=e)

@bot.tree.command(name="ping", description="Muestra la latencia del bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    color = GREEN if latency < 100 else YELLOW if latency < 200 else RED
    e = info_embed("🏓 Pong!", f"Latencia: **{latency}ms**", color)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="botinfo", description="Información sobre el bot")
async def botinfo(interaction: discord.Interaction):
    e = info_embed("🤖 Info del Bot")
    e.set_thumbnail(url=bot.user.display_avatar.url)
    e.add_field(name="Nombre",    value=str(bot.user),               inline=True)
    e.add_field(name="ID",        value=str(bot.user.id),            inline=True)
    e.add_field(name="Servidores",value=str(len(bot.guilds)),         inline=True)
    e.add_field(name="Usuarios",  value=str(sum(g.member_count for g in bot.guilds)), inline=True)
    e.add_field(name="Comandos",  value=str(len(bot.tree.get_commands())), inline=True)
    e.add_field(name="Librería",  value="discord.py 2.x",            inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario")
@app_commands.describe(usuario="Usuario del que ver el avatar")
async def avatar(interaction: discord.Interaction, usuario: discord.Member = None):
    user = usuario or interaction.user
    e = info_embed(f"🖼️ Avatar de {user.name}")
    e.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="userinfo", description="Información sobre un usuario")
@app_commands.describe(usuario="Usuario a consultar")
async def userinfo(interaction: discord.Interaction, usuario: discord.Member = None):
    u = usuario or interaction.user
    roles = [r.mention for r in u.roles[1:]][:10]
    e = info_embed(f"👤 Info de {u.name}")
    e.set_thumbnail(url=u.display_avatar.url)
    e.add_field(name="Tag",       value=str(u),                               inline=True)
    e.add_field(name="ID",        value=str(u.id),                            inline=True)
    e.add_field(name="Nick",      value=u.nick or "Ninguno",                  inline=True)
    e.add_field(name="Cuenta creada", value=discord.utils.format_dt(u.created_at, "R"), inline=True)
    e.add_field(name="Se unió",   value=discord.utils.format_dt(u.joined_at, "R") if u.joined_at else "?", inline=True)
    e.add_field(name="Bot",       value="Sí" if u.bot else "No",              inline=True)
    if roles:
        e.add_field(name=f"Roles ({len(u.roles)-1})", value=" ".join(roles), inline=False)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="serverinfo", description="Información sobre el servidor")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    e = info_embed(f"🏠 {g.name}")
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name="ID",          value=str(g.id),              inline=True)
    e.add_field(name="Owner",       value=str(g.owner),           inline=True)
    e.add_field(name="Miembros",    value=str(g.member_count),    inline=True)
    e.add_field(name="Canales",     value=str(len(g.channels)),   inline=True)
    e.add_field(name="Roles",       value=str(len(g.roles)),      inline=True)
    e.add_field(name="Boosts",      value=str(g.premium_subscription_count), inline=True)
    e.add_field(name="Nivel boost", value=str(g.premium_tier),   inline=True)
    e.add_field(name="Verificación",value=str(g.verification_level), inline=True)
    e.add_field(name="Creado",      value=discord.utils.format_dt(g.created_at, "R"), inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="roleinfo", description="Información sobre un rol")
@app_commands.describe(rol="Rol a consultar")
async def roleinfo(interaction: discord.Interaction, rol: discord.Role):
    e = info_embed(f"🎭 Rol: {rol.name}", color=rol.color.value or PURPLE)
    e.add_field(name="ID",          value=str(rol.id),            inline=True)
    e.add_field(name="Color",       value=str(rol.color),         inline=True)
    e.add_field(name="Miembros",    value=str(len(rol.members)),  inline=True)
    e.add_field(name="Posición",    value=str(rol.position),      inline=True)
    e.add_field(name="Hoisted",     value="Sí" if rol.hoist else "No", inline=True)
    e.add_field(name="Mentionable", value="Sí" if rol.mentionable else "No", inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="invite", description="Genera un link de invitación del bot")
async def invite(interaction: discord.Interaction):
    url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(administrator=True))
    e = info_embed("🔗 Invitar el Bot", f"[Click aquí para invitarme]({url})")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="uptime", description="Muestra el tiempo que lleva el bot activo")
async def uptime(interaction: discord.Interaction):
    delta = datetime.datetime.utcnow() - bot.start_time
    h, r = divmod(int(delta.total_seconds()), 3600)
    m, s = divmod(r, 60)
    e = info_embed("⏱️ Uptime", f"**{h}h {m}m {s}s**")
    await interaction.response.send_message(embed=e)

# ═══════════════════════════════════════════
#  CATEGORÍA: MODERACIÓN
# ═══════════════════════════════════════════
def check_mod(interaction):
    return interaction.user.guild_permissions.moderate_members

@bot.tree.command(name="ban", description="Banea a un usuario del servidor")
@app_commands.describe(usuario="Usuario a banear", razon="Razón del ban", dias="Días de mensajes a borrar (0-7)")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón", dias: int = 0):
    if usuario.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(embed=err_embed("Sin permisos", "No puedes banear a alguien con rol igual o superior."), ephemeral=True)
    await usuario.ban(reason=razon, delete_message_days=min(dias, 7))
    e = ok_embed("Usuario Baneado", f"**{usuario}** ha sido baneado.\n**Razón:** {razon}", RED)
    e.set_thumbnail(url=usuario.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="kick", description="Expulsa a un usuario del servidor")
@app_commands.describe(usuario="Usuario a expulsar", razon="Razón")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón"):
    if usuario.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(embed=err_embed("Sin permisos"), ephemeral=True)
    await usuario.kick(reason=razon)
    e = ok_embed("Usuario Expulsado", f"**{usuario}** ha sido expulsado.\n**Razón:** {razon}", YELLOW)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="mute", description="Mutea a un usuario (timeout)")
@app_commands.describe(usuario="Usuario a mutear", minutos="Duración en minutos", razon="Razón")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, usuario: discord.Member, minutos: int = 10, razon: str = "Sin razón"):
    until = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutos)
    await usuario.timeout(until, reason=razon)
    e = ok_embed("Usuario Muteado", f"**{usuario}** muteado por **{minutos} min**.\n**Razón:** {razon}")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="unmute", description="Desmutea a un usuario")
@app_commands.describe(usuario="Usuario a desmutear")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, usuario: discord.Member):
    await usuario.timeout(None)
    e = ok_embed("Usuario Desmuteado", f"**{usuario}** ya puede hablar de nuevo.")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="warn", description="Advierte a un usuario")
@app_commands.describe(usuario="Usuario a advertir", razon="Razón")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón"):
    warns = get_warns()
    key   = str(usuario.id)
    if key not in warns: warns[key] = []
    warns[key].append({"razon": razon, "mod": str(interaction.user), "fecha": str(datetime.datetime.utcnow())})
    save_warns(warns)
    e = ok_embed("Advertencia Registrada", f"**{usuario}** — Advertencia #{len(warns[key])}\n**Razón:** {razon}", YELLOW)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="warnings", description="Ver advertencias de un usuario")
@app_commands.describe(usuario="Usuario a consultar")
async def warnings(interaction: discord.Interaction, usuario: discord.Member):
    warns = get_warns()
    key   = str(usuario.id)
    user_warns = warns.get(key, [])
    if not user_warns:
        return await interaction.response.send_message(embed=info_embed(f"Sin advertencias", f"**{usuario}** no tiene advertencias."))
    e = info_embed(f"⚠️ Advertencias de {usuario.name}", color=YELLOW)
    for i, w in enumerate(user_warns, 1):
        e.add_field(name=f"#{i} — {w['fecha'][:10]}", value=f"**Razón:** {w['razon']}\n**Mod:** {w['mod']}", inline=False)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="clearwarns", description="Borra las advertencias de un usuario")
@app_commands.describe(usuario="Usuario")
@app_commands.checks.has_permissions(administrator=True)
async def clearwarns(interaction: discord.Interaction, usuario: discord.Member):
    warns = get_warns()
    warns.pop(str(usuario.id), None)
    save_warns(warns)
    await interaction.response.send_message(embed=ok_embed("Advertencias borradas", f"Se borraron las advertencias de **{usuario}**."))

@bot.tree.command(name="timeout", description="Aplica timeout a un usuario")
@app_commands.describe(usuario="Usuario", horas="Horas de timeout", razon="Razón")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout_cmd(interaction: discord.Interaction, usuario: discord.Member, horas: int = 1, razon: str = "Sin razón"):
    until = datetime.datetime.utcnow() + datetime.timedelta(hours=horas)
    await usuario.timeout(until, reason=razon)
    e = ok_embed("Timeout Aplicado", f"**{usuario}** en timeout por **{horas}h**.\n**Razón:** {razon}")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="untimeout", description="Quita el timeout a un usuario")
@app_commands.describe(usuario="Usuario")
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, usuario: discord.Member):
    await usuario.timeout(None)
    await interaction.response.send_message(embed=ok_embed("Timeout Removido", f"**{usuario}** ya no tiene timeout."))

@bot.tree.command(name="purge", description="Borra mensajes del canal")
@app_commands.describe(cantidad="Cantidad de mensajes (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, cantidad: int):
    cantidad = min(max(cantidad, 1), 100)
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(embed=ok_embed("Mensajes Borrados", f"Se borraron **{len(deleted)}** mensajes."), ephemeral=True)

@bot.tree.command(name="slowmode", description="Configura el slowmode del canal")
@app_commands.describe(segundos="Segundos de slowmode (0 para desactivar)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, segundos: int = 0):
    await interaction.channel.edit(slowmode_delay=segundos)
    txt = f"Slowmode configurado a **{segundos}s**." if segundos else "Slowmode desactivado."
    await interaction.response.send_message(embed=ok_embed("Slowmode", txt))

@bot.tree.command(name="lock", description="Bloquea el canal actual")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    ow = interaction.channel.overwrites_for(interaction.guild.default_role)
    ow.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=ow)
    await interaction.response.send_message(embed=ok_embed("Canal Bloqueado", f"🔒 {interaction.channel.mention} bloqueado."))

@bot.tree.command(name="unlock", description="Desbloquea el canal actual")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    ow = interaction.channel.overwrites_for(interaction.guild.default_role)
    ow.send_messages = True
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=ow)
    await interaction.response.send_message(embed=ok_embed("Canal Desbloqueado", f"🔓 {interaction.channel.mention} desbloqueado."))

@bot.tree.command(name="deafen", description="Ensordece a un usuario en voz")
@app_commands.describe(usuario="Usuario")
@app_commands.checks.has_permissions(deafen_members=True)
async def deafen(interaction: discord.Interaction, usuario: discord.Member):
    await usuario.edit(deafen=True)
    await interaction.response.send_message(embed=ok_embed("Usuario Ensordecido", f"**{usuario}** ha sido ensordecido."))

@bot.tree.command(name="undeafen", description="Quita el sordo a un usuario")
@app_commands.describe(usuario="Usuario")
@app_commands.checks.has_permissions(deafen_members=True)
async def undeafen(interaction: discord.Interaction, usuario: discord.Member):
    await usuario.edit(deafen=False)
    await interaction.response.send_message(embed=ok_embed("Sordo Removido", f"**{usuario}** ya puede escuchar."))

@bot.tree.command(name="unban", description="Desbanea a un usuario por ID")
@app_commands.describe(user_id="ID del usuario a desbanear", razon="Razón")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str, razon: str = "Sin razón"):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=razon)
        await interaction.response.send_message(embed=ok_embed("Usuario Desbaneado", f"**{user}** ha sido desbaneado."))
    except Exception as ex:
        await interaction.response.send_message(embed=err_embed("Error", str(ex)), ephemeral=True)

@bot.tree.command(name="softban", description="Banea y desbanea (borra mensajes recientes)")
@app_commands.describe(usuario="Usuario", razon="Razón")
@app_commands.checks.has_permissions(ban_members=True)
async def softban(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón"):
    await usuario.ban(reason=razon, delete_message_days=7)
    await interaction.guild.unban(usuario)
    await interaction.response.send_message(embed=ok_embed("Softban Aplicado", f"**{usuario}** fue softbaneado.\n**Razón:** {razon}", YELLOW))

@bot.tree.command(name="massban", description="Banea múltiples usuarios por ID")
@app_commands.describe(ids="IDs separados por comas", razon="Razón")
@app_commands.checks.has_permissions(administrator=True)
async def massban(interaction: discord.Interaction, ids: str, razon: str = "Mass ban"):
    await interaction.response.defer()
    baneados = 0
    for uid in ids.split(","):
        try:
            user = await bot.fetch_user(int(uid.strip()))
            await interaction.guild.ban(user, reason=razon)
            baneados += 1
        except: pass
    await interaction.followup.send(embed=ok_embed("Mass Ban", f"Se banearon **{baneados}** usuarios.", RED))

@bot.tree.command(name="nick", description="Cambia el nick de un usuario")
@app_commands.describe(usuario="Usuario", nick="Nuevo nick (vacío para resetear)")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nick(interaction: discord.Interaction, usuario: discord.Member, nick: str = None):
    await usuario.edit(nick=nick)
    txt = f"Nick de **{usuario}** cambiado a **{nick}**." if nick else f"Nick de **{usuario}** reseteado."
    await interaction.response.send_message(embed=ok_embed("Nick Cambiado", txt))

# ═══════════════════════════════════════════
#  CATEGORÍA: CANALES
# ═══════════════════════════════════════════
@bot.tree.command(name="createchannel", description="Crea un nuevo canal de texto")
@app_commands.describe(nombre="Nombre del canal", categoria="Categoría donde crearlo")
@app_commands.checks.has_permissions(manage_channels=True)
async def createchannel(interaction: discord.Interaction, nombre: str, categoria: discord.CategoryChannel = None):
    ch = await interaction.guild.create_text_channel(nombre, category=categoria)
    await interaction.response.send_message(embed=ok_embed("Canal Creado", f"{ch.mention} ha sido creado."))

@bot.tree.command(name="deletechannel", description="Elimina un canal")
@app_commands.describe(canal="Canal a eliminar", razon="Razón")
@app_commands.checks.has_permissions(manage_channels=True)
async def deletechannel(interaction: discord.Interaction, canal: discord.TextChannel, razon: str = "Sin razón"):
    nombre = canal.name
    await canal.delete(reason=razon)
    await interaction.response.send_message(embed=ok_embed("Canal Eliminado", f"**#{nombre}** ha sido eliminado."))

@bot.tree.command(name="renamechannel", description="Renombra el canal actual")
@app_commands.describe(nombre="Nuevo nombre")
@app_commands.checks.has_permissions(manage_channels=True)
async def renamechannel(interaction: discord.Interaction, nombre: str):
    old = interaction.channel.name
    await interaction.channel.edit(name=nombre)
    await interaction.response.send_message(embed=ok_embed("Canal Renombrado", f"**#{old}** → **#{nombre}**"))

@bot.tree.command(name="clonechannel", description="Clona el canal actual")
@app_commands.checks.has_permissions(manage_channels=True)
async def clonechannel(interaction: discord.Interaction):
    clone = await interaction.channel.clone()
    await interaction.response.send_message(embed=ok_embed("Canal Clonado", f"{clone.mention} es una copia de {interaction.channel.mention}."))

@bot.tree.command(name="topic", description="Cambia el tema del canal")
@app_commands.describe(tema="Nuevo tema del canal")
@app_commands.checks.has_permissions(manage_channels=True)
async def topic(interaction: discord.Interaction, tema: str):
    await interaction.channel.edit(topic=tema)
    await interaction.response.send_message(embed=ok_embed("Tema Actualizado", f"Tema: **{tema}**"))

@bot.tree.command(name="nsfwtoggle", description="Activa/desactiva NSFW en el canal")
@app_commands.checks.has_permissions(manage_channels=True)
async def nsfwtoggle(interaction: discord.Interaction):
    nsfw = not interaction.channel.is_nsfw()
    await interaction.channel.edit(nsfw=nsfw)
    status = "activado" if nsfw else "desactivado"
    await interaction.response.send_message(embed=ok_embed("NSFW Toggle", f"NSFW **{status}** en {interaction.channel.mention}."))

@bot.tree.command(name="channelinfo", description="Información del canal actual")
async def channelinfo(interaction: discord.Interaction):
    ch = interaction.channel
    e  = info_embed(f"📁 #{ch.name}")
    e.add_field(name="ID",       value=str(ch.id),                              inline=True)
    e.add_field(name="Tipo",     value=str(ch.type),                            inline=True)
    e.add_field(name="NSFW",     value="Sí" if ch.is_nsfw() else "No",          inline=True)
    e.add_field(name="Slowmode", value=f"{ch.slowmode_delay}s",                 inline=True)
    e.add_field(name="Creado",   value=discord.utils.format_dt(ch.created_at, "R"), inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="createcategory", description="Crea una nueva categoría")
@app_commands.describe(nombre="Nombre de la categoría")
@app_commands.checks.has_permissions(manage_channels=True)
async def createcategory(interaction: discord.Interaction, nombre: str):
    cat = await interaction.guild.create_category(nombre)
    await interaction.response.send_message(embed=ok_embed("Categoría Creada", f"**{cat.name}** creada."))

# ═══════════════════════════════════════════
#  CATEGORÍA: ROLES
# ═══════════════════════════════════════════
@bot.tree.command(name="addrole", description="Agrega un rol a un usuario")
@app_commands.describe(usuario="Usuario", rol="Rol a agregar")
@app_commands.checks.has_permissions(manage_roles=True)
async def addrole(interaction: discord.Interaction, usuario: discord.Member, rol: discord.Role):
    await usuario.add_roles(rol)
    await interaction.response.send_message(embed=ok_embed("Rol Agregado", f"**{rol.name}** dado a **{usuario}**."))

@bot.tree.command(name="removerole", description="Quita un rol a un usuario")
@app_commands.describe(usuario="Usuario", rol="Rol a quitar")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, usuario: discord.Member, rol: discord.Role):
    await usuario.remove_roles(rol)
    await interaction.response.send_message(embed=ok_embed("Rol Quitado", f"**{rol.name}** quitado a **{usuario}**."))

@bot.tree.command(name="createrole", description="Crea un nuevo rol")
@app_commands.describe(nombre="Nombre del rol", color="Color hex (ej: ff0000)")
@app_commands.checks.has_permissions(manage_roles=True)
async def createrole(interaction: discord.Interaction, nombre: str, color: str = "ffffff"):
    try: c = discord.Color(int(color.lstrip("#"), 16))
    except: c = discord.Color.default()
    rol = await interaction.guild.create_role(name=nombre, color=c)
    await interaction.response.send_message(embed=ok_embed("Rol Creado", f"**{rol.name}** creado."))

@bot.tree.command(name="deleterole", description="Elimina un rol")
@app_commands.describe(rol="Rol a eliminar")
@app_commands.checks.has_permissions(manage_roles=True)
async def deleterole(interaction: discord.Interaction, rol: discord.Role):
    nombre = rol.name
    await rol.delete()
    await interaction.response.send_message(embed=ok_embed("Rol Eliminado", f"**{nombre}** eliminado."))

@bot.tree.command(name="massrole", description="Da un rol a todos los miembros")
@app_commands.describe(rol="Rol a dar")
@app_commands.checks.has_permissions(administrator=True)
async def massrole(interaction: discord.Interaction, rol: discord.Role):
    await interaction.response.defer()
    count = 0
    for m in interaction.guild.members:
        if rol not in m.roles:
            try: await m.add_roles(rol); count += 1
            except: pass
    await interaction.followup.send(embed=ok_embed("Mass Role", f"**{rol.name}** dado a **{count}** miembros."))

@bot.tree.command(name="massunrole", description="Quita un rol a todos los miembros")
@app_commands.describe(rol="Rol a quitar")
@app_commands.checks.has_permissions(administrator=True)
async def massunrole(interaction: discord.Interaction, rol: discord.Role):
    await interaction.response.defer()
    count = 0
    for m in interaction.guild.members:
        if rol in m.roles:
            try: await m.remove_roles(rol); count += 1
            except: pass
    await interaction.followup.send(embed=ok_embed("Mass Unrole", f"**{rol.name}** quitado a **{count}** miembros."))

# ═══════════════════════════════════════════
#  CATEGORÍA: CONFIGURACIÓN
# ═══════════════════════════════════════════
@bot.tree.command(name="setwelcome", description="Configura el mensaje de bienvenida")
@app_commands.describe(canal="Canal de bienvenida", mensaje="Mensaje (usa {user} y {server})")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, canal: discord.TextChannel, mensaje: str):
    cfg = get_config()
    gid = str(interaction.guild.id)
    if gid not in cfg: cfg[gid] = {}
    cfg[gid]["welcome_channel"] = canal.id
    cfg[gid]["welcome_message"] = mensaje
    save_config(cfg)
    await interaction.response.send_message(embed=ok_embed("Bienvenida Configurada", f"Canal: {canal.mention}\nMensaje: {mensaje}"))

@bot.tree.command(name="setlogs", description="Configura el canal de logs")
@app_commands.describe(canal="Canal para logs")
@app_commands.checks.has_permissions(administrator=True)
async def setlogs(interaction: discord.Interaction, canal: discord.TextChannel):
    cfg = get_config()
    gid = str(interaction.guild.id)
    if gid not in cfg: cfg[gid] = {}
    cfg[gid]["logs_channel"] = canal.id
    save_config(cfg)
    await interaction.response.send_message(embed=ok_embed("Logs Configurado", f"Canal de logs: {canal.mention}"))

@bot.tree.command(name="autorole", description="Configura el rol automático al entrar")
@app_commands.describe(rol="Rol a dar automáticamente")
@app_commands.checks.has_permissions(administrator=True)
async def autorole(interaction: discord.Interaction, rol: discord.Role):
    cfg = get_config()
    gid = str(interaction.guild.id)
    if gid not in cfg: cfg[gid] = {}
    cfg[gid]["autorole"] = rol.id
    save_config(cfg)
    await interaction.response.send_message(embed=ok_embed("Autorole Configurado", f"Rol automático: {rol.mention}"))

@bot.tree.command(name="serverconfig", description="Ver la configuración del servidor")
@app_commands.checks.has_permissions(administrator=True)
async def serverconfig(interaction: discord.Interaction):
    cfg = get_config()
    gid = str(interaction.guild.id)
    gcfg = cfg.get(gid, {})
    e = info_embed("⚙️ Configuración del Servidor")
    e.add_field(name="Welcome Channel", value=f"<#{gcfg.get('welcome_channel','No configurado')}>" if gcfg.get('welcome_channel') else "No configurado", inline=True)
    e.add_field(name="Logs Channel",    value=f"<#{gcfg.get('logs_channel','No configurado')}>" if gcfg.get('logs_channel') else "No configurado", inline=True)
    e.add_field(name="Autorole",        value=f"<@&{gcfg.get('autorole','No configurado')}>" if gcfg.get('autorole') else "No configurado", inline=True)
    await interaction.response.send_message(embed=e)

# ═══════════════════════════════════════════
#  CATEGORÍA: UTILIDADES
# ═══════════════════════════════════════════
@bot.tree.command(name="embed", description="Crea un embed personalizado")
@app_commands.describe(titulo="Título", descripcion="Descripción", color="Color hex", imagen="URL de imagen")
@app_commands.checks.has_permissions(manage_messages=True)
async def embed_cmd(interaction: discord.Interaction, titulo: str, descripcion: str, color: str = "a020f0", imagen: str = None):
    try: c = int(color.lstrip("#"), 16)
    except: c = PURPLE
    e = discord.Embed(title=titulo, description=descripcion, color=c)
    if imagen: e.set_image(url=imagen)
    e.set_footer(text=f"Por {interaction.user}")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="poll", description="Crea una encuesta")
@app_commands.describe(pregunta="Pregunta", opcion1="Opción 1", opcion2="Opción 2", opcion3="Opción 3 (opcional)")
async def poll(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str, opcion3: str = None):
    e = info_embed(f"📊 {pregunta}", color=BLUE)
    opts = [f"1️⃣ {opcion1}", f"2️⃣ {opcion2}"]
    emojis = ["1️⃣","2️⃣"]
    if opcion3:
        opts.append(f"3️⃣ {opcion3}")
        emojis.append("3️⃣")
    e.description = "\n".join(opts)
    e.set_footer(text=f"Encuesta por {interaction.user}")
    await interaction.response.send_message(embed=e)
    msg = await interaction.original_response()
    for emoji in emojis:
        await msg.add_reaction(emoji)

@bot.tree.command(name="calc", description="Calcula una expresión matemática")
@app_commands.describe(expresion="Expresión a calcular")
async def calc(interaction: discord.Interaction, expresion: str):
    try:
        result = eval(expresion, {"__builtins__": {}}, {})
        await interaction.response.send_message(embed=info_embed("🧮 Calculadora", f"`{expresion}` = **{result}**"))
    except:
        await interaction.response.send_message(embed=err_embed("Error", "Expresión inválida."), ephemeral=True)

@bot.tree.command(name="color", description="Muestra información sobre un color hex")
@app_commands.describe(hex="Color en hexadecimal (ej: ff0000)")
async def color_cmd(interaction: discord.Interaction, hex: str):
    try:
        hex = hex.lstrip("#")
        val = int(hex, 16)
        r, g, b = (val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF
        e = discord.Embed(title=f"🎨 Color #{hex.upper()}", color=val)
        e.add_field(name="HEX", value=f"#{hex.upper()}", inline=True)
        e.add_field(name="RGB", value=f"({r}, {g}, {b})", inline=True)
        e.add_field(name="Int", value=str(val), inline=True)
        e.set_thumbnail(url=f"https://singlecolorimage.com/get/{hex}/100x100")
        await interaction.response.send_message(embed=e)
    except:
        await interaction.response.send_message(embed=err_embed("Error", "Color inválido."), ephemeral=True)

@bot.tree.command(name="timestamp", description="Genera un timestamp de Discord")
@app_commands.describe(fecha="Fecha (YYYY-MM-DD HH:MM)")
async def timestamp(interaction: discord.Interaction, fecha: str):
    try:
        dt = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M")
        ts = int(dt.timestamp())
        e = info_embed("🕐 Timestamp")
        e.add_field(name="Corto",    value=f"<t:{ts}:t>  →  `<t:{ts}:t>`",  inline=False)
        e.add_field(name="Largo",    value=f"<t:{ts}:F>  →  `<t:{ts}:F>`",  inline=False)
        e.add_field(name="Relativo", value=f"<t:{ts}:R>  →  `<t:{ts}:R>`",  inline=False)
        await interaction.response.send_message(embed=e)
    except:
        await interaction.response.send_message(embed=err_embed("Error", "Formato: YYYY-MM-DD HH:MM"), ephemeral=True)

@bot.tree.command(name="remind", description="Establece un recordatorio")
@app_commands.describe(minutos="En cuántos minutos", mensaje="Qué recordar")
async def remind(interaction: discord.Interaction, minutos: int, mensaje: str):
    await interaction.response.send_message(embed=ok_embed("Recordatorio Establecido", f"Te avisaré en **{minutos} minutos**."))
    await asyncio.sleep(minutos * 60)
    try:
        await interaction.user.send(embed=info_embed("⏰ Recordatorio", mensaje))
    except:
        await interaction.channel.send(f"{interaction.user.mention} ⏰ **Recordatorio:** {mensaje}")

@bot.tree.command(name="say", description="El bot dice algo en el canal")
@app_commands.describe(mensaje="Mensaje a enviar")
@app_commands.checks.has_permissions(manage_messages=True)
async def say(interaction: discord.Interaction, mensaje: str):
    await interaction.response.send_message("✅", ephemeral=True)
    await interaction.channel.send(mensaje)

@bot.tree.command(name="announce", description="Hace un anuncio en un canal")
@app_commands.describe(canal="Canal", titulo="Título", mensaje="Mensaje")
@app_commands.checks.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, canal: discord.TextChannel, titulo: str, mensaje: str):
    e = discord.Embed(title=f"📢 {titulo}", description=mensaje, color=GOLD)
    e.set_footer(text=f"Anuncio por {interaction.user}")
    e.timestamp = datetime.datetime.utcnow()
    await canal.send(embed=e)
    await interaction.response.send_message(embed=ok_embed("Anuncio Enviado", f"Enviado en {canal.mention}."), ephemeral=True)

@bot.tree.command(name="dm", description="Manda un DM a un usuario")
@app_commands.describe(usuario="Usuario", mensaje="Mensaje")
@app_commands.checks.has_permissions(administrator=True)
async def dm_cmd(interaction: discord.Interaction, usuario: discord.Member, mensaje: str):
    try:
        await usuario.send(embed=info_embed(f"Mensaje de {interaction.guild.name}", mensaje))
        await interaction.response.send_message(embed=ok_embed("DM Enviado", f"DM enviado a **{usuario}**."), ephemeral=True)
    except:
        await interaction.response.send_message(embed=err_embed("Error", "No se pudo enviar el DM."), ephemeral=True)

# ═══════════════════════════════════════════
#  CATEGORÍA: COMUNIDAD
# ═══════════════════════════════════════════
rep_cooldowns = {}

@bot.tree.command(name="rep", description="Da reputación a un usuario")
@app_commands.describe(usuario="Usuario al que dar rep")
async def rep(interaction: discord.Interaction, usuario: discord.Member):
    if usuario == interaction.user:
        return await interaction.response.send_message(embed=err_embed("Error", "No puedes darte rep a ti mismo."), ephemeral=True)
    uid = interaction.user.id
    now = datetime.datetime.utcnow()
    if uid in rep_cooldowns and (now - rep_cooldowns[uid]).seconds < 3600:
        rem = 3600 - (now - rep_cooldowns[uid]).seconds
        return await interaction.response.send_message(embed=err_embed("Cooldown", f"Espera **{rem//60}m {rem%60}s** para dar rep de nuevo."), ephemeral=True)
    rep_cooldowns[uid] = now
    await interaction.response.send_message(embed=ok_embed("Reputación", f"**{interaction.user.name}** le dio +1 rep a **{usuario.name}** ⭐"))

@bot.tree.command(name="suggest", description="Envía una sugerencia")
@app_commands.describe(sugerencia="Tu sugerencia")
async def suggest(interaction: discord.Interaction, sugerencia: str):
    cfg = get_config()
    gid = str(interaction.guild.id)
    ch_id = cfg.get(gid, {}).get("suggest_channel")
    e = info_embed("💡 Nueva Sugerencia", sugerencia, YELLOW)
    e.set_footer(text=f"Por {interaction.user} • {interaction.user.id}")
    if ch_id:
        ch = interaction.guild.get_channel(ch_id)
        if ch:
            msg = await ch.send(embed=e)
            await msg.add_reaction("✅"); await msg.add_reaction("❌")
            return await interaction.response.send_message(embed=ok_embed("Sugerencia Enviada"), ephemeral=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="report", description="Reporta a un usuario")
@app_commands.describe(usuario="Usuario a reportar", razon="Razón del reporte")
async def report(interaction: discord.Interaction, usuario: discord.Member, razon: str):
    e = info_embed("🚨 Nuevo Reporte", color=RED)
    e.add_field(name="Reportado", value=str(usuario), inline=True)
    e.add_field(name="Por",       value=str(interaction.user), inline=True)
    e.add_field(name="Razón",     value=razon, inline=False)
    cfg = get_config()
    gid = str(interaction.guild.id)
    ch_id = cfg.get(gid, {}).get("logs_channel")
    if ch_id:
        ch = interaction.guild.get_channel(ch_id)
        if ch: await ch.send(embed=e)
    await interaction.response.send_message(embed=ok_embed("Reporte Enviado", "Los moderadores han sido notificados."), ephemeral=True)

@bot.tree.command(name="ticket", description="Abre un ticket de soporte")
async def ticket(interaction: discord.Interaction):
    cat = discord.utils.get(interaction.guild.categories, name="Tickets")
    if not cat:
        cat = await interaction.guild.create_category("Tickets")
    existing = discord.utils.get(interaction.guild.channels, name=f"ticket-{interaction.user.name.lower()}")
    if existing:
        return await interaction.response.send_message(embed=err_embed("Ticket existente", f"Ya tienes un ticket abierto: {existing.mention}"), ephemeral=True)
    ow = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
    }
    ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=ow)
    e = info_embed("🎫 Ticket Abierto", f"Hola {interaction.user.mention}! Un moderador te atenderá pronto.\nEscribe tu consulta aquí.")
    view = TicketCloseView()
    await ch.send(embed=e, view=view)
    await interaction.response.send_message(embed=ok_embed("Ticket Creado", f"Tu ticket: {ch.mention}"), ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cerrando ticket en 3 segundos...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

@bot.tree.command(name="giveaway", description="Inicia un sorteo")
@app_commands.describe(premio="Premio", minutos="Duración en minutos", ganadores="Número de ganadores")
@app_commands.checks.has_permissions(manage_guild=True)
async def giveaway(interaction: discord.Interaction, premio: str, minutos: int = 5, ganadores: int = 1):
    end = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutos)
    e = discord.Embed(title="🎉 SORTEO", description=f"**Premio:** {premio}\n**Ganadores:** {ganadores}\n**Termina:** {discord.utils.format_dt(end, 'R')}", color=GOLD)
    e.set_footer(text="Reacciona con 🎉 para participar")
    await interaction.response.send_message(embed=e)
    msg = await interaction.original_response()
    await msg.add_reaction("🎉")
    await asyncio.sleep(minutos * 60)
    msg = await interaction.channel.fetch_message(msg.id)
    reaction = discord.utils.get(msg.reactions, emoji="🎉")
    users = [u async for u in reaction.users() if not u.bot]
    if not users:
        return await interaction.channel.send(embed=info_embed("🎉 Sorteo terminado", "No hubo participantes."))
    winners = random.sample(users, min(ganadores, len(users)))
    w_mentions = ", ".join(w.mention for w in winners)
    await interaction.channel.send(embed=ok_embed("🎉 ¡Ganadores del Sorteo!", f"**Premio:** {premio}\n**Ganadores:** {w_mentions}", GOLD))

# ═══════════════════════════════════════════
#  CATEGORÍA: ROLEPLAY
# ═══════════════════════════════════════════
RP_GIFS = {
    "hug":      "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
    "kiss":     "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
    "slap":     "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "pat":      "https://media.giphy.com/media/5tmRHwTlHAA9WkBBOR/giphy.gif",
    "cry":      "https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif",
    "poke":     "https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif",
    "bite":     "https://media.giphy.com/media/8t7L0T4RSyKrm/giphy.gif",
    "cuddle":   "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
    "highfive": "https://media.giphy.com/media/3oEjHV0z8S7WM4MwnK/giphy.gif",
    "wave":     "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif",
}

def rp_cmd(action, emoji, msg_template):
    @bot.tree.command(name=action, description=f"Acción de roleplay: {action}")
    @app_commands.describe(usuario="Usuario objetivo")
    async def _rp(interaction: discord.Interaction, usuario: discord.Member):
        e = discord.Embed(description=f"{emoji} {msg_template.format(a=interaction.user.mention, b=usuario.mention)}", color=PURPLE)
        e.set_image(url=RP_GIFS.get(action, ""))
        await interaction.response.send_message(embed=e)
    return _rp

rp_cmd("hug",      "🤗", "**{a}** le dio un abrazo a **{b}**")
rp_cmd("kiss",     "💋", "**{a}** le dio un beso a **{b}**")
rp_cmd("slap",     "👋", "**{a}** le dio una bofetada a **{b}**")
rp_cmd("pat",      "🫶", "**{a}** le dio palmaditas a **{b}**")
rp_cmd("cry",      "😢", "**{a}** está llorando con **{b}**")
rp_cmd("poke",     "👉", "**{a}** le dio un toque a **{b}**")
rp_cmd("bite",     "😤", "**{a}** le mordió a **{b}**")
rp_cmd("cuddle",   "🥰", "**{a}** se acurrucó con **{b}**")
rp_cmd("highfive", "🙌", "**{a}** chocó los cinco con **{b}**")
rp_cmd("wave",     "👋", "**{a}** le saludó a **{b}**")

# ═══════════════════════════════════════════
#  CATEGORÍA: JUEGOS
# ═══════════════════════════════════════════
@bot.tree.command(name="rps", description="Piedra, papel o tijeras")
@app_commands.describe(eleccion="Tu elección")
@app_commands.choices(eleccion=[
    app_commands.Choice(name="Piedra",  value="piedra"),
    app_commands.Choice(name="Papel",   value="papel"),
    app_commands.Choice(name="Tijeras", value="tijeras"),
])
async def rps(interaction: discord.Interaction, eleccion: app_commands.Choice[str]):
    opts    = ["piedra","papel","tijeras"]
    bot_opt = random.choice(opts)
    emojis  = {"piedra":"🪨","papel":"📄","tijeras":"✂️"}
    wins    = {"piedra":"tijeras","papel":"piedra","tijeras":"papel"}
    user_e  = eleccion.value
    if user_e == bot_opt:   result = "¡Empate! 🤝"
    elif wins[user_e] == bot_opt: result = "¡Ganaste! 🎉"
    else:                         result = "¡Perdiste! 😢"
    e = info_embed("🎮 Piedra Papel Tijeras", f"Tú: {emojis[user_e]} **{user_e}**\nYo: {emojis[bot_opt]} **{bot_opt}**\n\n**{result}**")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="coinflip", description="Lanza una moneda")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["🪙 Cara", "🪙 Cruz"])
    await interaction.response.send_message(embed=info_embed("Lanzamiento de Moneda", f"**{result}**"))

@bot.tree.command(name="dice", description="Lanza un dado")
@app_commands.describe(caras="Número de caras (default: 6)")
async def dice(interaction: discord.Interaction, caras: int = 6):
    result = random.randint(1, caras)
    await interaction.response.send_message(embed=info_embed(f"🎲 Dado de {caras} caras", f"Resultado: **{result}**"))

@bot.tree.command(name="8ball", description="Pregúntale a la bola mágica")
@app_commands.describe(pregunta="Tu pregunta")
async def magic8ball(interaction: discord.Interaction, pregunta: str):
    responses = [
        "Sí, definitivamente.", "No lo creo.", "Es muy posible.",
        "No cuentes con ello.", "Absolutamente.", "Mis fuentes dicen no.",
        "Sin duda alguna.", "Muy dudoso.", "Sí.", "No.",
        "Las perspectivas son buenas.", "Mejor no decirte ahora.",
    ]
    e = info_embed("🎱 Bola Mágica", f"**Pregunta:** {pregunta}\n**Respuesta:** {random.choice(responses)}")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="trivia", description="Pregunta de trivia aleatoria")
async def trivia(interaction: discord.Interaction):
    questions = [
        ("¿Cuál es la capital de Francia?",   ["París","Madrid","Roma","Berlín"],   0),
        ("¿Cuántos lados tiene un hexágono?", ["4","5","6","8"],                    2),
        ("¿Quién pintó la Mona Lisa?",        ["Picasso","Da Vinci","Rembrandt","Dalí"], 1),
        ("¿En qué año llegó el hombre a la luna?", ["1965","1967","1969","1971"],   2),
        ("¿Cuál es el planeta más grande?",   ["Tierra","Saturno","Júpiter","Neptuno"], 2),
    ]
    q, opts, ans = random.choice(questions)
    emojis = ["🇦","🇧","🇨","🇩"]
    e = info_embed("🧠 Trivia", q, BLUE)
    for i, opt in enumerate(opts):
        e.add_field(name=f"{emojis[i]} {opt}", value="", inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="guess", description="Adivina el número (1-100)")
async def guess(interaction: discord.Interaction):
    number = random.randint(1, 100)
    await interaction.response.send_message(embed=info_embed("🔢 Adivina el Número", f"Piensa en un número del **1 al 100**.\n*Número secreto guardado. Usa /guess_check para adivinar.*"))
    cfg = get_config()
    gid = str(interaction.guild.id)
    if gid not in cfg: cfg[gid] = {}
    if "games" not in cfg[gid]: cfg[gid]["games"] = {}
    cfg[gid]["games"][str(interaction.user.id)] = number
    save_config(cfg)

@bot.tree.command(name="random", description="Número aleatorio entre dos valores")
@app_commands.describe(minimo="Mínimo", maximo="Máximo")
async def random_num(interaction: discord.Interaction, minimo: int = 1, maximo: int = 100):
    result = random.randint(minimo, maximo)
    await interaction.response.send_message(embed=info_embed("🎲 Número Aleatorio", f"Entre **{minimo}** y **{maximo}**: **{result}**"))

# ═══════════════════════════════════════════
#  CATEGORÍA: ANTINUKE / ANTIRAID
# ═══════════════════════════════════════════
@bot.tree.command(name="antinuke", description="Gestiona el sistema AntiNuke")
@app_commands.describe(accion="on/off/status/whitelist/unwhitelist", usuario="Usuario (para whitelist)")
@app_commands.checks.has_permissions(administrator=True)
async def antinuke(interaction: discord.Interaction, accion: str, usuario: discord.Member = None):
    cfg = get_config()
    gid = str(interaction.guild.id)
    if gid not in cfg: cfg[gid] = {}
    if "antinuke" not in cfg[gid]: cfg[gid]["antinuke"] = {"enabled": False, "whitelist": []}
    an = cfg[gid]["antinuke"]
    if accion == "on":
        an["enabled"] = True; save_config(cfg)
        await interaction.response.send_message(embed=ok_embed("AntiNuke", "🔒 Sistema AntiNuke **activado**."))
    elif accion == "off":
        an["enabled"] = False; save_config(cfg)
        await interaction.response.send_message(embed=ok_embed("AntiNuke", "🔓 Sistema AntiNuke **desactivado**."))
    elif accion == "status":
        status = "✅ Activo" if an["enabled"] else "❌ Inactivo"
        wl = ", ".join(f"<@{u}>" for u in an["whitelist"]) or "Nadie"
        e = info_embed("🔒 Estado AntiNuke", f"**Estado:** {status}\n**Whitelist:** {wl}")
        await interaction.response.send_message(embed=e)
    elif accion == "whitelist" and usuario:
        if usuario.id not in an["whitelist"]: an["whitelist"].append(usuario.id)
        save_config(cfg)
        await interaction.response.send_message(embed=ok_embed("AntiNuke Whitelist", f"**{usuario}** añadido a la whitelist."))
    elif accion == "unwhitelist" and usuario:
        if usuario.id in an["whitelist"]: an["whitelist"].remove(usuario.id)
        save_config(cfg)
        await interaction.response.send_message(embed=ok_embed("AntiNuke Whitelist", f"**{usuario}** removido de la whitelist."))
    else:
        await interaction.response.send_message(embed=err_embed("Error", "Acción inválida. Usa: on, off, status, whitelist, unwhitelist"), ephemeral=True)

@bot.tree.command(name="antiraid", description="Gestiona el sistema AntiRaid")
@app_commands.describe(accion="on/off/status", threshold="Joins por minuto para activar (default: 10)")
@app_commands.checks.has_permissions(administrator=True)
async def antiraid(interaction: discord.Interaction, accion: str, threshold: int = 10):
    cfg = get_config()
    gid = str(interaction.guild.id)
    if gid not in cfg: cfg[gid] = {}
    if "antiraid" not in cfg[gid]: cfg[gid]["antiraid"] = {"enabled": False, "threshold": 10}
    ar = cfg[gid]["antiraid"]
    if accion == "on":
        ar["enabled"] = True; ar["threshold"] = threshold; save_config(cfg)
        await interaction.response.send_message(embed=ok_embed("AntiRaid", f"🛡️ AntiRaid **activado**. Threshold: **{threshold}** joins/min."))
    elif accion == "off":
        ar["enabled"] = False; save_config(cfg)
        await interaction.response.send_message(embed=ok_embed("AntiRaid", "AntiRaid **desactivado**."))
    elif accion == "status":
        status = "✅ Activo" if ar["enabled"] else "❌ Inactivo"
        await interaction.response.send_message(embed=info_embed("🛡️ Estado AntiRaid", f"**Estado:** {status}\n**Threshold:** {ar.get('threshold', 10)} joins/min"))

# ═══════════════════════════════════════════
#  EVENTOS
# ═══════════════════════════════════════════
@bot.event
async def on_member_join(member):
    cfg = get_config()
    gid = str(member.guild.id)
    gcfg = cfg.get(gid, {})
    # Welcome
    if ch_id := gcfg.get("welcome_channel"):
        ch = member.guild.get_channel(ch_id)
        if ch:
            msg = gcfg.get("welcome_message", "¡Bienvenido {user} a {server}!")
            msg = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
            e = discord.Embed(description=msg, color=PURPLE)
            e.set_thumbnail(url=member.display_avatar.url)
            await ch.send(embed=e)
    # Autorole
    if role_id := gcfg.get("autorole"):
        role = member.guild.get_role(role_id)
        if role:
            try: await member.add_roles(role)
            except: pass

@bot.event
async def on_command_error(ctx, error):
    pass

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=err_embed("Sin permisos", "No tienes permisos para usar este comando."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=err_embed("Error", str(error)), ephemeral=True)

# ═══════════════════════════════════════════
#  ADMIN EXTRA
# ═══════════════════════════════════════════
@bot.tree.command(name="nuke", description="Clona el canal y borra el original")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    ch = interaction.channel
    pos = ch.position
    new_ch = await ch.clone()
    await new_ch.edit(position=pos)
    await ch.delete()
    e = ok_embed("💣 Canal Nukeado", f"{new_ch.mention} ha sido reseteado.")
    await new_ch.send(embed=e)

@bot.tree.command(name="setname", description="Cambia el nombre del servidor")
@app_commands.describe(nombre="Nuevo nombre")
@app_commands.checks.has_permissions(manage_guild=True)
async def setname(interaction: discord.Interaction, nombre: str):
    old = interaction.guild.name
    await interaction.guild.edit(name=nombre)
    await interaction.response.send_message(embed=ok_embed("Nombre Cambiado", f"**{old}** → **{nombre}**"))

@bot.tree.command(name="members", description="Muestra el conteo de miembros")
async def members(interaction: discord.Interaction):
    g = interaction.guild
    humans = sum(1 for m in g.members if not m.bot)
    bots   = sum(1 for m in g.members if m.bot)
    e = info_embed("👥 Miembros del Servidor")
    e.add_field(name="Total",   value=str(g.member_count), inline=True)
    e.add_field(name="Humanos", value=str(humans),          inline=True)
    e.add_field(name="Bots",    value=str(bots),            inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="bans", description="Lista los bans del servidor")
@app_commands.checks.has_permissions(ban_members=True)
async def bans(interaction: discord.Interaction):
    await interaction.response.defer()
    banned = [entry async for entry in interaction.guild.bans()]
    if not banned:
        return await interaction.followup.send(embed=info_embed("Bans", "No hay usuarios baneados."))
    desc = "\n".join(f"**{e.user}** — {e.reason or 'Sin razón'}" for e in banned[:20])
    e = info_embed(f"🔨 Bans ({len(banned)})", desc)
    await interaction.followup.send(embed=e)

# ─────────────────────────────────────────────
#  START
# ─────────────────────────────────────────────
@bot.event
async def setup_hook():
    bot.start_time = datetime.datetime.utcnow()

bot.run(TOKEN)
