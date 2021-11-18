import discord
import json
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.messages = True

if os.path.isfile("globalchat.json"):
    with open("globalchat.json",encoding="utf-8") as f:
        chats = json.load(f)

else:
    chats = {'servers': []}
    with open("globalchat.json","w",encoding="utf-8") as f:
        json.dump(chats,f,indent=4)

client = commands.Bot(command_prefix="z.",intents=intents)

link_prefixes = ["http://","https://","www.",".com",".net",".xyz",".gg"]

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

class Globalchat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        await ctx.send("""
Globalchat Rules:
1. No Links in globalchat
2. Remember the Human - everyone talking out there is a human like you
3. No heated arguments
4. Cursing is okay but please know your limits
5. Breaking any of the rules mentioned above will lead to you being blocked from GC for 1 week
6. Bots WILL NOT be able to send Messages into GC
        """)

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
            with open("globalchat.json","w",encoding="utf-8") as f:
                json.dump(chats,f,indent=4)
            await channel.send("THIS CHANNEL is now the Global chat!")

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

    async def sendAll(self,message:discord.Message):
        embed = discord.Embed(description=message.content,color=message.author.color)
        embed.set_author(name=message.author,icon_url=message.author.avatar.url)
        embed.set_footer(text=f'Posted in {message.guild.name} ({message.guild.id})')
        for server in chats['servers']:
            guild:discord.Guild = self.bot.get_guild(int(server['guildid']))
            if guild:
                channel:discord.TextChannel = guild.get_channel(int(server['channelid']))
                if channel:
                    await channel.send(embed=embed)

        await message.delete()

    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        if message.author.bot:
            return
        for server in chats['servers']:
            if int(message.channel.id) == int(server['channelid']):
                for prefix in link_prefixes:
                    if prefix in message.content.lower():

                        return await message.channel.send("You may not post any Links!")
                await self.sendAll(message)

        # await self.bot.process_commands(message)

client.add_cog(Globalchat(client))

client.run(os.getenv("TOKEN"))
