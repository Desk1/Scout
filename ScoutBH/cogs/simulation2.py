import discord
from pyasn1.type.univ import Null
import requests
import json
import os
from pymongo import MongoClient
from math import floor, ceil
from cogs.simulation import Simulation
from func.playerCard import *
from func.buffs import *
from func import decoder
from discord.ext import commands
from HordesCraft.shaman import run
from time import gmtime, strftime


def setup(client):
    client.add_cog(Shamandps(client))

class Shamandps(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.Decoder = decoder.APIDecoder()
        MONGO = os.environ["mongo"]
        self.cluster = MongoClient(MONGO)
        self.db = self.cluster["scout"]
        self.collection = self.db["items"]
        self.collectionGen = self.db["items-gen"]

    @commands.command(name="gloomfury")
    async def prestige(self, ctx, name, *args):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        

        r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : name, "order" : "gs", "limit" : 25, "offset" : 0}))
        players = json.loads(r.text)
        found = False
        for player in players:
            if name.lower() == player["name"].lower():
                playerinfo = player
                found = True
        if not found:
            return await ctx.send("Unknown player")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        itemIDs = {}
        itemSets = []
        maxupgrade = False
        maxtier = False
        charms = ["Tattooed Skull","Hardened Egg","Blue Marble","Little Bell","Ship Pennant"]
        buffNames = ["enchant","arctic","hypo","armor","warcry","crusader","bulwark","temporal","cranial","invigorate","howl"]
        buffs = [enchantBuff,arcticBuff,hypothermicBuff,armorBuff,warcryBuff,crusaderBuff,bulwarkBuff,temporalBuff,cranialBuff,invigorateBuff,howlBuff]
        ranks = [0,4000,8000,12000,16000,20000,24000,28000,32000,36000,40000,44000,48000]
        playerCharms = []

        prompt = await ctx.send("Paste auxi/itemID info here: (each item ID must be on new line)")
        inp = await self.client.wait_for('message', check=check)

        parsed = inp.content.split("\n")

        for charm in charms:
            if charm in parsed:
                playerCharms.append(charm)
                if len(playerCharms) == 2:
                    break

        for idx, i in enumerate(parsed):
            if "%" in i:
                if "+" in parsed[idx+1]:
                    itemIDs[i[i.index("%")+4:]] = int(parsed[idx+1][parsed[idx+1].index("+")+1:])
                else:
                    itemIDs[i[i.index("%")+4:]] = None
            else:
                if "+" in i:
                        if i[0] == "+":
                            itemSets.append(i) 
                        elif i[:i.index("+")-1].isnumeric():
                            itemIDs[i[:i.index("+")-1]] = int(i[i.index("+")+1:])

                else:
                    if i.isnumeric() or i[0] == "-":
                        itemIDs[i] = None

        if len(itemIDs) > 9:
            return await ctx.send("Too many items")
        
        gen = False
        apiIDS = []
        genIDS = []

        for set in itemSets:
            doc = self.collectionGen.find_one({"_id" : ctx.author.id}, {set : 1})
            
            for id in doc[set]:
                itemIDs[id] = None

        for k in itemIDs.keys():
            if k[0] == "-":
                genIDS.append(k)
            else:
                apiIDS.append(k)

        if len(genIDS) > 0:
            gen = True

        if len(apiIDS) == 0:
            items = []
        else:
            url = 'https://hordes.io/api/item/get'
            data = {"ids":apiIDS}
            cookies = {"sid":''}
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            items = json.loads(r.text)

        try:
            rank = ranks.index(floor(playerinfo["prestige"]/4000)*4000)
        except:
            rank = 12
        

        duration = 150
        simulations = 1
        args = [a for a in args]
        args.extend(["guh","enchant4", "arctic4", "warcry4", "crusader4", "temporal4","howl5"])
        if ctx.author.id in self.client.VIP:
            if "maxprestige" in args:
                rank = 12
            elif "noprestige" in args:
                rank = 0


            for a in args:
                if a[:-1].isdigit() and a[-1] == "s":
                    duration = min(int(a[:-1]), 600)
                if a.isdigit():
                    simulations = min(int(a), 150)

        name = playerinfo["name"]
        pclass = playerinfo["pclass"]
        level = playerinfo["level"]
        unallocated = playerinfo["level"]*3

        if pclass != 3:
            return await ctx.send("I don't know how to play this class yet")

        allocatedStats = {
            "str": 10,
            "sta": 10,
            "dex": 10,
            "int": 10,
            "wis": 10,
            "luc": 5
        }

        realStats = {
            "hp": 100,
            "hpr": 2.0,
            "mp": 100,
            "mpr": 3.0,
            "def": 15,
            "blo": 0.00,
            "min": 0,
            "max": 0,
            "att": 10,
            "cri": 5.0,
            "has": 0,
            "mov": 105,
            "bag": 15,
            "if": 0,
            "gs": 0
        }

        if pclass == 1:
            bloodline = "int"
        elif pclass == 2:
            bloodline = "dex"
        elif pclass == 3:
            bloodline = "wis"
        elif pclass == 0:
            bloodline = "str"

        allocatedStats["sta"] += level*2
        realStats["hp"] += level*8
        allocatedStats[bloodline] += level
        if "customspec" in args[1:]:
            await ctx.send("Enter stat allocation (each stat on new line, with ':' seperating name and value):")
            inp2 = await self.client.wait_for('message', check=check)

            stats = inp2.content.split("\n")

            altNames = {
                "strength": "str",
                "stamina": "sta",
                "stam": "sta",
                "dexterity": "dex",
                "dext": "dex",
                "intelligence": "int",
                "intel": "int",
                "wisdom": "wis",
                "luck": "luc"
            }

            totalAllocated = 0

            for stat in stats:
                if stat[:stat.index(":")] in altNames.keys():
                    statname = altNames[stat[:stat.index(":")]]
                else:
                    statname = stat[:stat.index(":")]

                toAllocate = int(stat[stat.index(":")+1:])

                allocatedStats[statname] += toAllocate
                totalAllocated += toAllocate
            
            if totalAllocated != unallocated:
                return await ctx.send(f"Stat points must add to {unallocated}")


        else:
            if "fullstam" in args:
                allocatedStats["sta"] += unallocated
            elif "fullstr" in args:
                allocatedStats["str"] += unallocated
            elif "fulldex" in args:
                allocatedStats["dex"] += unallocated
            elif "fullint" in args:
                allocatedStats["int"] += unallocated
            elif "fullwis" in args:
                allocatedStats["wis"] += unallocated
            elif "fullluck" in args:
                allocatedStats["luc"] += unallocated
            else:
                allocatedStats[bloodline] += unallocated


        decodedItems = []

        if ctx.author.id in self.client.VIP and len(genIDS) > 0:
            collection = self.db["items-gen"]

            doc = collection.find_one({"_id" : ctx.author.id})
            templates = []
            for i in genIDS:
                template = {
                    "id": 44483520,
                    "slot": None,
                    "bound": 0,
                    "type": "misc",
                    "upgrade": None,
                    "tier": 3,
                    "rolls": None,
                    "stacks": 1,
                    "stash": "2020-02-13T20:44:39.915Z"
                }
                templates.append(template)
            count = 0
            for x in doc:
                if x[0] == "-" and x in genIDS:
                    
                    templates[count]["rolls"] = doc[x]["rolls"]
                    templates[count]["upgrade"] = doc[x]["upgrade"]
                    templates[count]["type"] = doc[x]["type"]
                    templates[count]["tier"] = doc[x]["tier"]
                    templates[count]["id"] = x

                    items.append(templates[count])
                    count += 1
                    

        for item in items:
            if ctx.author.id in self.client.VIP:
                if maxupgrade:
                    item["upgrade"] = 6
                elif itemIDs[str(item["id"])] != None:
                    item["upgrade"] = itemIDs[str(item["id"])]
            try:
                item = self.Decoder.decode(item, maxtier)
            except:
                return await ctx.send("Failed to decode item data")
            decodedItems.append(item)

            for stat in item["attr"]:
                if stat in allocatedStats:
                    allocatedStats[stat] += item["attr"][stat]["value"]
                else:
                    realStats[stat] += item["attr"][stat]["value"]
            realStats["gs"] += item["gearscore"]

        for charm in playerCharms:
            realStats["gs"] += 30


        if rank >= 1:
            realStats["mov"] += 5
        if rank >= 2:
            realStats["mp"] += 50
        if rank >= 3:
            realStats["if"] += 15
        if rank >= 4:
            realStats["min"] += 5
            realStats["max"] += 5
        if rank >= 5:
            realStats["hpr"] += 2
            realStats["mpr"] += 2
        if rank >= 6:
            realStats["mov"] += 5
        if rank >= 7:
            realStats["hp"] += 30
        if rank >= 8:
            realStats["if"] += 15
        if rank >= 9:
            realStats["cri"] += 5
        if rank >= 10:
            realStats["has"] += 3
        if rank >= 11:
            realStats["hp"] += 30
        if rank >= 12:
            realStats["min"] += 5
            realStats["max"] += 5

        activeBuffs = {}
        dmgMultiplier = 1
        for arg in args[1:]:
            if arg[:-1] in buffNames:
                bufflevel = int(arg[-1])
                buff = arg[:-1]
                buffEffect = buffs[buffNames.index(buff)](bufflevel)
                if buffEffect[1] is not False and buffEffect[1] is not pclass:
                    pass
                else:
                    for effect in buffEffect[0]:
                        if effect == "dmg":
                            dmgMultiplier += buffEffect[0][effect]
                        else:
                            realStats[effect] += buffEffect[0][effect]
                    activeBuffs[buff] = bufflevel
                
                if buff == "bulwark":
                    await ctx.send("Enter Bulwark block stacks:")
                    inpstacks = await self.client.wait_for('message', check=check)
                    try:
                        stacks = int(inpstacks.content)
                    except:
                        return await ctx.send("error")

                    if stacks in range(1,9):
                        buffEffect = enrageBuff(bufflevel,stacks)
                        if buffEffect[1] is not False and buffEffect[1] is not pclass:
                            pass
                        else:
                            for effect in buffEffect[0]:
                                if effect == "dmg":
                                    dmgMultiplier += buffEffect[0][effect]
                                else:
                                    realStats[effect] += buffEffect[0][effect]
                            activeBuffs["enrage"] = stacks
            
            elif arg[:-1] == "plague" or arg[:-1] == "plaguespreader":
                await ctx.send("Enter Plaguespreader haste stacks:")
                inpstacks = await self.client.wait_for('message', check=check)
                try:
                    stacks = int(inpstacks.content)
                except:
                    return await ctx.send("error")

                if stacks in range(1,6):
                    bufflevel = int(arg[-1])
                    buff = arg[:-1]
                    buffEffect = plagueBuff(bufflevel, stacks)

                    if buffEffect[1] is not False and buffEffect[1] is not pclass:
                        pass
                    else:
                        for effect in buffEffect[0]:
                            if effect == "dmg":
                                dmgMultiplier += buffEffect[0][effect]
                            else:
                                realStats[effect] += buffEffect[0][effect]
                        activeBuffs["plague"] = stacks

            if arg == "skull":
                dmgMultiplier += 0.2
                activeBuffs["skull"] = 1


        realStats = initreal(allocatedStats, realStats, bloodline, dmgMultiplier)

        try:
            await inp.delete()
            await prompt.delete()
        except:
            pass
    
        ###########################################################################

        stats = {
            "min" : realStats["min"],
            "max" : realStats["max"],
            "crit" : realStats["cri"],
            "haste" : round(realStats['has'], 1)
        }

        skills = {
            "revitalize" : 5,
            "canine howl" : 5,
            "plaguespreader" : 5,
            "healing totem" : 4,
            "decay" : 1
        }

        config = {
            "duration" : duration,
            "tickrate" : 40,
            "healLogs" : False
        }

        totalheal = []
        for n in range(simulations):
            sim = run(skills, stats, config)
            totalheal.append(sum(sim["healing"].values()))
            stats["haste"] = round(stats['haste']-55, 1)
        stats["haste"] = round(stats['haste']-40, 1)
        skillmsg = ""
        for s in skills:
            skillmsg += f"{s.capitalize()}: {skills[s]}\n"

        statmsg = ""
        for s in stats:
            statmsg += f"{s.capitalize()}: {stats[s]}\n"

        castmsg = ""
        for s in sim["casts"]:
            castmsg += f"{s.capitalize()}: {sim['casts'][s]}\n"

        healmsg = ""
        for s in sim["healing"]:
            healmsg += f"{s.capitalize()}:\n{sim['healing'][s]} Healing\n{sim['ticks'][s]} Ticks\n\n"



        resultsmsg = ""
        if simulations > 1:
            avgTotal = sum(totalheal)/simulations
            minTotal = min(totalheal)
            maxTotal = max(totalheal)

            avgHPS = (avgTotal)/config["duration"]
            minHPS = minTotal/config["duration"]
            maxHPS = maxTotal/config["duration"]

            resultsmsg += f"Min Healing: {round(minTotal)}\nMax Healing: {round(maxTotal)}\nAvg Healing: {round(avgTotal)}\n\n"
            resultsmsg += f"Min HPS: {round(minHPS)}\nMax HPS: {round(maxHPS)}\nAvg HPS: {round(avgHPS)}\n"
        else:
            resultsmsg += f"Total Healing: {totalheal[0]}\nHPS: {round(totalheal[0]/config['duration'])}"
        
        if "log" in args and ctx.author.id in self.client.VIP:
            r = requests.post('https://pastebin.com/api/api_post.php', data={"api_dev_key" : "", "api_option" : "paste", "api_paste_code" : sim["log"], "api_paste_private" : 0, "api_paste_name" : f"Gloomfury - {name}", "api_paste_expire_date": "1M"})
            embed=discord.Embed(title=f"Gloomfury - {name}", description=f"Fight Duration - {strftime('%M:%S', gmtime(config['duration']))}   |   Simulations - {simulations}", color=0x0040ff, url=r.text)
        else:
            embed=discord.Embed(title=f"Gloomfury - {name}", description=f"Fight Duration - {strftime('%M:%S', gmtime(config['duration']))}   |   Simulations - {simulations}", color=0x0040ff)
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/923032334415040573/39af89e68b182e6884bdb31fa813b101.webp?size=96")
        embed.add_field(name="Stats", value=statmsg, inline=True)
        embed.add_field(name="Skills", value=skillmsg, inline=True)
        embed.add_field(name="Casts", value=castmsg, inline=True)
        embed.add_field(name="Abilities", value=healmsg, inline=True)
        embed.add_field(name="Results", value=resultsmsg, inline=True)
        await ctx.send(embed=embed)
        