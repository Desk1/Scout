from ast import Bytes
from re import L
import discord
import requests
import json
import asyncio
import os
from math import log
from io import BytesIO
from pymongo import MongoClient
from func.itemCard import *
from func.res import attr_combos
from func import decoder
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from google.oauth2 import service_account

def setup(client):
    client.add_cog(Viewgear(client))

class Viewgear(commands.Cog):
    
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

        self.minimum_tiers = {
            "hammer" : 5,
            "bow" : 5,
            "staff" : 5,
            "sword" : 5,
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


        #self.updateBuilds.start()


    @commands.command(name="viewgear")
    async def viewgear(self, ctx, *args):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")

        tl = False
        tlraw = False
        itemIDs = {}
        itemSets = []

        if "tierlist" in args[1:]:
            tl = True
            if "raw" in args:
                tlraw = True
            r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : args[0], "order" : "gs", "limit" : 25, "offset" : 0}))
            players = json.loads(r.text)
            found = False
            for player in players:
                if args[0].lower() == player["name"].lower():
                    playerinfo = player
                    found = True
            if not found:
                return await ctx.send("Unknown player")

            if args[1][0] == "(" and args[1][-1] == ")":
                NAME = " ".join([playerinfo["name"],args[1]])
            else:
                NAME = playerinfo["name"]


            SPREADSHEET_ID = self.sheetIDs[playerinfo["pclass"]]

            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()

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

            args = [NAME]
        else:
            prompt = await ctx.send("Paste auxi/itemID info here: (each item ID must be on new line)")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            inp = await self.client.wait_for('message', check=check)

            if inp.attachments == []:
                if "ptr" in args and "\n" not in inp.content:
                    parsed = inp.content.split(", ")
                else:
                    parsed = inp.content.split("\n")

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
                    
            else:
                await inp.attachments[0].save("items/input.txt")
                with open("items/input.txt") as f:
                    for i in f:
                        i = i.rstrip("\n")
                        if "%" in i:
                            itemIDs.append(i[i.index("%")+6:])
                        else:
                            if i.isnumeric():
                                itemIDs.append(i)
        
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
            itemsRaw = []
        else:
            if "ptr" in args:
                url = 'https://ptr.hordes.io/api/item/get'
                cookies = {"sid":''}
            else:
                url = 'https://hordes.io/api/item/get'
                cookies = {"sid":''}
            data = {"ids":apiIDS}
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            itemsRaw = json.loads(r.text)

        items = []

        if ctx.author.id in self.client.VIP and len(genIDS) > 0 and "ptr" not in args:
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

        def find_common(a,b):
            common = 0
            for i in a:
                if i in b:
                    common += 1
            return common

        for itemRaw in itemsRaw:
            if itemIDs[str(itemRaw["id"])] != None:
                itemRaw["upgrade"] = itemIDs[str(itemRaw["id"])]
            if "ptr" in args:
                itemRaw["id"] = str(itemRaw["id"]) + " PTR"
                
            item = self.Decoder.decode(itemRaw)

            """
            itemClass = 0
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

            overallScore = getItemScore(item, itemClass, self.client.gears)
            """
            if itemRaw["type"]  != "charm":
                items.append((item,0,0))

            if not gen and "ptr" not in args:
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



        if items == {}:
            print(itemIDs)
            return await ctx.send("Unknown items")

        if "raw" in args or tlraw:
            msg = ""

            for item in items:
                msg += f"{item[0]['name']} • {item[0]['quality']}\n{item[0]['ID']}\n"


            await ctx.send(msg)
            
        else:
            if "ptr" in args:
                args = []
            
            with BytesIO() as image_binary:
                generateItemCard(items, args).save(image_binary, "PNG")
                image_binary.seek(0)
                f = discord.File(fp=image_binary, filename="output.png")

            try:
                await ctx.send(file=f)
            except:
                await asyncio.sleep(1)
                await ctx.send(file=f)

        if not tl and not isinstance(ctx.channel, discord.channel.DMChannel):
            await prompt.delete()
            await inp.delete()

    @tasks.loop(hours=6)
    async def updateBuilds(self):
        cl = {
            1 : "Mage",
            2 : "Archer",
            3 : "Shaman"
        }
        
        for i in cl:
            SPREADSHEET_ID = self.sheetIDs[i]
            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()

            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"Overall {cl[i]} Rankings!A2:A11",
                majorDimension="COLUMNS"
                ).execute()

            resp = result.get("values", [])

            ps = resp[0]
            
            for p in ps:
                args = p.split()
                r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : args[0], "order" : "gs", "limit" : 25, "offset" : 0}))
                players = json.loads(r.text)
                found = False
                for player in players:
                    if args[0].lower() == player["name"].lower():
                        playerinfo = player
                        found = True
                if not found:
                    return "guh"

                if len(args) == 1:
                    NAME = playerinfo["name"]
                else:
                    args[1][0] == "(" and args[1][-1] == ")"
                    NAME = " ".join([playerinfo["name"],args[1]])

                self.client.gears[i][NAME] = {}

                SPREADSHEET_ID = self.sheetIDs[playerinfo["pclass"]]

                service = build("sheets", "v4", credentials=self.creds)
                sheet = service.spreadsheets()

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

                gs = resp[gearloc][loc].split(",")
                itemIDs = {id:None for id in gs}
                
                url = 'https://hordes.io/api/item/get'
                data = {"ids":gs}
                cookies = {"sid":''}
                r = requests.post(url, data=json.dumps(data),cookies=cookies)
                itemsRaw = json.loads(r.text)
                
                for itemRaw in itemsRaw:
                    if itemIDs[str(itemRaw["id"])] != None:
                        itemRaw["upgrade"] = gs[str(itemRaw["id"])]
                    item = self.Decoder.decode(itemRaw)

                    
                    self.client.gears[i][NAME][item["type"]] = item
        


        
        

                


    @commands.has_role("Owner")
    @commands.command(name="updateb")
    async def vip(self, ctx):
        self.updateBuilds.restart()
        await ctx.send("Success")