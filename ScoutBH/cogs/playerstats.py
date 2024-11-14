import discord
import requests
import json
import asyncio
import os
from pymongo import MongoClient
from math import fabs, floor, ceil
from io import BytesIO
from func.playerCard import *
from func.buffs import *
from func import decoder
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from google.oauth2 import service_account


def setup(client):
    client.add_cog(Playerstats(client))

class Playerstats(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.Decoder = decoder.APIDecoder()

        self.SERVICE_ACCOUNT_FILE = "static/gapi/keys.json"
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.sheetIDs = {
            1 : "1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s", # Mage
            2 : "1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0", # Archer
            3 : "1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw",  # Shaman
            0 : "150QNvGaKPkOQ6pKD1z2SPWfXjjYS0p7RrH8LMRWFIC8" # Warrior
        }

        MONGO = os.environ["mongo"]
        self.cluster = MongoClient(MONGO)
        self.db = self.cluster["scout"]
        self.collection = self.db["items"]
        self.collectionGen = self.db["items-gen"]

        service = build("sheets", "v4", credentials=self.creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=self.sheetIDs[1],
            range=f"data!AB2:AB200",
            majorDimension="COLUMNS"
            ).execute()
        self.trusted = result.get("values", [])[0]

        self.minimum_tiers = {
            "hammer" : 4,
            "bow" : 4,
            "staff" : 4,
            "sword" : 4,
            "armlet" : 2,
            "armor" : 2,
            "bag" : 0,
            "boot" : 2,
            "glove" : 2,
            "ring" : 0,
            "amulet" : 0,
            "quiver" : 2,
            "shield" : 2,
            "totem" : 2,
            "orb" : 2
        }

        self.linkPlayers.start()

    async def requestCharacterLink(self, author, charname, itemid):
        request = {
            "discord" : author,
            "character" : charname,
            "item" : itemid,
            "count" : 0
        }

        self.client.characterLinkRequests.append(request)

    @tasks.loop(seconds=10)
    async def linkPlayers(self):
        renew = []
        collection = self.db["characters"]

        for req in self.client.characterLinkRequests:
            linked = False
            req["count"] += 1

            url = 'https://hordes.io/api/item/get'
            cookies = {"sid":''}
            data = {"auction": 1, "ids":[req["item"]]}
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            itemdata = json.loads(r.text)

            if len(itemdata) and itemdata[0]["name"] == req["character"]:
                linked = True
                x = {
                    "_id" : req["discord"].id
                }
                y = {
                    "name" : req["discord"].name
                }

                z = {
                    "characters" : {
                        "$each" : [req["character"]]
                    }
                }

                collection.update_one(x, {"$set" : y}, upsert=True)
                collection.update_one(x, {"$addToSet" : z})

                try:
                    user = self.client.scoutGuild.get_member(req["discord"].id)
                    dm = await user.create_dm()
                    await dm.send(f"The following characters were registered under your account: {req['character']}")
                    await self.characterRegisterLog(req["discord"], req["character"])
                except:
                    pass


            if req["count"] <= 30 and not linked:
                renew.append(req)
            elif not linked:
                try:
                    user = self.client.scoutGuild.get_member(req["discord"].id)
                    dm = await user.create_dm()
                    await dm.send(f"Character link request has timed out for: {req['character']}")
                except:
                    pass

        
        self.client.characterLinkRequests = renew
    
    async def characterRegisterLog(self, author, charname):
        channel = self.client.get_channel(1001526619460083902)
        colour = 0x27bd90

        embed=discord.Embed(title=author.id, description=charname, color=colour)
        embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=author.avatar_url)
        await channel.send(embed=embed)

    async def tierlistlog(self, f, data, author, pclass, name):
        channel = self.client.get_channel(976503812250566736)
        colours = {
            1 : 0x42c6ff,
            2 : 0x31c31d,
            3 : 0x1d2ae2,
            0 : 0x9d5353
        }

        embed=discord.Embed(title=name, description=data, color=colours[pclass])
        embed.set_image(url="attachment://output.png")
        embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=author.avatar_url)

        await channel.send(file=f, embed=embed)
        

    @commands.command(name="playerstats")
    async def playerstats(self, ctx, *args):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        
        args = [a for a in args]

        r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : args[0], "order" : "gs", "limit" : 25, "offset" : 0}))
        players = json.loads(r.text)
        found = False
        for player in players:
            if args[0].lower() == player["name"].lower():
                playerinfo = player
                found = True
        if not found:
            return await ctx.send("Unknown player")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        itemIDs = {}
        itemSets = []
        maxupgrade = False
        altered = False
        maxtier = False
        charms = ["Tattooed Skull","Hardened Egg","Blue Marble","Little Bell","Ship Pennant"]
        buffNames = ["enchant","arctic","hypo","armor","warcry","crusader","bulwark","temporal","cranial","invigorate","howl"]
        buffs = [enchantBuff,arcticBuff,hypothermicBuff,armorBuff,warcryBuff,crusaderBuff,bulwarkBuff,temporalBuff,cranialBuff,invigorateBuff,howlBuff]
        ranks = [0,4000,8000,12000,16000,20000,24000,28000,32000,36000,40000,44000,48000]
        playerCharms = []

        if "tierlist" in args[1:]:
            SPREADSHEET_ID = self.sheetIDs[playerinfo["pclass"]]

            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()

            if args[1][0] == "(" and args[1][-1] == ")":
                NAME = " ".join([playerinfo["name"],args[1]])
            else:
                NAME = playerinfo["name"]

            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"data!A2:O1000",
                majorDimension="COLUMNS"
                ).execute()

            resp = result.get("values", [])

            loc = resp[0].index(NAME)
            
            if playerinfo["pclass"] == 1:
                gearloc = 4
            elif playerinfo["pclass"] == 2:
                gearloc = 4
            elif playerinfo["pclass"] == 3:
                gearloc = 6
            elif playerinfo["pclass"] == 0:
                gearloc = 14

            gear = resp[gearloc][loc]
            gear = gear.split(",")
            for id in gear:
                itemIDs[id] = None

            playerCharms = ["Tattooed Skull","Hardened Egg"]

        else:
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
        name = playerinfo["name"]
        pclass = playerinfo["pclass"]
        elo = playerinfo["elo"]
        level = playerinfo["level"]
        faction = playerinfo["faction"]
        currentPrestige = playerinfo["prestige"]
        nextBracket = str((ceil(playerinfo["prestige"]/4000)*4000)/1000)+"k"
        if (ceil(playerinfo["prestige"]/4000)*4000) > 48000:
            nextBracket = "48.0k"
        unallocated = playerinfo["level"]*3
        if "maxprestige" in args:
            rank = 12
            currentPrestige = 48000
            nextBracket = "48.0k"
        elif "noprestige" in args:
            rank = 0
            currentPrestige = 0
            nextBracket = "4.0k"
        if "maxupgrade" in args:
            maxupgrade = True
        if "maxtier" in args:
            maxtier = True

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
            if maxupgrade:
                item["upgrade"] = 7
            elif itemIDs[str(item["id"])] != None:
                if item["upgrade"] != itemIDs[str(item["id"])]:
                    altered = True
                item["upgrade"] = itemIDs[str(item["id"])]
            try:
                item = self.Decoder.decode(item, maxtier)
            except:
                return await ctx.send("Failed to decode item data")
            decodedItems.append(item)
            if not maxtier and not gen:
                if (len(item['bonus_attr_keys']) >= 2 and item["tier"] >= self.minimum_tiers[item["type"]]):
                    x = {
                        "_id" : item["ID"]
                    }

                    y = {
                        "type" : item['type'],
                        "tier" : item['tier'],
                        "quality" : item["quality"],
                        "gearscore" : item["gearscore"],
                        "bound" : item["bound"],
                        "name" : item["name"],
                        "base_stats" : {},
                        "bonus_stats" : {},
                        "bonus_stats_keys" : item["bonus_attr_keys"]
                    }

                    for st in item["attr"]:
                        if item["attr"][st]["bonus"]:
                            y["bonus_stats"][st] = {
                                "value" : item["attr"][st]["value"],
                                "quality" : item["attr"][st]["quality"]
                            }
                        else:
                            y["base_stats"][st] = {
                                "value" : item["attr"][st]["value"],
                                "quality" : item["attr"][st]["quality"]
                            }

                    self.collection.update_one(x, {"$set" : y}, upsert=True)

            for stat in item["attr"]:
                if stat in allocatedStats:
                    allocatedStats[stat] += item["attr"][stat]["value"]
                else:
                    realStats[stat] += item["attr"][stat]["value"]
            realStats["gs"] += item["gearscore"]

        for charm in playerCharms:
            realStats["gs"] += 30


        realStats_tl = realStats.copy()

        realStats_tl["mov"] += 5
        realStats_tl["mp"] += 50
        realStats_tl["if"] += 15
        realStats_tl["min"] += 5
        realStats_tl["max"] += 5
        realStats_tl["hpr"] += 2
        realStats_tl["mpr"] += 2
        realStats_tl["mov"] += 5
        realStats_tl["hp"] += 30
        realStats_tl["if"] += 15
        realStats_tl["cri"] += 5
        realStats_tl["has"] += 3
        realStats_tl["hp"] += 30
        realStats_tl["min"] += 5
        realStats_tl["max"] += 5

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
        if "maxbuff" in args[1:]: args.extend(["enchant4", "arctic4", "warcry4", "crusader4", "temporal4"])
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
        evaluated = evalstats(realStats, pclass)

        tierlistRank = None
        Overall_Score = None
        pos = 999

        realStats_tl = initreal(allocatedStats, realStats_tl, bloodline, 1)
        evaluated_tl = evalstats(realStats_tl, pclass)

        SPREADSHEET_ID = self.sheetIDs[pclass]
        service = build("sheets", "v4", credentials=self.creds)
        sheet = service.spreadsheets()

        if pclass == 0:
            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"data!AG6:AH21",
                majorDimension="ROWS"
                ).execute()
        else:
            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"data!X6:Y21",
                majorDimension="ROWS"
                ).execute()

        ranks = result.get("values", [])

        ranks[0][0] = 0
        
        Overall_Score = getBuildScore(evaluated_tl, realStats_tl, pclass)


        for r in reversed(ranks):
            if Overall_Score >= float(r[0]):
                tierlistRank = r[1]
                break

        if tierlistRank == "SS":
            if pclass == 0:
                result = sheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"data!AD2:AD",
                    majorDimension="COLUMNS"
                    ).execute()
            else:
                result = sheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"data!U2:U",
                    majorDimension="COLUMNS"
                    ).execute()

            scores = result.get("values", [])
            pos = 1
            for score in scores[0]:
                if float(f"{Overall_Score:.7f}") >= float(score):
                    break
                pos += 1
            
    
        
        with BytesIO() as image_binary:
            generateCard(name,level,pclass,faction,currentPrestige,nextBracket,rank,elo,allocatedStats,realStats,evaluated,decodedItems,playerCharms,activeBuffs,tierlistRank,Overall_Score,pos).save(image_binary, "PNG")
            image_binary.seek(0)
            f = discord.File(fp=image_binary, filename="output.png")

            try:
                card = await ctx.send(file=f)
                image_binary.seek(0)
            except:
                await asyncio.sleep(1)
                card = await ctx.send(file=f)
            if "tierlist" not in args[1:] and not isinstance(ctx.channel, discord.channel.DMChannel):
                await prompt.delete()
                await inp.delete()

            def emojicheck(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["➕","🔒"] and reaction.message == card
                
            restricted = discord.utils.get(self.client.scoutGuild.roles, name="restricted")
            
            tlcheck = "tierlist" not in args[1:] and not gen and not altered and not maxupgrade and len(items) == 9 and level > 40 and realStats["if"] < 200 and restricted not in self.client.scoutGuild.get_member(ctx.author.id).roles
            regcheck = True #ctx.author.id in self.client.VIP or ctx.author.id in self.client.ruin

            if tlcheck:
                await card.add_reaction("➕")
            if regcheck:
                await card.add_reaction("🔒")


            confirmation = [""]
            if tlcheck or regcheck:
                try:
                    confirmation = await self.client.wait_for("reaction_add", timeout=30.0, check=emojicheck)
                except:
                    pass

            
      
                if str(confirmation[0]).encode("utf-8") == "🔒".encode("utf-8") and regcheck:
                    await ctx.send(f"Link {name} to your discord account? Type 'yes' to confirm")
                    rinp = await self.client.wait_for('message', check=check)

                    if rinp.content.lower() == "yes":
                        await ctx.send("Post an item on merchant with requested character and enter the id below")
                        idinp = await self.client.wait_for('message', check=check)

                        if idinp.content.isnumeric():
                            await self.requestCharacterLink(ctx.author, name, idinp.content)
                            await ctx.send("Request sent")
                        else:
                            await idinp.add_reaction("❎")

                    else:
                        await rinp.add_reaction("❎")

                elif str(confirmation[0]).encode("utf-8") == "➕".encode("utf-8") and tlcheck:# and str(ctx.author.id) in self.trusted:
                    if args != [args[0], "maxprestige"]:
                        dmgMultiplier = 1
                        maxupgrade = False

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

                        realStats["mov"] += 5
                        realStats["mp"] += 50
                        realStats["if"] += 15
                        realStats["min"] += 5
                        realStats["max"] += 5
                        realStats["hpr"] += 2
                        realStats["mpr"] += 2
                        realStats["mov"] += 5
                        realStats["hp"] += 30
                        realStats["if"] += 15
                        realStats["cri"] += 5
                        realStats["has"] += 3
                        realStats["hp"] += 30
                        realStats["min"] += 5
                        realStats["max"] += 5
                        
                        allocatedStats["sta"] += level*2
                        realStats["hp"] += level*8
                        allocatedStats[bloodline] += level

                        if 0 and "fullstam" in args:
                            allocatedStats["sta"] += unallocated
                        else:
                            allocatedStats[bloodline] += unallocated

                        decodedItems = []
                        for item in items:
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

                        realStats = initreal(allocatedStats, realStats, bloodline, dmgMultiplier)
                        evaluated = evalstats(realStats, pclass)

                    if "alt" in args:
                        await ctx.send("Enter alt identifier tag")
                        inp2 = await self.client.wait_for('message', check=check)
                        name = f"{name} ({inp2.content.strip().lower()})"
                        

                    itemdata = ",".join(list(itemIDs.keys()))
                    if pclass == 3:
                        data = [[name, round(evaluated["DPS"]), round(evaluated["Burst"]), round(evaluated["eHp"]), evaluated["hpValue"], f'{realStats["has"]:.1f}', itemdata,f"{ctx.author.name}#{ctx.author.discriminator}"]]
                    elif pclass == 0:
                        data = [[name, realStats["hp"], realStats["def"], realStats["blo"], realStats["min"], realStats["max"], realStats["cri"], realStats["has"]]]
                        data2 = [[itemdata,f"{ctx.author.name}#{ctx.author.discriminator}"]]
                    else:
                        data = [[name, round(evaluated["DPS"]), round(evaluated["Burst"]), round(evaluated["eHp"]), itemdata, f"{ctx.author.name}#{ctx.author.discriminator}"]]
                        
                    SPREADSHEET_ID = self.sheetIDs[pclass]
                    service = build("sheets", "v4", credentials=self.creds)
                    sheet = service.spreadsheets()

                    #DATA SHEET
                    if pclass == 0:
                        result = sheet.values().get(
                            spreadsheetId=SPREADSHEET_ID,
                            range="data!R2"
                            ).execute()

                        end = int(result.get("values", [])[0][0])+1

                        result = sheet.values().get(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"data!A2:A",
                            majorDimension="COLUMNS"
                            ).execute()

                        resp = result.get("values", [])
                        names = resp[0]

                        if name in names:
                            loc = names.index(name)
                            insertPoint = names.index(name)+2
                        else:
                            insertPoint = end+1
                            end += 1
                        
                        sheet.values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"data!A{insertPoint}",
                            valueInputOption="USER_ENTERED",
                            body={"values":data}
                            ).execute()

                        sheet.values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"data!O{insertPoint}",
                            valueInputOption="USER_ENTERED",
                            body={"values":data2}
                            ).execute()

                    else:
                        result = sheet.values().get(
                            spreadsheetId=SPREADSHEET_ID,
                            range="data!I2"
                            ).execute()

                        end = int(result.get("values", [])[0][0])+1

                        result = sheet.values().get(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"data!A2:D{end}",
                            majorDimension="COLUMNS"
                            ).execute()

                        resp = result.get("values", [])
                        names = resp[0]

                        if data[0][0] in names:
                            loc = names.index(data[0][0])
                            insertPoint = names.index(data[0][0])+2
                        else:
                            insertPoint = end+1
                            end += 1
                        
                        request = sheet.values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"data!A{insertPoint}",
                            valueInputOption="USER_ENTERED",
                            body={"values":data}
                            ).execute()

                    await self.tierlistlog(f, inp.content, ctx.author,  pclass, name)
                    return await ctx.send(f"Updated tier list for {data[0][0]}")


