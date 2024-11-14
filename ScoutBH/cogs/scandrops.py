from inspect import FullArgSpec
import discord
import requests
import json
import asyncio
import os
from pymongo import MongoClient
from collections import Counter
from math import ceil, floor
from io import BytesIO
from func import decoder
from func.itemCard import *
from func.res import attr_combos
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from google.oauth2 import service_account

def setup(client):
    client.add_cog(Scandrops(client))

class Scandrops(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.Decoder = decoder.APIDecoder()
        self.SERVICE_ACCOUNT_FILE = "static/gapi/keys.json"
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)

        MONGO = os.environ["mongo"]
        self.cluster = MongoClient(MONGO)
        self.db = self.cluster["scout"]
        self.collection = self.db["items"]

        self.minimum_tiers = {
            "hammer" : 4,
            "bow" : 4,
            "staff" : 4,
            "sword" : 4,
            "armlet" : 2,
            "armor" : 2,
            "bag" : 0,
            "boot" : 3,
            "glove" : 3,
            "ring" : 1,
            "amulet" : 1,
            "quiver" : 2,
            "shield" : 2,
            "totem" : 2,
            "orb" : 2
        }

        self.good_tiers = {
            "hammer" : 7,
            "bow" : 7,
            "staff" : 7,
            "sword" : 7,
            "armlet" : 4,
            "armor" : 4,
            "bag" : 1,
            "boot" : 4,
            "glove" : 4,
            "ring" : 3,
            "amulet" : 3,
            "quiver" : 3,
            "shield" : 4,
            "totem" : 4,
            "orb" : 4
        }


        self.blood_table = {
            "staff" : "int",
            "hammer" : "wis",
            "sword" : "str",
            "bow" : "dex"
        }

        self.gen_desireable = attr_combos.gen_desireable

        self.gen2_desireable = attr_combos.gen2_desireable

        self.archer_desireable = attr_combos.archer_desireable

        self.mage_desireable = attr_combos.mage_desireable

        self.shaman_desireable = attr_combos.shaman_desireable

        self.warrior_desireable = attr_combos.warrior_desireable

        self.orb_desireable = attr_combos.orb_desireable

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
        
        if not self.client.dev:
            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()

            result = sheet.values().get(
                spreadsheetId="1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s",
                range=f"data!Z32",
                majorDimension="COLUMNS"
                ).execute()
            self.start_id = int(result.get("values", [])[0][0])

            self.updateStartID.start()
            self.scan.start()
        
        
        

    @commands.command(name="startID")
    async def startID(self, ctx):
        await ctx.send(self.start_id)

    @commands.has_role('Owner')
    @commands.command(name="restartscan")
    async def start(self, ctx):
        self.scan.restart()

    @commands.command(name="test")
    async def test(self, ctx):
        itemIDs = {}
        prompt = await ctx.send("Paste auxi/itemID info here: (each item ID must be on new line)")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        inp = await self.client.wait_for('message', check=check)

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
                    if i.isnumeric():
                        itemIDs[i] = None

        url = 'https://hordes.io/api/item/get'
        data = {"ids":list(itemIDs.keys())}
        cookies = {"sid":''}
        r = requests.post(url, data=json.dumps(data),cookies=cookies)
        itemsRaw = json.loads(r.text)
        items = []
        msg = ""
        for itemRaw in itemsRaw:
            if itemIDs[str(itemRaw["id"])] != None:
                itemRaw["upgrade"] = itemIDs[str(itemRaw["id"])]
            item = self.Decoder.decode(itemRaw, False)
            """
            try:
                item = self.Decoder.decode(itemRaw, maxtier)
            except:
                return await ctx.send("Failed to decode item data. Type >help if you are confused")"""
            items.append((item,overallScore,itemClass))

            await ctx.send(f"""```{item}```""")
            """
            found = False
            if len(item["bonus_attr_keys"]) == 4:
                await ctx.send(f"{item['ID']} : True")

                found = True
            else:
                if item["type"] == "orb":
                    for combo in self.orb_desireable:
                        if Counter(combo) == Counter(item['bonus_attr_keys']):
                            await ctx.send(f"{item['ID']} : True")

                            found = True
                else:
                    if item["type"] in self.type_table.keys():
                        toCheck = self.type_table[item["type"]]
                    else:
                        toCheck = self.gen_desireable

                    for combo in toCheck:      
                        if Counter(combo) == Counter(item['bonus_attr_keys']):
                            msg += f"{item['ID']} : True\n"

                            found = True
                            break

                        if item["type"] in ["staff","sword","hammer","bow"]:
                            try:
                                item["bonus_attr_keys"].remove(self.blood_table[item["type"]])
                            except ValueError:
                                break
                            for roll in item["bonus_attr_keys"]:
                                if roll in combo:
                                    msg += f"{item['ID']} : True\n"

                                    found = True
                                    break 

            if not found:
                msg += f"{item['ID']} : False\n"
            """
                        
        if items == []:
            return await ctx.send("Unknown items")


    @tasks.loop(seconds=900)
    async def updateStartID(self):
        service = build("sheets", "v4", credentials=self.creds)
        sheet = service.spreadsheets()

        request = sheet.values().update(
        spreadsheetId="1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s",
        range=f"data!Z32",
        valueInputOption="USER_ENTERED",
        body={
            "values":[[str(self.start_id)]],
            "majorDimension":"ROWS"
            }
        ).execute()

    @tasks.loop(seconds=120)
    async def scan(self):
        dropchannelAll = self.client.get_channel(874710769424556102)
        dropchannelGood = self.client.get_channel(875387207647645707)
        dropchannelMage = self.client.get_channel(881283495920533524)
        dropchannelArcher = self.client.get_channel(881283603361853461)
        dropchannelShaman = self.client.get_channel(881283636685586452)
        dropchannelWarrior = self.client.get_channel(881283683942817845)
        dropchannelLegendary = self.client.get_channel(881283783700127745)
        dropchannelMisc = self.client.get_channel(881300971773378620)

        dropchannelMageCB = self.client.get_channel(976501578146144356)
        dropchannelArcherCB = self.client.get_channel(976501557602431006)
        dropchannelShamanCB = self.client.get_channel(976501605551734834)
        dropchannelWarriorCB = self.client.get_channel(976501643963170826)

        url = 'https://hordes.io/api/item/get'
        cookies = {"sid":''}

        def find_common(a,b):
            common = 0
            for i in a:
                if i in b:
                    common += 1
            return common

        #start_id = 122273989 # 151273594
        currstart_id = self.start_id
        rang = 150
        empty = 0
        itemsRaw = []
        count = 0
        itemsChecked = 0
        itemsFound = 0
        itemsToCheck = []
        items = []
        gooditems= []
        while (empty < 2) and count < 6:
            x = []
            for i in range(rang):
                x.append(currstart_id + i + 1)

            data = {"ids":x}    
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            itemsRaw = json.loads(r.text)

            count += 1
            currstart_id  += rang
            itemsChecked += rang
            itemsFound += len(itemsRaw)
            if len(itemsRaw) > 0:
                empty = 0
                for i in itemsRaw:
                    itemsToCheck.append(i)
            else:
                empty += 1        


        #await dropchannelA.send(f"API calls made: {count}\nIDs Checked: {itemsChecked}\nItems Found: {itemsFound}")
        if itemsFound > 0:
            self.start_id = itemsToCheck[-1]["id"]

            for itemRaw in itemsToCheck:
                item = self.Decoder.decode(itemRaw)

                if item["type"]:
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


                if "if" in item['bonus_attr_keys'] and "luc" in item['bonus_attr_keys'] and item["tier"] >= self.good_tiers[item["type"]]:
                    ifquality = item["attr"]["if"]["quality"]
                    luckquality = item["attr"]["luc"]["quality"]

                    if (ifquality + luckquality)/2 >= 70:
                        overallScore = getItemScore(item, itemClass, self.client.gears)
                        gooditems.append((item,overallScore,itemClass))
                        items.append((item,overallScore,itemClass))
                        continue

                if (len(item['bonus_attr_keys']) >= 3 and item["tier"] >= self.minimum_tiers[item["type"]]) or len(item['bonus_attr_keys']) == 4:
                    overallScore = getItemScore(item, itemClass, self.client.gears)

                    items.append((item,overallScore,itemClass))

                    if len(item["bonus_attr_keys"]) == 4:
                         gooditems.append((item,overallScore,itemClass))

                    else:
                        if item["tier"] >= self.good_tiers[item["type"]]:
                            if item["type"] in ["staff","sword","hammer","bow"] and item["quality"] >= 90 and item["tier"] > self.minimum_tiers[item["type"]]:
                                check1 = self.blood_table[item["type"]] in item["bonus_attr_keys"]
                                check2 = False
                                for s in self.gen2_desireable:
                                    if find_common(item["bonus_attr_keys"], s) == 2:
                                        check2 = True
                                        break

                                if check1 or check2:
                                    gooditems.append((item,overallScore,itemClass))
                                    continue
                            

                            if item["type"] == "orb":
                                for combo in self.orb_desireable:
                                    if Counter(combo) == Counter(item['bonus_attr_keys']):
                                         gooditems.append((item,overallScore,itemClass))
                            else:
                                if self.type_table[item["type"]] != "misc":
                                    toCheck = self.type_table[item["type"]]
                                else:
                                    toCheck = self.gen_desireable
                                for combo in toCheck:      
                                    if Counter(combo) == Counter(item['bonus_attr_keys']):
                                        gooditems.append((item,overallScore,itemClass))
                                        break
                                    
                                    found = False

                                    if item["type"] in ["staff","sword","hammer","bow"] and self.blood_table[item["type"]] in item["bonus_attr_keys"]:
                                        for roll in [y for y in item["bonus_attr_keys"] if y!=self.blood_table[item["type"]]]:
                                            if roll in combo:
                                                gooditems.append((item,overallScore,itemClass))
                                                found = True
                                                break 

                                        if found:
                                            break
                
                """
                for user in self.client.WL:
                    for wish in self.client.WL[user]:
                        check = False
                        if item["type"] == wish["type"]:
                            if item["tier"]+1 == wish["tier"] and item["quality"] >= wish["quality"] and item["bound"] == 0:
                                if find_common(item["bonus_attr_keys"], list(wish["stats"].keys())) == len(list(wish["stats"].keys())):
                                    for s in list(wish["stats"].keys()):
                                        if not item["attr"][s]["quality"] >= wish["stats"][s]:
                                            check = True

                                    if not check:
                                        scoutServer = self.client.get_guild(872255568922947644)
                                        member = scoutServer.get_member(user)
                                        channel = await member.create_dm()
                                        
                                        with BytesIO() as image_binary:
                                            generateItemCard([(item,overallScore,itemClass)], []).save(image_binary, "PNG")
                                            image_binary.seek(0)
                                            f = discord.File(fp=image_binary, filename="output.png")

                                        await channel.send("An item from your wishlist has dropped")
                                        try:
                                            await channel.send(file=f)
                                        except:
                                            try:
                                                await asyncio.sleep(30)
                                                await channel.send(file=f)
                                            except:
                                                pass
                                        break
                
            
            if len(items) > 0:
                with BytesIO() as image_binary:
                    generateItemCard(items, []).save(image_binary, "PNG")
                    image_binary.seek(0)
                    f = discord.File(fp=image_binary, filename="output.png")

                try:
                    await dropchannelAll.send(file=f)
                except:
                    try:
                        await asyncio.sleep(30)
                        await dropchannelAll.send(file=f)
                    except:
                        pass"""


            if len(gooditems) > 0:
                for item in gooditems:
                    """
                    dropchannel = []

                    if item[0]["quality"] >= 99 and item[0]["bound"] == 0:
                        dropchannel.append(dropchannelLegendary)

                    if self.type_table[item[0]["type"]] == self.mage_desireable or ("int" in item[0]["bonus_attr_keys"] and self.type_table[item[0]["type"]] == "misc"):
                        if item[0]["bound"] == 0:
                            dropchannel.append(dropchannelMage)
                        else:
                            dropchannel.append(dropchannelMageCB)

                    if self.type_table[item[0]["type"]] == self.archer_desireable or ("dex" in item[0]["bonus_attr_keys"] and self.type_table[item[0]["type"]] == "misc"):
                        if item[0]["bound"] == 0:
                            dropchannel.append(dropchannelArcher)
                        else:
                            dropchannel.append(dropchannelArcherCB)

                    if self.type_table[item[0]["type"]] == self.shaman_desireable or ("wis" in item[0]["bonus_attr_keys"] and self.type_table[item[0]["type"]] == "misc"):
                        if item[0]["bound"] == 0:
                            dropchannel.append(dropchannelShaman)
                        else:
                            dropchannel.append(dropchannelShamanCB)

                    if self.type_table[item[0]["type"]] == self.warrior_desireable or ("str" in item[0]["bonus_attr_keys"] and self.type_table[item[0]["type"]] == "misc"):
                        if item[0]["bound"] == 0:
                            dropchannel.append(dropchannelWarrior)
                        else:
                            dropchannel.append(dropchannelWarriorCB)

                    if dropchannel == []:
                        dropchannel.append(dropchannelMisc)

                    
                    for ch in dropchannel:
                        with BytesIO() as image_binary:
                            generateItemCard([item], []).save(image_binary, "PNG")
                            image_binary.seek(0)
                            f = discord.File(fp=image_binary, filename="output.png")
                        
                        try:
                            await ch.send(file=f)
                        except:
                            try:
                                await asyncio.sleep(30)
                                await ch.send(file=f)
                            except:
                                pass
                    """

                    x = {
                        "_id" : item[0]["ID"]
                    }

                    y = {
                        "type" : item[0]['type'],
                        "tier" : item[0]['tier'],
                        "quality" : item[0]["quality"],
                        "gearscore" : item[0]["gearscore"],
                        "bound" : item[0]["bound"],
                        "name" : item[0]["name"],
                        "base_stats" : {},
                        "bonus_stats" : {},
                        "bonus_stats_keys" : item[0]["bonus_attr_keys"]
                    }

                    for st in item[0]["attr"]:
                        if item[0]["attr"][st]["bonus"]:
                            y["bonus_stats"][st] = {
                                "value" : item[0]["attr"][st]["value"],
                                "quality" : item[0]["attr"][st]["quality"]
                            }
                        else:
                            y["base_stats"][st] = {
                                "value" : item[0]["attr"][st]["value"],
                                "quality" : item[0]["attr"][st]["quality"]
                            }

                    self.collection.update_one(x, {"$set" : y}, upsert=True)


