import discord
import requests
import json
import asyncio
from math import ceil, floor
from discord.ext import commands

def setup(client):
    client.add_cog(Prestige(client))

class Prestige(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(name="prestige")
    async def prestige(self, ctx, name):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        factionPercentiles = json.loads(requests.get("https://hordes.io/api/pvp/getfactionpercentiles").text)
        ranks = {
            0     : ["None","None"],
            4000  : ["Recruit","Unclean"],
            8000  : ["Novice","Brawler"],
            12000 : ["Squire","Slayer"],
            16000 : ["Apprentice","Ravager"],
            20000 : ["Adept","Breaker"],
            24000 : ["Fierce Master","Ruthless Demolisher"],
            28000 : ["Valiant Knight","Savage Marauder"],
            32000 : ["Gallant Soldier","Wild Reaper"],
            36000 : ["Famous Veteran","Defiant Liberator"],
            40000 : ["Fearless Warden","Bold Champion"],
            44000 : ["Supreme Commander","Restless Hero"],
            48000 : ["Lord","Chosen"]
        }
        pawards = [2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000]

        r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : name, "order" : "prestige", "limit" : 1, "offset" : 0}))
        if json.loads(r.text):
            player = json.loads(r.text)[0]
        else:
            return await ctx.send("Player not found")

        currentPrestige = player["prestige"]
        for i in ranks:
            if currentPrestige > 48000:
                currentRank = ranks[48000][player["faction"]]
                currentBracket = 48000
                break
            elif currentPrestige < i:
                currentRank = ranks[i-4000][player["faction"]]
                currentBracket = i-4000
                break
        prestigeNeeded = currentBracket-(currentPrestige*0.8)
        if prestigeNeeded <= 0:
            bracketNeededMaintain = "None"
            fameNeededMaintain = "None"
        elif prestigeNeeded < 1001:
            bracketNeededMaintain = 1
            fameNeededMaintain = factionPercentiles[player["faction"]][bracketNeededMaintain-1]
        else:
            bracketNeededMaintain = pawards.index(ceil(prestigeNeeded/1000)*1000)+1
            fameNeededMaintain = factionPercentiles[player["faction"]][bracketNeededMaintain-1]
        if currentBracket == 48000:
            bracketNeededNext = "0"
            fameNeededNext = "0"
        elif currentBracket == 0:
            bracketNeededNext = pawards.index(ceil((4000-prestigeNeeded)/1000)*1000)+1
            fameNeededNext = factionPercentiles[player["faction"]][bracketNeededNext-1]
        elif prestigeNeeded <= 0:
            bracketNeededNext = pawards.index(ceil(((currentBracket+4000)-(currentPrestige*0.8))/1000)*1000)+1
            fameNeededNext = factionPercentiles[player["faction"]][bracketNeededNext-1]
        else:
            bracketNeededNext = bracketNeededMaintain + 4
            fameNeededNext = factionPercentiles[player["faction"]][bracketNeededNext-1]

        
        await ctx.send(f"Current rank: {currentRank} - {currentPrestige} prestige\nMaintain rank: Bracket {bracketNeededMaintain} - {fameNeededMaintain} fame\nNext rank: Bracket {bracketNeededNext} - {fameNeededNext} fame")