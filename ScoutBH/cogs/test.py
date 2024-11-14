import discord
import requests
import json
import asyncio
import os
from pymongo import MongoClient
from math import floor, ceil
from io import BytesIO
from func.playerCard import *
from func.itemCard import *
from func.buffs import *
from func import decoder
from discord.ext import commands
from googleapiclient.discovery import build
from google.oauth2 import service_account


def setup(client):
    client.add_cog(Test(client))

class Test(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.Decoder = decoder.APIDecoder()

        self.SERVICE_ACCOUNT_FILE = "static/gapi/keys.json"
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.sheetIDs = {
            1 : "1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s", # Mage
            2 : "1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0", # Archer
            3 : "1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw"  # Shaman
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

    def tlremove(self, mode, list, name):
        if mode == "remove":
            if 1==1:
                try:
                    SPREADSHEET_ID = self.sheetIDs[1]
                except:
                    return print("err1")

                service = build("sheets", "v4", credentials=self.creds)
                sheet = service.spreadsheets()

                #DATA SHEET
                result = sheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range="data!I2"
                    ).execute()

                end = int(result.get("values", [])[0][0])+1

                if list.lower() == "mage" or list.lower() == "archer":
                    endletter = "F"
                    colummnLen = 6
                elif list.lower() == "shaman":
                    endletter = "H"
                    colummnLen = 8

                result = sheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"data!A2:{endletter}{end}",
                    majorDimension="COLUMNS"
                    ).execute()

                resp = result.get("values", [])
                names = resp[0]

                if name in names:
                    loc = names.index(name)
                    for i in range(colummnLen):
                        resp[i].pop(loc)
                        resp[i].append("")
                else:
                    return print("err2")

                request = sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"data!A2",
                    valueInputOption="USER_ENTERED",
                    body={
                        "values":resp,
                        "majorDimension":"COLUMNS"
                        }
                    ).execute()

                print(f"Removed {name} from {list} tierlist")
            else:
                print  ("Permission denied")

    async def out(self, pl, items):
        channel = self.client.get_channel(872509991922303036)
        with BytesIO() as image_binary:
            if items == []:
                f = None
            else:
                generateItemCard(items, []).save(image_binary, "PNG")
                image_binary.seek(0)
                f = discord.File(fp=image_binary, filename="output.png")

            await channel.send(f"`{pl}`", file=f)

        self.tlremove("remove","mage",pl)

    @commands.command(name="fix")
    @commands.has_role("Owner")
    async def fix(self, ctx):
        if self.client.dev:
            with open("./TOCHECK.txt", "r") as f:
                for pl in f:
                    args = pl.strip().split(" ")
                    args.append("tierlist")
                    r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : args[0], "order" : "gs", "limit" : 25, "offset" : 0}))
                    players = json.loads(r.text)
                    found = False
                    for player in players:
                        if args[0].lower() == player["name"].lower():
                            playerinfo = player
                            found = True
                    if not found:
                        print("not found")
                        await self.out(pl, [])
                        continue

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
                            range=f"data!A2:G1000",
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

                        gear = resp[gearloc][loc]
                        gear = gear.split(",")
                        for id in gear:
                            itemIDs[id] = None

                    if len(itemIDs) < 9:
                        await self.out(pl, [])
                        continue

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
                        decodedItems.append((item, 0, 0))


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
                    evaluated = evalstats(realStats)

                    tierlistRank = None
                    Overall_Score = None
                    if pclass != 0:
                        realStats_tl = initreal(allocatedStats, realStats_tl, bloodline, 1)
                        evaluated_tl = evalstats(realStats_tl)

                        SPREADSHEET_ID = self.sheetIDs[pclass]
                        service = build("sheets", "v4", credentials=self.creds)
                        sheet = service.spreadsheets()

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
                    

                    bad = level < 42 or len(items) < 9 or (evaluated_tl["eHp"] < 5000 and evaluated_tl["DPS"] < 400) or (evaluated_tl["eHp"] > 6000 and evaluated_tl["DPS"] < 300) or realStats_tl["if"] > 100

                    if bad:
                        await self.out(pl, decodedItems)
    
    @commands.command(name="block")
    @commands.has_role("Owner")
    async def block(self, ctx):
        if self.client.dev:
            with open("./TOCHECK.txt", "r") as f:
                for pl in f:
                    args = pl.strip().split(" ")
                    args.append("tierlist")
                    r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : args[0], "order" : "gs", "limit" : 25, "offset" : 0}))
                    players = json.loads(r.text)
                    found = False
                    for player in players:
                        if args[0].lower() == player["name"].lower():
                            playerinfo = player
                            found = True
                    if not found:
                        print("not found")
                        await self.out(pl, [])
                        continue

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
                            range=f"data!A2:G1000",
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

                        gear = resp[gearloc][loc]
                        gear = gear.split(",")
                        for id in gear:
                            itemIDs[id] = None

                    if len(itemIDs) < 9:
                        await self.out(pl, [])
                        continue

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
                        decodedItems.append((item, 0, 0))


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

                    if realStats["blo"] > 0 and len(decodedItems) == 9:

                        Overall_Score = None
                        if pclass != 0:
                            realStats_tl = initreal(allocatedStats, realStats_tl, bloodline, 1)
                            evaluated_tl = evalstats(realStats_tl)

                            SPREADSHEET_ID = self.sheetIDs[pclass]
                            service = build("sheets", "v4", credentials=self.creds)
                            sheet = service.spreadsheets()

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
                        
                        
                        name = pl.strip()
                        if pclass in [1,2,3]:
                            itemdata = ",".join(list(itemIDs.keys()))
                            if pclass == 3:
                                data = [[name, round(evaluated_tl["DPS"]), round(evaluated_tl["Burst"]), round(evaluated_tl["eHp"]), evaluated_tl["hpValue"], f'{realStats_tl["has"]:.1f}', itemdata,f"{ctx.author.name}#{ctx.author.discriminator}"]]
                            else:
                                data = [[name, round(evaluated_tl["DPS"]), round(evaluated_tl["Burst"]), round(evaluated_tl["eHp"]), itemdata, f"{ctx.author.name}#{ctx.author.discriminator}"]]
                                
                            SPREADSHEET_ID = self.sheetIDs[pclass]
                            service = build("sheets", "v4", credentials=self.creds)
                            sheet = service.spreadsheets()

                            #DATA SHEET
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

                            print(pl)

                                
                        