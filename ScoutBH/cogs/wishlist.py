import discord
import os
import requests
import json
import asyncio
from collections import Counter
from pymongo import MongoClient
from func.res import attr_factors
from func.res import attr_names
from func.itemCard import *
from func import decoder
from discord.ext import commands, tasks


def setup(client):
    client.add_cog(Wishlist(client))

class Wishlist(commands.Cog):
    
    def __init__(self, client):
        self.client = client

        self.attr_names = attr_names.attr_info
        self.attr_factors = attr_factors.attr_factors
        self.Decoder = decoder.APIDecoder()
        self.names = {}
        for x in self.attr_names:
            self.names[self.attr_names[x]["long"].lower()] = self.attr_names[x]["short"]

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
            "hpreg" : "hpr",
            "hpregen" : "hpr",
            "mpreg" : "mpr",
            "mpregen" : "mpr",
            "min dmg" : "min",
            "max dmg" : "max",
            "crit" : "cri",
            "itemfind" : "if",
            "defence" : "def",
            "luck" : "luc",
        }

        self.altitemtypes = {
            "armour" : "armor",
            "chest" : "armor",
            "chestplate" : "chest",
            "shoe" : "boot",
            "shoes" : "boot",
            "boots" : "boot",
            "fists" : "glove",
            "gloves" : "glove"
        }

        MONGO = os.environ["mongo"]
        self.cluster = MongoClient(MONGO)
        self.db = self.cluster["scout"]

        self.client.WL = {}
        self.updateWL.start()

    @commands.command(name="wishlist")
    async def wishlist(self, ctx, *args):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")

        collection = self.db["users"]

        if "add" in args:
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("This command is only available for VIP users")

            doc = collection.find_one({"_id" : ctx.author.id}, {"wishlist" : 1, "_id" : 0})
            for x in doc:
                if x == "wishlist":
                    if len(doc["wishlist"]) > 10:
                        return await ctx.send("Wishlist capacity reached")
            args = list(args)

            statsSearch = {}
            quality = 0
            tier = 0
            itemtype = False
            for a in args:
                if ":" in a or "=" in a:
                    if ":" in a:
                        typeQuery = ":"
                    elif "=" in a:
                        typeQuery = "="

                    statname = a[0:a.index(typeQuery)]

                    if statname.lower() in self.altnames.keys():
                        statsSearch[f"{typeQuery}{self.altnames[statname.lower()]}"] = int(a[a.index(typeQuery)+1:])
                    elif statname.lower() in self.names.keys():
                        statsSearch[f"{typeQuery}{self.names[statname.lower()]}"] = int(a[a.index(typeQuery)+1:])
                    elif statname.lower() in self.names.values():
                        statsSearch[f"{typeQuery}{statname.lower()}"] = int(a[a.index(typeQuery)+1:])



                elif a[-1] == "%":
                    quality = a[:-1]
                elif a[-1] == "+":
                    if a[0].lower() == "t":
                        tier  = a[1:-1]
                    else:
                        tier = a[:-1]
                elif a[0].lower() == "t" and a[1].isdigit():
                    tier = a[1]
                elif a.isdigit():
                    tier = a
                elif a.lower() in self.attr_factors.keys():
                    itemtype = a.lower()
                elif a.lower() in self.altitemtypes.keys():
                    itemtype = self.altitemtypes[a.lower()]
                elif a.lower() in self.altnames.keys():
                    statsSearch[f"{self.altnames[a.lower()]}"] = 0
                elif a.lower() in self.names.keys():
                    statsSearch[f"{self.names[a.lower()]}"] = 0
                elif a.lower() in self.names.values():
                    statsSearch[f"{a.lower()}"] = 0

            if itemtype == False:
                return await ctx.send("Must specify an item type")

            wl = {
                "stats" : {}
            }
            for s in statsSearch:
                if s[0] == ":":
                    wl["stats"][s[1:]] = statsSearch[s]

                elif s[0] == "=":
                    wl["stats"][s[1:]] = statsSearch[s]

                else:
                    wl["stats"][s] = statsSearch[s]

            wl["type"] = itemtype
            wl["tier"] = int(tier)
            wl["quality"] = int(quality)

            x = {
                "_id" : ctx.author.id
            }

            y = {
                "wishlist" : wl
            }

            collection.update_one(x, {"$push" : y}, upsert=True)
            self.updateWL.restart()
            await ctx.send("Success")

        elif "view" in args:
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("This command is only available for VIP users")
            doc = collection.find_one({"_id" : ctx.author.id}, {"wishlist" : 1, "_id" : 0})

            msg = ""
            c = 0
            for w in doc["wishlist"]:
                statlist = []
                for s in w["stats"]:
                    statlist.append(f"{s}:{w['stats'][s]}")

                msg += f"{c} • {w['type'].capitalize()} {w['quality']}% • T{w['tier']} • stats: {statlist}\n"
                c += 1

            if msg == "":
                msg = "None"
            await ctx.send(msg)

        elif "remove" in args or "delete" in args:
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("This command is only available for VIP users")

            ids = [int(i) for i in args if i.isnumeric()]

            await ctx.send(f"Type 'yes' to confirm deletion of ids {ids} from wishlist for user {ctx.author.name}")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            inp = await self.client.wait_for('message', check=check)

            if inp.content.lower() == "yes":
                doc = collection.find_one({"_id" : ctx.author.id}, {"wishlist" : 1, "_id" : 0})
                wl = doc["wishlist"]
                wl = [y for z,y in enumerate(wl) if z not in ids]

                x = {
                    "_id" : ctx.author.id
                }

                y = {
                    "wishlist" : wl
                }

                collection.update_one(x, {"$set" : y}, upsert=True)
                self.updateWL.restart()
                await ctx.send("Success")
            else:
                await ctx.send("Aborted")

        elif "clear" in args or "deleteall" in args:
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("This command is only available for VIP users")

            await ctx.send(f"Type 'yes' to confirm deletion of wishlist for user {ctx.author.name}")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            inp = await self.client.wait_for('message', check=check)
            if inp.content.lower() == "yes":
                x = {
                    "_id" : ctx.author.id
                }

                y = {
                    "wishlist" : []
                }

                collection.update_one(x, {"$set" : y}, upsert=True)
                self.updateWL.restart()
                await ctx.send("Success")
            else:
                await ctx.send("Aborted")

        elif len(args) == 1:
            if args[0].isnumeric():
                id = int(args[0])

                url = 'https://hordes.io/api/item/get'
                data = {"ids":[id]}
                cookies = {"sid":''}
                r = requests.post(url, data=json.dumps(data),cookies=cookies)
                itemRaw = json.loads(r.text)[0]

                item = self.Decoder.decode(itemRaw)
                usersFound = []
                
                for user in self.client.WL:
                    for wish in self.client.WL[user]:
                        check = False
                        if item["type"] == wish["type"]:
                            if item["tier"]+1 >= wish["tier"] and item["quality"] >= wish["quality"]:
                                if Counter(item["bonus_attr_keys"]) == Counter(list(wish["stats"].keys())):
                                    for s in item["bonus_attr_keys"]:
                                        if not item["attr"][s]["quality"] >= wish["stats"][s]:
                                            check = True

                                    if not check:
                                        scoutServer = self.client.get_guild(872255568922947644)
                                        member = scoutServer.get_member(user)

                                        if f"{member.name}#{member.discriminator}" not in usersFound:
                                            usersFound.append(f"{member.name}#{member.discriminator}")

                if usersFound == []:
                    await ctx.send("Found no users who wished for this item")
                else:
                    msg = "Found the following users who wished for this item:\n"
                    for u in usersFound:
                        msg += f"{u}\n"

                    await ctx.send(msg)

        else:
            await ctx.send("Type >help wishlist for info on how to use this command")



    @tasks.loop(hours=12)
    async def updateWL(self):
        collection = self.db["users"]
    
        doc = collection.find({"wishlist" : {"$exists" : True}}, {"wishlist" : 1})

        for user in doc:
            if user["_id"] in self.client.VIP:
                self.client.WL[user["_id"]] = user["wishlist"]




        