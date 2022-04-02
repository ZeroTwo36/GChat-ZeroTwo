import nextcord as discord
import re
import json
import configparser
from nextcord.ext import commands
import os
from profanity import has_profanity
import typing
from datetime import datetime, timedelta

def get_ratelimit(message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        for k in chats['servers']:
            if str(k['channelid']) == str(message.channel.id):
                bucket = _cd.get_bucket(message)
                return bucket.update_rate_limit()

        return None

cfg = configparser.ConfigParser()
_cd = commands.CooldownMapping.from_cooldown(1, 12, commands.BucketType.member) # Change accordingly
intents = discord.Intents.default()
intents.messages = True
intents.members = True

if os.path.isfile("globalchat.json"):
    with open("globalchat.json",encoding="utf-8") as f:
        chats = json.load(f)

else:
    chats = {'servers': []}
    with open("globalchat.json","w",encoding="utf-8") as f:
        json.dump(chats,f,indent=4)

client = commands.Bot(command_prefix="z.",intents=intents)
RULES = open("rules.md").read()

JOINSTRING = """

Hello! I'm ZeroTwo, a GLOBALCHAT Bot!

If you don't know what GLOBALCHATting means, it
basically allows cross-server chatting.

**_Getting Started_**
To start chatting, tell an Admin to do `z.connect #channel`

Check the rules with `z.rules`
"""

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        try:
            await channel.send(JOINSTRING)
            break
        except:
            continue

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="I accept the GlobalChat Rules",emoji="✔️",style=discord.ButtonStyle.green)
    async def confirm(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message("Setting up GlobalChat...",ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="I do not accept",emoji="❌",style=discord.ButtonStyle.red)
    async def decline(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message("Cancelled setup!",ephemeral=True)
        self.value = False
        self.stop()

class Globalchat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_users = []

    def guild_exists(self,guildid):
        for server in chats['servers']:
            if(int(server['guildid']) == int(guildid)):
                return True

        return False


    def get_globalchat(self,guildid,channelid=None):
        globalChat = None
        for server in chats['servers']:
            if(int(server['guildid']) == int(guildid)):
                if channelid:
                    if int(channelid) == int(server['channelid']):
                        globalChat = server

                else:
                    globalChat = server

        return globalChat

    def get_globalchat_id(self,guildid):
        globalChat = -1
        i = 0
        for server in chats['servers']:
            if(int(server['guildid']) == int(guildid)):
                globalChat = i

            i += 1

        return globalChat

    @commands.command()
    async def rules(self,ctx):
        await ctx.send(RULES)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def connect(self,ctx,channel:discord.TextChannel=None):
            if not channel:
                channel = ctx.channel
            if self.guild_exists(ctx.guild.id):
                return await ctx.send("Globalchat already set up!")

            server = {
                'guildid':ctx.guild.id,
                'channelid':channel.id,
                'invite': f'{(await ctx.channel.create_invite()).url}'
            }
            chats['servers'].append(server)
            embed = discord.Embed(title="⚠️ Important, Please read ⚠️")
            embed.description = "By setting up the Globalchat, you confirm that you have read and agree to the rules (`z.rules`)"
            view = Confirm()
            await ctx.send(embed=embed,view=view)
            
            def getBotsAndUsers(guild):
                bots = 0
                users = 0
                for m in guild.members:
                    if m.bot:
                        bots += 1
                    else:
                        users += 1
                return (bots,users)

            bots, users = getBotsAndUsers(ctx.guild)
            await view.wait()
            if not view.value:
                await ctx.send(":x: Timed out!")
                return
            if view.value:
                with open("globalchat.json","w",encoding="utf-8") as f:
                    json.dump(chats,f,indent=4)
                await self.sendJoinMSG(f'┏📚 › Server-Name: `{ctx.guild.name}`\n┣👥 › Members: {users}👤 - {bots}🤖\n┗🚨 › Globalchat\'s Rules: `z.rules`')
                await channel.send("THIS CHANNEL is now the Global chat!")
            else:
                await ctx.send("The Globalchat Setup has been cancelled")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def disconnect(self,ctx):
        await ctx.send("```Disconnected from Global Network!```")

        if self.guild_exists(ctx.guild.id):
            globalid = self.get_globalchat_id(ctx.guild.id)
            if globalid != -1:
                chats['servers'].pop(globalid)
                with open("globalchat.json","w",encoding="utf-8") as f:
                    json.dump(chats,f,indent=4)

    
    @commands.command()
    @commands.is_owner()
    async def tempban(self,ctx,user_id):
        self.bans.append(user_id)
        await ctx.send(f"```{user_id} has been temp-banned!```")
    
    @commands.command()
    @commands.is_owner()
    async def permaban(self,ctx,user_id,*,reason="Not provided"):
        with open("globalchat.json","r") as f:
            gc = json.load(f)
        gc["bans"].append({"id":user_id,"reason":reason})
        with open("globalchat.json","w") as f:
            json.dump(gc,f)
        embed = discord.Embed(title="That shit head is gone!",description="The negativity has been eliminated from the globalchat.")
        embed.add_field(name="User ID",value=user_id)
        embed.add_field(name="Reason",value=reason)
        await ctx.send(embed=embed)

    
    @client.message_command(name="Report Message")
    async def rep(self,interaction: discord.Interaction, message: discord.Message):
        if message.author.id == client.user.id:
            m = await interaction.response.send_message("<a:discordloading:949624209703862272> Please wait - Your Request is being processed...", ephemeral=True)
            await client.get_channel(959826541221666836).send(embeds=message.embeds)
            await interaction.response.send_message("`✔` The Message was reported and will be reviewed by the Team as soon as possible", ephemeral=True)
        else:
            await interaction.response.send_message("`❌` The Message was not reported: `Message MUST be sent by this Bot`", ephemeral=True)


    async def sendAll(self,message:discord.Message):
        def getBotsAndUsers(guild):
            bots = 0
            users = 0
            for m in guild.members:
                if m.bot:
                    bots += 1
                else:
                    users += 1
            return (bots,users)

        async def potentialReply(message:discord.Message):
            if message.reference:
                msg:discord.Message = await message.channel.fetch_message(message.reference.message_id)
                og_msg = msg.embeds[0].description.split("\n\n")[0]
                og_user = msg.embeds[0].author.name.split("›")[1]
                content = '''
`✍`› **Responding to `{0}`**:
> {1}
                '''.format(og_user,og_msg)
                return content
            return ''

        botCount, UserCount = getBotsAndUsers(message.guild)

        embed = discord.Embed(description=f'{message.content}{await potentialReply(message)}',color=message.author.color)        
        embed.set_author(name=f"{'👤' if message.author.id != 899722893603274793 else '👑'} › {message.author.display_name}",icon_url=message.author.avatar.url)
        embed.set_footer(text=f'{message.guild.name} - {message.channel.name} (👤 {UserCount} - 🤖 {botCount} - 👥{UserCount+botCount})',icon_url=message.guild.icon.url or "https://www.svgrepo.com/show/353655/discord-icon.svg" if hasattr(message.guild.icon,"url") else "https://www.svgrepo.com/show/353655/discord-icon.svg")
        for server in chats['servers']:
            guild:discord.Guild = self.bot.get_guild(int(server['guildid']))
            if guild:
                channel:discord.TextChannel = guild.get_channel(int(server['channelid']))
                if channel:
                  try:
                    await channel.send(embed=embed)
                  except:
                      continue
        await message.delete()

    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        if message.author.bot:
            return
        self.URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        if message.author.id in self.banned_users:
            embed = discord.Embed(title="⛔ Message not sent")
            embed.add_field(name="Reason",value="You have been muted from the Global Chat")
            embed.set_footer(text=f'{message.author} | {message.author.id}')
            return await message.channel.send(embed=embed)

        with open("globalchat.json","r") as f:
            gc = json.load(f)

        ratelimit = get_ratelimit(message)        
        
        if ratelimit is not None:
            embed = discord.Embed(title="⛔ Message not sent")
            embed.add_field(name="Reason",value="You can only send one Message each 12 Seconds")
            embed.set_footer(text=f'{message.author} | {message.author.id}')
            return await message.channel.send(embed=embed)

        for server in chats['servers']:
            if int(message.channel.id) == int(server['channelid']):
                for i in gc["bans"]:
                    print(i)
                    print(i["id"])
                    print(message.author.id == i["id"])
                    if str(message.author.id) == i["id"]:
                        await message.channel.send(f"You have been prevented from Globalchatting ({i['reason']})")
                if len(re.findall(self.URL_REGEX,message.content)) >0:
                    embed = discord.Embed(title="⛔ Message not sent")
                    embed.add_field(name="Reason",value="You cannot post Links in the Globalchat")
                    embed.set_footer(text=f'{message.author} | {message.author.id}')
                    return await message.channel.send(embed=embed)

                if has_profanity(message.content):
                    embed = discord.Embed(title="⛔ Message not sent")
                    embed.add_field(name="Reason",value="Profanity found in Message")
                    embed.set_footer(text=f'{message.author} | {message.author.id}')
                    return await message.channel.send(embed=embed)
                await self.sendAll(message)

        # await self.bot.process_commands(message)
    
    
    async def sendAllSystem(self,message):
        embed = discord.Embed(description=message,color=discord.Color.red())
        embed.set_author(name="System Message!",icon_url=client.user.avatar.url)
        embed.set_footer(text=f'I am a Bot and this message was sent automatically. Beep Bop.')
        for server in chats['servers']:
            guild:discord.Guild = self.bot.get_guild(int(server['guildid']))
            if guild:
                channel:discord.TextChannel = guild.get_channel(int(server['channelid']))
                if channel:
                  try:
                    await channel.send(embed=embed)
                  except:
                      continue
        await message.delete()

    async def sendJoinMSG(self,message):
        embed = discord.Embed(description=message,color=discord.Color.green(),title='Welcome!')
        embed.set_author(name="A new Server joined the System!",icon_url=client.user.avatar.url)
        embed.set_footer(text=f'I am a Bot and this message was sent automatically. Beep Bop.')
        for server in chats['servers']:
            guild:discord.Guild = self.bot.get_guild(int(server['guildid']))
            if guild:
                channel:discord.TextChannel = guild.get_channel(int(server['channelid']))
                if channel:
                  try:
                    await channel.send(embed=embed)
                  except:
                      continue
        await message.delete()

client.add_cog(Globalchat(client))
cfg.read("config.cfg")
if __name__ == "__main__":
    client.run(cfg.get("main","HTTP_BOT_TOKEN"))
