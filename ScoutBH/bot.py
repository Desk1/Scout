# bot.py
import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from time import strftime
import discord
import requests
from discord.ext import commands
from static.misc import ruin


intents = discord.Intents.default()
intents.members = True

dev = False

if dev:
    TOKEN = ""
    client = commands.Bot(command_prefix='.', help_command=None, intents=intents)
    os.environ["mongo"] = ""
else:
    TOKEN = os.environ["token"]
    os.environ["mongo"] = ""
    client = commands.Bot(command_prefix='>', help_command=None, intents=intents)


war_status = 790627728713973780 # war=status
war_chat = 706155936489668620 # war-chat
testing_status = 778603129134383145 # hordespvp
testing_chat = 484051920802021397 # botting

upperBound = 200000
middleBound = 50000
lowerBound = 20000


@client.event
async def on_ready():
    #guild = discord.utils.get(client.guilds, name=GUILD)
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild: {guild.name}(id: {guild.id})'
        )
    await client.change_presence(activity=discord.Game(name=">help | 👁"))

    client.scoutGuild = client.get_guild(872255568922947644)
    client.dev = dev
    client.gears = None # that one thing that is useless but breaks a bunch of stuff if you remove it

    client.VIP = [225697391926444033]
    client.characterLinkRequests = []

    print("^ yome ^")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

    client.ruin = []
    for x in ruin.ruin:
        client.ruin.append(int(ruin.ruin[x]))
    """
    channel = client.get_channel(war_status)
    await channel.purge(limit=1)
    lb = discord.Embed(title="PvP leaderboard", color=0x000000)
    leaderboard = await channel.send(embed=lb)

    client.loop.create_task(scrapePvpLeaderboard(leaderboard))
    """

@client.command()
@commands.has_role("Owner")
async def reload(ctx, cmd):
    client.reload_extension(f"cogs.{cmd}")

    await ctx.send(f"Reloaded {cmd}.py")

@client.event # error handler taken from https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
            return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    ignored = (commands.CommandNotFound, )

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        return

    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    await ctx.send("error")


async def scrapePvpLeaderboard(msg):
    try:
        old = {
            0: [], # vg
            1: []  # bl
        }
        largetime1 = datetime(2020, 12, 10)
        mediumtime1 = datetime(2020, 12, 10)
        smalltime1 = datetime(2020, 12, 10)
        channel = client.get_channel(war_chat)
        while True:
            url = 'https://hordes.io/api/playerinfo/search'
            data = {"name":"","order":"fame","limit":100,"offset":0}
            r = requests.post(url, data=json.dumps(data))
            players = json.loads(r.text)
            gains = {
                0: [], # vg
                1: []  # bl
            }
            fame = {
                0: [], # vg
                1: []  # bl
            }
            time = strftime("%H:%M")

            vgcount = 0
            blcount = 0
            for player in players:
                if player["faction"] == 0:
                    vgcount += 1
                else:
                    blcount += 1
            limit = min(vgcount,blcount)

            try:
                for i in range(100): # adding fames
                    faction = players[i]["faction"]
                    if len(fame[faction]) < limit:
                        fame[faction].append(players[i]["fame"])
                        pos = fame[faction].index(players[i]["fame"])
                        try:
                            gains[faction].append(fame[faction][pos] - old[faction][pos])
                        except:
                            gains[faction].append(0)
                        if gains[faction][pos] < 0:
                            raise ValueError
            except ValueError:
                continue

            old = fame

            if sum(gains[1]) > upperBound or sum(gains[0]) > upperBound:
                status = "Large war"
                largetime2 = datetime.today()
                if (((largetime2-largetime1).total_seconds())/60) > 120:
                    await channel.send("Large <@&724822880419971192>")
                    largetime1 = datetime.today()
            elif sum(gains[1]) > middleBound or sum(gains[0]) > middleBound:
                status = "Moderate war"
                mediumtime2 = datetime.today()
                if (((mediumtime2-mediumtime1).total_seconds())/60) > 60:
                    mediumtime1 = datetime.today()
            elif sum(gains[1]) > lowerBound or sum(gains[0]) > lowerBound:
                status = "Small war"
                smalltime2 = datetime.today()
                if (((smalltime2-smalltime1).total_seconds())/60) > 60:
                    smalltime1 = datetime.today()
            else:
                status = "No war"


            totalbl = sum(gains[1])
            totalvg = sum(gains[0])


            if totalbl > totalvg and status != "No war":
                lb = discord.Embed(color=0xef4d4d)
                lb.set_footer(text="Bloodlust winning.")
                lb.set_thumbnail(url='https://hordes.io/assets/ui/factions/1.webp?v=4586729')
            elif totalvg > totalbl and status != "No war":
                lb = discord.Embed(color=0x19b1d7)
                lb.set_footer(text="Vanguard winning. Come help out!")
                lb.set_thumbnail(url='https://hordes.io/assets/ui/factions/0.webp?v=4586729')
            else:
                lb = discord.Embed(color=0x949494)
                lb.set_footer(text="No war")
                lb.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Peace_sign.svg/1200px-Peace_sign.svg.png')
            lb.add_field(name='Bloodlust', value=f"+{totalbl} Fame", inline=False)
            lb.add_field(name='Vanguard', value=f"+{totalvg} Fame", inline=False)
            lb.set_author(name=f"{status} - {time}", icon_url='https://static.thenounproject.com/png/3139255-200.png')
            await msg.edit(embed=lb)

            await asyncio.sleep(600)
    except:
        pass

client.run(TOKEN)
