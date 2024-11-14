import discord
import asyncio
import os
from math import ceil, pow
from io import BytesIO
from pymongo import MongoClient
from func.itemCard import *
from func import decoder
from func.res import attr_factors
from func.res import attr_names
from func.res import attr_upgrade_gains
from func.res import attr_random_stats
from func.res import item_info
from discord.ext import commands


def setup(client):
    client.add_cog(Builditem(client))

class Builditem(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.attr_factors = attr_factors.attr_factors
        self.upgrade_gains = attr_upgrade_gains.upgrade_gains
        self.random_stats = attr_random_stats.random_stats 
        self.random_stats_keys = sorted(list(self.random_stats.keys()))
        self.attr_info = attr_names.attr_info
        self.item_info = item_info.item_info
        self.attr_names = attr_names.attr_info
        self.names = {}
        for x in self.attr_names:
            self.names[self.attr_names[x]["short"]] = self.attr_names[x]["long"]
        del self.names["mov"]
        del self.names["att"]

        MONGO = os.environ["mongo"]
        self.cluster = MongoClient(MONGO)
        self.db = self.cluster["scout"]
        self.collection = self.db["items-gen"]

        self.altnames = {
            "stam" : "sta",
            "dext" : "dex",
            "intel" : "int",
            "health" : "hp",
            "mana" : "mp",
            "hp reg" : "hpr",
            "hp regen" : "hpr",
            "mp reg" : "mpr",
            "mp regen" : "mpr",
            "min dmg" : "min",
            "max dmg" : "max",
            "crit" : "cri",
            "itemfind" : "if",
            "defence" : "def"
        }

        self.ids = {}
        for x in self.attr_names:
            self.ids[self.attr_names[x]["long"].lower()] = x

        self.Decoder = decoder.APIDecoder()

    @commands.command(name="builditem")
    async def help(self, ctx, tier, itemtype, quality, upgrade=None, store=None):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        
        def find_common(a,b):
            common = 0
            for i in a:
                if i in b:
                    common += 1
            return common

        tier = int(tier[1:])-1
        quality = int(quality[:quality.index("%")])
        itemtype = itemtype.lower()

        if upgrade == None:
            upgrade = 0
        elif upgrade == "store":
            upgrade = 0
            store = True
        else:
            upgrade = int(upgrade.replace("+",""))

        if store == "store":
            store = True

        if quality > 200:
            return await ctx.send("Quality cannot be higher than 200%")
        if upgrade > 10:
            return await ctx.send("Upgrade cannot be higher than +10")

        n_attr_bonus = round((quality / 100) ** 1.5 * 3.6)

        inp = ""
        if n_attr_bonus != 0:
            prompt = await ctx.send("Enter bonus stat info:")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            inp = await self.client.wait_for('message', check=check)
            inp = inp.content.split("\n")

            if len(inp) != n_attr_bonus:
                return await ctx.send(f"Item must have {n_attr_bonus} bonus stats")
        stats = {}
        statsEx = {}
        for i in inp:
            if ":" in i:
                namestartIndex = 0
                nameendIndex = 0
                for c in i:
                    if not c.isalpha():
                        nameendIndex =  i.index(c)
                        break

                valstartIndex = nameendIndex
                valendIndex = i.index("%")
                for c in i:
                    if c.isnumeric():
                        valstartIndex = i.index(c)
                        break
                stats[i[namestartIndex:nameendIndex].lower()] = int(i[valstartIndex:valendIndex])

            elif "=" in i:
                namestartIndex = 0
                nameendIndex = 0
                for c in i:
                    if not c.isalpha():
                        nameendIndex =  i.index(c)
                        break

                valstartIndex = nameendIndex
                for c in i:
                    if c.isnumeric():
                        valstartIndex = i.index(c)
                        break
                statsEx[i[namestartIndex:nameendIndex].lower()] = float(i[valstartIndex:])


        rolls = []
        rolls.append(quality)

        warning = [False,None]
        for stat in stats:
            if stats[stat] > ceil((quality + 100)/2) or stats[stat] < ceil(quality/2):
                warning = [True,stats[stat]]

            if stat.lower() in self.altnames:
                x = self.altnames[stat.lower()]
            else:
                x = stat.lower()

            if x in self.names:
                statName = self.names[x].lower()
            else:
                statName = x.lower()
            
            statID = self.ids[statName]

            if self.attr_names[statID]["short"] == "has":
                statID -= 1
            elif self.attr_names[statID]["short"] == "if":
                statID -= 2
            
            x = statID * ceil(101/len(self.random_stats))
            #print(statName,statID)
            #print("appending: ",x)
            rolls.append(x)
            rolls.append(stats[stat]*2-quality)
        
        statsPer = ["block","critical","haste"]
        for stat in statsEx:
            stat_data = {}

            if stat.lower() in self.altnames:
                x = self.altnames[stat.lower()]
            else:
                x = stat.lower()

            if x in self.names:
                statName = self.names[x].lower()
            else:
                statName = x.lower()
            
            statID = self.ids[statName]

            attr_data = self.attr_factors[itemtype]
            attr_stat = self.random_stats[statID]
            stat_data['level'] = attr_data['baselvl'] + int(tier / attr_data['tiers'] * 100)
            stat_data['weight'] = attr_data['weight']
            stat_data['min'] = attr_stat['min']
            stat_data['max'] = attr_stat['max']
            stat_data['ug'] = self.upgrade_gains[statID]
            stat_data['u'] = upgrade

            if self.attr_names[statID]["short"] == "has":
                statID -= 1
            elif self.attr_names[statID]["short"] == "if":
                statID -= 2


            if statName in statsPer:
                v = statsEx[stat] * 10
                print("d")
            else:
                v = statsEx[stat]

            b1 = (v-(stat_data["u"]*stat_data["ug"]))/(stat_data["level"]*stat_data["weight"])

            q2 = ((b1-stat_data["min"])/(stat_data["max"]-stat_data["min"])) * 10000

            q = int(pow(q2, 1/2))
            
            
            x = statID * ceil(101/len(self.random_stats))
            #print(statName,statID)
            #print("appending: ",x)
            rolls.append(x)
            rolls.append(q*2-quality)

            if q > ceil((quality + 100)/2) or q < ceil(quality/2):
                warning = [True,q]
        
        itemsRaw = {
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

        itemsRaw["rolls"] = rolls
        itemsRaw["upgrade"] = upgrade
        itemsRaw["type"] = itemtype.lower()
        itemsRaw["tier"] = tier
        if store and ctx.author.id in self.client.VIP:
            doc = self.collection.find_one({"_id" : ctx.author.id})

            if doc:
                num = doc["count"]
            else:
                num = 0

            try:
                if len(doc) > 151:
                    return await ctx.send("Stored item limit reached")
            except:
                pass

            idgen = f"-{ctx.author.name[:4].upper()}{num+1}"
            itemsRaw["id"] = idgen

            x = {
                "_id" : ctx.author.id
            }

            y = {
                "count" : num+1,
                idgen : {
                    "rolls" : rolls,
                    "upgrade" : upgrade,
                    "type" : itemtype.lower(),
                    "tier" : tier
                }
            }

        else:    
            itemsRaw["id"] = "GENERATED"

        try:
            itemHydrated = self.Decoder.decode(itemsRaw)
        except Exception as e:
            print(e)
            print(stats)
            print(statsEx)

        with BytesIO() as image_binary:
            generateItemCard([(itemHydrated, 0, 0)], "").save(image_binary, "PNG")
            image_binary.seek(0)
            f = discord.File(fp=image_binary, filename="output.png")

        try:
            itemimg = await ctx.send(file=f)
        except:
            await asyncio.sleep(1)
            itemimg = await ctx.send(file=f)
        try:
            self.collection.update_one(x, {"$set" : y}, upsert=True)
        except:
            pass

