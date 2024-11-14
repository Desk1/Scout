import discord
import requests
import json
import asyncio
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from math import floor, ceil
from time import time
from func.playerCard import evalstats, initreal
from func.buffs import *
from func.itemCard import *
from func import decoder
from HordesCraft.mage import *
from HordesCraft.archer import *
from discord.ext import commands
from googleapiclient.discovery import build, createNextMethod
from google.oauth2 import service_account


def setup(client):
    client.add_cog(Simulation(client))

class Simulation(commands.Cog):
    
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

        self.APLs = {
            1 : ["skull IFtarget:iceboltCharge","hypo IFtarget:iceboltCharge","chilling IFtarget:iceboltCharge","bolt"],
            2 : ["skull","invigorate","dash IFcooldown:precise","precise","swift"]
        }

        self.skills = {
            1 : {
                "icebolt" : 5,
                "iceorb" : 0,
                "hypothermic frenzy" : 5,
                "chilling radiance" : 5,
                "enchantment" : 4,
                "arctic aura" : 4
            },
            2 : {
                "swift shot" : 5,
                "precise shot" : 5,
                "poison arrows" : 5,
                "invigorate" : 5,
                "dash" : 1,
                "temporal dilation" : 3,
                "cranial punctures" : 0
            }
        }

    @commands.command(name="dpstest")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.has_role('Owner')
    async def dpstest(self, ctx, *args):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        """for arg in args:
            if arg[:arg.index("=")] == "time":
                fightTime = int(arg[arg.index("=")+1:])
            elif arg[:arg.index("=")] == "target":
                target = arg[arg.index("=")+1:]
            elif arg[:arg.index("=")] == "simulations":
                simulations = int(arg[arg.index("=")+1:])
            elif arg[:arg.index("=")] == "players":
                playerCount = int(arg[arg.index("=")+1:])
        interval = 50
        if simulations > 1000 or simulations < 1:
            return await ctx.send("Number of simulations must be between 1-1000")
        if fightTime > 1000 or fightTime < 1:
            return await ctx.send("Fight time must be between 1-1000 seconds")
        if playerCount > 10 or playerCount < 1:
            return await ctx.send("Number of players must be between 1-10")
        try:
            await ctx.send(f"time:{fightTime} seconds, target:{target}, simulations:{simulations}, players:{playerCount}")
        except UnboundLocalError:
            return await ctx.send("Invalid arguemnts. Please include: time=[seconds], simulations=[number of simulations], target=[target name], players=[number of players]")"""

        interval = 50
        simulations = 250
        fightTime = 120

        stats = {}
        names = {}
        namesInput = list(args)
        for p in args:
            if p[0] == "(":
                del namesInput[args.index(p)]
                continue
            r = requests.post('https://hordes.io/api/playerinfo/search', data=json.dumps({"name" : p, "order" : "gs", "limit" : 25, "offset" : 0}))
            players = json.loads(r.text)
            found = False
            for player in players:
                if p.lower() == player["name"].lower():
                    playerinfo = player
                    names[playerinfo["name"]] = playerinfo["pclass"]
                    found = True
            if not found:
                return await ctx.send("Unknown player")

            SPREADSHEET_ID = self.sheetIDs[playerinfo["pclass"]]

            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()

            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"data!A2:G1000",
                majorDimension="COLUMNS"
                ).execute()

            resp = result.get("values", [])

            try:
                if args[args.index(p)+1][0] == "(" and args[args.index(p)+1][-1] == ")":
                    NAME = " ".join([playerinfo["name"],args[args.index(p)+1]])
                else:
                    NAME = playerinfo["name"]
            except:
                NAME = playerinfo["name"]

            loc = resp[0].index(NAME)

            if playerinfo["pclass"] == 1:
                gearloc = 4
            elif playerinfo["pclass"] == 2:
                gearloc = 4
            elif playerinfo["pclass"] == 3:
                gearloc = 6

            itemIDs = {}
            gear = resp[gearloc][loc]
            gear = gear.split(",")
            for id in gear:
                itemIDs[id] = None
            

            buffNames = ["enchant","arctic","hypo","armor","warcry","crusader","bulwark","temporal","cranial","invigorate","howl"]
            buffs = [enchantBuff,arcticBuff,hypothermicBuff,armorBuff,warcryBuff,crusaderBuff,bulwarkBuff,temporalBuff,cranialBuff,invigorateBuff,howlBuff]
            ranks = [0,4000,8000,12000,16000,20000,24000,28000,32000,36000,40000,44000,48000]

            url = 'https://hordes.io/api/item/get'
            data = {"ids":list(itemIDs.keys())}
            cookies = {"sid":''}
            r = requests.post(url, data=json.dumps(data),cookies=cookies)
            items = json.loads(r.text)

            pclass = playerinfo["pclass"]
            level = playerinfo["level"]
            unallocated = playerinfo["level"]*3
            rank = 12

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
                "gs": playerinfo["gs"]
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
            allocatedStats[bloodline] += unallocated

            dmgMultiplier = 1
            if pclass == 1:
                buffEffect = buffs[buffNames.index("arctic")](4)
                for effect in buffEffect[0]:
                    realStats[effect] += buffEffect[0][effect]
                buffEffect = buffs[buffNames.index("enchant")](4)
                for effect in buffEffect[0]:
                    realStats[effect] += buffEffect[0][effect]
            elif pclass == 2:
                buffEffect = buffs[buffNames.index("temporal")](3)
                for effect in buffEffect[0]:
                    realStats[effect] += buffEffect[0][effect]

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

            decodedItems = []
            for item in items:
                try:
                    item = self.Decoder.decode(item)
                except:
                    return await ctx.send("Failed to decode item data")
                decodedItems.append(item)
                for stat in item["attr"]:
                    if stat in allocatedStats:
                        allocatedStats[stat] += item["attr"][stat]["value"]
                    else:
                        realStats[stat] += item["attr"][stat]["value"]


            realStats = initreal(allocatedStats, realStats, bloodline, dmgMultiplier)
            stats[playerinfo["name"]] = {
                "min" : realStats["min"],
                "max" : realStats["max"],
                "crit" : realStats["cri"],
                "haste" : realStats["has"],
                "atkspeed" : realStats["att"]
            }



        results = {}

        data = {
            "Time" : [],
            "Damage" : [],
            "Sim" : [],
        }

        for p in names:
            pclass = names[p]
            results[p] = []
            if pclass == 1:
                skills = self.skills[pclass]
                APL = self.APLs[pclass]
                await ctx.send(f"{p}  :  {stats[p]}  :  mage sim")
                for i in range(simulations):
                    mageSim(fightTime, stats[p], skills, APL, results[p], interval, data, p)
                        
            elif pclass == 2:
                skills = self.skills[pclass]
                APL = self.APLs[pclass]
                await ctx.send(f"{p}  :  {stats[p]}  :  archer sim")
                for i in range(simulations):
                    archerSim(fightTime, stats[p], skills, APL, results[p], interval, data, p)

        """
        avgDPS = sum(results[0])/len(results[0])
        minDPS = min(results[0])
        maxDPS = max(results[0])
        endTime = time()

        await ctx.send(f
Avg. DPS: {avgDPS}
Max DPS: {maxDPS}
Min DPS: {minDPS}
"""
        await ctx.send(f"""
Fight Length: {fightTime} seconds
Simulations ran: {simulations}
Simulation interval: {interval} ms
        """)           

        df = pd.DataFrame(data)

        palette = sns.color_palette("mako_r", len(namesInput))
        sns.set_theme()
        custom_style = {
            'axes.labelcolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white'
        }
        sns.set_style("dark")
        sns.lineplot(data=df, x=df["Time"], y=df["Damage"], palette=palette, hue=df["Sim"], ci="sd").set(title=f' DPS | Training dummy Lv.40 (faivel)')
        plt.savefig("static/misc/simulation.png", dpi = 500)
        plt.clf()
        with open("static/misc/simulation.png", "rb") as fh:
            f = discord.File(fh, filename="output.png")
        try:
            await ctx.send(file=f)
        except:
            await asyncio.sleep(1)
            await ctx.send(file=f)


