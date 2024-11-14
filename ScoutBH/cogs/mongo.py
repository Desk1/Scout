from logging import exception
import os
from numpy import NaN
import requests
import json
import discord
import asyncio
from io import BytesIO
from pymongo import MongoClient
from func.res import attr_factors, attr_names, attr_combos
from func.itemCard import *
from func import decoder
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord.utils import get


def setup(client):
    client.add_cog(Mongo(client))

class Mongo(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.Decoder = decoder.APIDecoder()
        self.attr_names = attr_names.attr_info
        self.attr_factors = attr_factors.attr_factors
        self.names = {}
        for x in self.attr_names:
            self.names[self.attr_names[x]["long"].lower()] = self.attr_names[x]["short"]

        MONGO = os.environ["mongo"]
        self.cluster = MongoClient(MONGO)
        self.db = self.cluster["scout"]

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

        self.archer_desireable = attr_combos.archer_desireable

        self.mage_desireable = attr_combos.mage_desireable

        self.shaman_desireable = attr_combos.shaman_desireable

        self.warrior_desireable = attr_combos.warrior_desireable

        self.type_table = {
            "staff" : self.mage_desireable,
            "orb" : self.mage_desireable,
            "bow" : self.archer_desireable,
            "quiver" : self.archer_desireable,
            "hammer" : self.shaman_desireable,
            "totem" : self.shaman_desireable,
            "sword" : self.warrior_desireable,
            "shield" : self.warrior_desireable,
            "armlet" : "misc",
            "armor" : "misc",
            "bag" : "misc",
            "boot" : "misc",
            "glove" : "misc",
            "ring" : "misc",
            "amulet" : "misc",
        }


        self.updateVIP.start()

    @commands.command(name="findgear")
    async def findgear(self, ctx, *args):
        #if ctx.author.id not in self.client.VIP:
        #    return await ctx.send("This command is only available for VIP users")
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("You must be in the scout server to use this command")
                
        collection = self.db["items"]

        args = list(args)

        statsSearch = {}
        quality = 0
        tier = 0
        tierGTE = False
        itemtype = False
        bound = -1
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
                qualityType = "$gte"
                if a[0] == "<":
                    qualityType = "$lte"
                    a = a[1:]
                elif a[0] == "=":
                    qualityType = False
                    a = a[1:]
                elif a[0] == ">":
                    a = a[1:]
                quality = a[:-1]
            elif a[-1] == "+":
                tierGTE = True
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
                statsSearch[f"{self.altnames[a.lower()]}"] = None
            elif a.lower() in self.names.keys():
                statsSearch[f"{self.names[a.lower()]}"] = None
            elif a.lower() in self.names.values():
                statsSearch[f"{a.lower()}"] = None
                
            elif a.lower() in ["unbound", "noncb", "non-cb"]:
                bound = 0
            elif a.lower() in ["bound", "cb", "characterbound"]:
                bound = 2

        query = {}
        if quality:
            if not qualityType:
                query["quality"] = int(quality)
            else:
                query["quality"] = {qualityType : int(quality)}
        if tier:
            if tierGTE:
                query["tier"] = {"$gte" : int(tier)-1}
            else:
                query["tier"] = int(tier)-1
        if itemtype:
            query["type"] = itemtype
        if bound != -1:
            query["bound"] = bound
        if len(statsSearch) > 0:
            statsQuery = []
            for s in statsSearch:
                if s[0] == ":":
                    statsQuery.append(s[1:])
                    query[f"bonus_stats.{s[1:]}.quality"] = {"$gte" : statsSearch[s]}

                elif s[0] == "=":
                    statsQuery.append(s[1:])
                    query[f"bonus_stats.{s[1:]}.value"] = {"$gte" : statsSearch[s]}

                else:
                    statsQuery.append(s)
                    

            query["bonus_stats_keys"] = {"$all" : statsQuery}

        mydoc = collection.find(query)

        itemIDs = []
        if mydoc.count() == 0:
            await ctx.send("None found")
        elif mydoc.count() > 150:
            await ctx.send("Too many items. Try giving a more specific query, e.g:\n>findgear staff t7+ int stam crit 85%")
        else:
            for x in mydoc:
                itemIDs.append(x["_id"])

            url = 'https://hordes.io/api/item/get'
            data = {"ids":itemIDs}
            cookies = {"sid":''}
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            itemsRaw = json.loads(r.text)
            items = []
            for itemRaw in itemsRaw:
                item = self.Decoder.decode(itemRaw)
                try:
                    docBound = x["bound"]
                except:
                    docBound = -1
                if item["bound"] != docBound:
                    x = {"_id" : item["ID"]}
                    y = {"$set" : {"bound" : item["bound"]}}
                    collection.update_one(x, y, upsert=True)

                itemClass = 0
                """
                if find_common(item['bonus_attr_keys'], ["if","luc"]) == 2:
                    itemClass = 0

                elif self.type_table[item["type"]] == self.mage_desireable or ("int" in item["bonus_attr_keys"] and self.type_table[item["type"]] == "misc"):
                    itemClass = 1

                elif self.type_table[item["type"]] == self.archer_desireable or ("dex" in item["bonus_attr_keys"] and self.type_table[item["type"]] == "misc"):
                    itemClass = 2

                elif self.type_table[item["type"]] == self.shaman_desireable or ("wis" in item["bonus_attr_keys"] and self.type_table[item["type"]] == "misc"):
                    itemClass = 3

                elif self.type_table[item["type"]] == "misc" and "str" not in item["bonus_attr_keys"]:
                    found = False
                    for combo in self.shaman_desireable:      
                        if find_common(item['bonus_attr_keys'], combo) >= 3:
                            found = True
                            break
                    if found:
                        itemClass = 3
                """
                overallScore = 0

                items.append((item,overallScore,itemClass))

            confirmed = [x[0]["ID"] for x in items]
            for id in itemIDs:
                if id not in confirmed:
                    collection.delete_one({"_id" : id})


            if "raw" in args:
                msg = ""

                for item in items:
                    msg += f"{item[0]['name']} • {item[0]['quality']}\n{item[0]['ID']}\n"


                await ctx.send(msg)

            else:
                with BytesIO() as image_binary:
                    generateItemCard(items, []).save(image_binary, "PNG")
                    image_binary.seek(0)
                    f = discord.File(fp=image_binary, filename="output.png")

                try:
                    await ctx.send(file=f)
                except:
                    await asyncio.sleep(1)
                    await ctx.send(file=f)

    @commands.has_role("Owner")
    @commands.command(name="vip")
    async def vip(self, ctx, user : discord.User, time=None):
        collection = self.db["users"]

        """
        try:
            time = int(time)
        except:
            return await ctx.send(f"Invalid duration {time}")

        if user.id in self.client.VIP:
            users = collection.find()

            for u in users:
                if u["_id"] == user.id:
                    currentDate = datetime.strptime(u["VIPuntil"], "%d-%m-%y")
        else:
            currentDate = datetime.today()

        endDate = currentDate + timedelta(days=int(time))
        """

        x = {
            "_id" : user.id
        }

        y = {
            "name" : user.name,
            "VIPuntil" : datetime.today().strftime("%d-%m-%y")
        }

        collection.update_one(x, {"$set" : y}, upsert=True)

        self.updateVIP.restart()
        await ctx.send("Success")

    @commands.command(name="storage")
    async def stored(self, ctx, *args):
        if ctx.author.id not in self.client.VIP:
            return await ctx.send("This command is only available for VIP users")
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")

        collection = self.db["items-gen"]

        if "clear" in args or "deleteall" in args:
            await ctx.send(f"Type 'yes' to confirm deletion of all stored items for user {ctx.author.name}")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            inp = await self.client.wait_for('message', check=check)
            if inp.content.lower() == "yes":
                collection.delete_one({"_id" : ctx.author.id})
                await ctx.send("Storage cleared")
            else:
                await ctx.send("Aborted")

        elif "remove" in args or "delete" in args:
            ids = list(args)
            if "remove" in args:
                ids.remove("remove")
            else:
                ids.remove("delete")

            x = {
                "_id" : ctx.author.id
            }

            y = {}

            for id in ids:
                y[id] = 1

            collection.update(x, {"$unset" : y})

            await ctx.send("Success")

        elif "add" in args or "addset" in args:
            prompt = await ctx.send("Paste auxi/itemID info here: (each item ID must be on new line)")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            inp = await self.client.wait_for('message', check=check)

            itemIDs = {}

            parsed = inp.content.split("\n")
            for idx, i in enumerate(parsed):
                if "%" in i:
                    if "+" in parsed[idx+1]:
                        itemIDs[i[i.index("%")+4:]] = int(parsed[idx+1][parsed[idx+1].index("+")+1:])
                    else:
                        itemIDs[i[i.index("%")+4:]] = None
                else:
                    if "+" in i:
                        if i[:i.index("+")-1].isnumeric():
                            itemIDs[i[:i.index("+")-1]] = int(i[i.index("+")+1:])
                    else:
                        if i.isnumeric() or i[0] == "-":
                            itemIDs[i] = None
            if len(itemIDs.keys()) > 150:
                return await ctx.send("Too many items")

            apiIDS = []
            genIDS = []
            for k in itemIDs.keys():
                if k[0] == "-":
                    genIDS.append(k)
                else:
                    apiIDS.append(k)

            if len(genIDS) > 0:
                gen = True

            if len(apiIDS) == 0:
                itemsRaw = []
            else:
                url = 'https://hordes.io/api/item/get'
                data = {"ids":apiIDS}
                cookies = {"sid":''}
                r = requests.post(url, data=json.dumps(data),cookies=cookies)
                itemsRaw = json.loads(r.text)

            items = []

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

                        itemsRaw.append(templates[count])
                        count += 1

            for itemRaw in itemsRaw:
                if itemIDs[str(itemRaw["id"])] != None:
                    itemRaw["upgrade"] = itemIDs[str(itemRaw["id"])]
                item = self.Decoder.decode(itemRaw)

                items.append(item)

            if items == []:
                return await ctx.send("Unknown items")

            doc = collection.find_one({"_id" : ctx.author.id})

            if doc:
                try:
                    num = doc["count-set"]
                except:
                    collection.update_one({"_id" : ctx.author.id}, {"$set" : {"count-set" : 0}}, upsert=True)
                    doc = collection.find_one({"_id" : ctx.author.id})
                    num = doc["count-set"]
            else:
                num = 0

            try:
                if len(doc) > 152:
                    return await ctx.send("Stored item limit reached")
            except:
                pass
            
            if args[0] == args[-1]:
                idgen = f"+{ctx.author.name[:4].upper()}{num+1}"
            else:
                idgen = f"+{args[-1]}"

            x = {
                "_id" : ctx.author.id
            }

            y = {
                "count-set" : num+1,
                idgen : list(itemIDs.keys())
            }

            collection.update_one(x, {"$set" : y}, upsert=True)

            await ctx.send(f"Stored item set with ID {idgen}")
        else:
            doc = collection.find_one({"_id" : ctx.author.id})
            if not doc:
                return await ctx.send("No items found")

            url = 'https://hordes.io/api/item/get'
            data = {"ids":[91558164]}
            cookies = {"sid":''}
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            itemsRaw = json.loads(r.text)[0]

            itemsToHydrate = {}
            itemsHydrated = []
            for x in doc:
                if x[0] == "-":
                    itemsToHydrate[x] = doc[x]
                if x[0] == "+":
                    z = {
                        "ID" : x,
                        "type" : "itemSet",
                        "name" : "Item Set",
                        "quality" : 200
                    }
                    itemsHydrated.append((z,0,0))

            for item in itemsToHydrate:
                itemsRaw["rolls"] = itemsToHydrate[item]["rolls"]
                itemsRaw["upgrade"] = itemsToHydrate[item]["upgrade"]
                itemsRaw["type"] = itemsToHydrate[item]["type"]
                itemsRaw["tier"] = itemsToHydrate[item]["tier"]
                itemsRaw["id"] = item

                itemsHydrated.append((self.Decoder.decode(itemsRaw), 0, 0))

            if "raw" in args:
                msg = ""

                for item in itemsHydrated:
                    msg += f"{item['name']} • {item['quality']}\n{item['ID']}\n"


                await ctx.send(msg)
            else:
                with BytesIO() as image_binary:
                    generateItemCard(itemsHydrated, "").save(image_binary, "PNG")
                    image_binary.seek(0)
                    f = discord.File(fp=image_binary, filename="output.png")

                    try:
                        await ctx.send(file=f)
                        image_binary.seek(0)
                    except:
                        await asyncio.sleep(1)
                        await ctx.send(file=f)

 
    @commands.command(name="vips")
    async def vips(self, ctx):
        if ctx.author.id == 225697391926444033:

            collection = self.db["users"]

            doc = collection.find()

            msg = ""
            for x in doc:
                msg += f"{x['name']}  -  {x['VIPuntil']}\n"

            await ctx.send(msg)
            await ctx.send(self.client.VIP)

    @commands.has_role("Owner")
    @commands.command(name="register")
    async def register(self, ctx, userid, characters):
        collection = self.db["characters"]
        userid = int(userid)
        user = self.client.scoutGuild.get_member(userid)
        dm = await user.create_dm()

        if characters == "[delete]":
            collection.delete_one({
                "_id" : userid
            })
        
        else:
            characters = characters.split(",")

            x = {
                "_id" : userid
            }

            y = {
                "name" : user.name
            }

            z = {
                "characters" : {
                    "$each" : characters
                }
            }

            collection.update_one(x, {"$set" : y}, upsert=True)
            collection.update_one(x, {"$addToSet" : z})

            await dm.send(f"The following characters were registered under your account: {characters}")

        await ctx.message.add_reaction("🟩")


    @tasks.loop(seconds=180)
    async def updateVIP(self):
        collection = self.db["users"]
    
        doc = collection.find()

        scoutServer = self.client.get_guild(872255568922947644)
        roleVIP = get(scoutServer.roles, id=876915536292900895)
        currentDate = datetime.today()

        for x in doc:
            user = scoutServer.get_member(int(x["_id"]))
            try:
                if x["_id"] not in self.client.VIP:
                    self.client.VIP.append(x["_id"])
                await user.add_roles(roleVIP)
            except:
                #print(e, x["name"])
                pass
            """
            if datetime.strptime(x["VIPuntil"], '%d-%m-%y') > currentDate:
                try:
                    if x["_id"] not in self.client.VIP:
                        self.client.VIP.append(x["_id"])
                    await user.add_roles(roleVIP)
                except Exception as e:
                    print(e, x["name"])
                
            elif datetime.strptime(x["VIPuntil"], '%d-%m-%y') < currentDate:
                try:
                    if x["_id"] in self.client.VIP:
                        self.client.VIP.remove(x["_id"])
                    collection.delete_one({"_id" : x["_id"]})
                    await user.remove_roles(roleVIP)
                    await user.send("Your VIP subscription has ended")
                except Exception as e:
                    print(e)
            """





