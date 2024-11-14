import os
import discord
from math import ceil
from discord.ext import tasks
from datetime import datetime, timedelta


TOKEN = ""
client = discord.Client()

@client.event
async def on_ready():
  print("online")

  client.timerChannel = client.get_channel(923281551402369044)
  client.timeleftCategory = client.get_channel(923311238832849046)
  client.currentPhaseChannel = client.get_channel(923311299348271105)

  await client.timerChannel.purge(limit=10)
  client.timersEmbed = await client.timerChannel.send(embed=discord.Embed(title="yome"))

  timers.start()

@tasks.loop(minutes=5)
async def timers():
  now = datetime.now()
  nowHour = int(now.strftime("%H"))

  phaseEnd = (now+timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
  minutesLeft = round((phaseEnd-now).total_seconds()/60)


  newTimers = discord.Embed(title="Game Phases", color=0x60019b)

  if nowHour%3 == 0:
    currentPhase = "Obelisk"
    
    nextObelisk = (now + timedelta(hours=(3*ceil(nowHour/3)-1)-nowHour)).replace(minute=0, second=0, microsecond=0)
    nextBoss = (now + timedelta(hours=(3*ceil(nowHour/3))-nowHour)).replace(minute=0, second=0, microsecond=0)
    nextFarm = (now + timedelta(hours=(3*ceil(nowHour/3)+1)-nowHour)).replace(minute=0, second=0, microsecond=0)

    newTimers.add_field(name="Obelisk", value=f"<t:{int(nextObelisk.timestamp())}:t>")
    newTimers.add_field(name="Gloomfury", value=f"<t:{int(nextBoss.timestamp())}:t>")
    newTimers.add_field(name="Farming", value=f"<t:{int(nextFarm.timestamp())}:t>")

  elif nowHour%3 == 1:
    currentPhase = "Gloomfury"

    nextObelisk = (now + timedelta(hours=(3*ceil(nowHour/3)+1)-nowHour)).replace(minute=0, second=0, microsecond=0)
    nextBoss = (now + timedelta(hours=(3*ceil(nowHour/3)-1)-nowHour)).replace(minute=0, second=0, microsecond=0)
    nextFarm = (now + timedelta(hours=(3*ceil(nowHour/3))-nowHour)).replace(minute=0, second=0, microsecond=0)

    newTimers.add_field(name="Gloomfury", value=f"<t:{int(nextBoss.timestamp())}:t>")
    newTimers.add_field(name="Farming", value=f"<t:{int(nextFarm.timestamp())}:t>")
    newTimers.add_field(name="Obelisk", value=f"<t:{int(nextObelisk.timestamp())}:t>")

  else:
    currentPhase = "Farming"

    nextObelisk = (now + timedelta(hours=(3*ceil(nowHour/3))-nowHour)).replace(minute=0, second=0, microsecond=0)
    nextBoss = (now + timedelta(hours=(3*ceil(nowHour/3)+1)-nowHour)).replace(minute=0, second=0, microsecond=0)
    nextFarm = (now + timedelta(hours=(3*ceil(nowHour/3)-1)-nowHour)).replace(minute=0, second=0, microsecond=0)

    newTimers.add_field(name="Farming", value=f"<t:{int(nextFarm.timestamp())}:t>")
    newTimers.add_field(name="Obelisk", value=f"<t:{int(nextObelisk.timestamp())}:t>")
    newTimers.add_field(name="Gloomfury", value=f"<t:{int(nextBoss.timestamp())}:t>")

  newTimers.set_thumbnail(url="https://cdn.discordapp.com/icons/923032334415040573/39af89e68b182e6884bdb31fa813b101.webp?size=96")
  newTimers.set_footer(text=f"Current Phase: {currentPhase}", icon_url="https://cdn3.iconfinder.com/data/icons/glypho-travel/64/history-swords-crossed-512.png")

  await client.timersEmbed.edit(embed=newTimers)
  await client.timeleftCategory.edit(name=f"{minutesLeft} minutes remaining")
  await client.currentPhaseChannel.edit(name=f"{currentPhase}")



client.run(TOKEN)

"""
from datetime import datetime

# time(hour = 0, minute = 0, second = 0)
now = datetime.now()
nowHour = int(now.strftime("%H"))


phaseEnd = (now+timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

minutesLeft = (phaseEnd-now).total_seconds()
print(round(minutesLeft/60))"""