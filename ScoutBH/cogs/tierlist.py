from func.buffs import cranialBuff
import discord
import requests
import json
import asyncio
from discord.ext import commands
from googleapiclient.discovery import build
from google.oauth2 import service_account


def setup(client):
    client.add_cog(Tierlist(client))
    

class Tierlist(commands.Cog):
    
    def __init__(self, client):
        self.client = client

        self.SERVICE_ACCOUNT_FILE = "static/gapi/keys.json"
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.sheetIDs = {
            "mage" : "1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s", 
            "archer" : "1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0",
            "shaman" : "1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw",
            "warrior" : "150QNvGaKPkOQ6pKD1z2SPWfXjjYS0p7RrH8LMRWFIC8"
        }

        service = build("sheets", "v4", credentials=self.creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=self.sheetIDs["mage"],
            range=f"data!AB2:AB200",
            majorDimension="COLUMNS"
            ).execute()

        self.trusted = result.get("values", [])[0]

    async def tierlistlog(self, mode, author, name, list=None):
        channel = self.client.get_channel(976503812250566736)
        colours = {
            "mage" : 0x42c6ff,
            "archer" : 0x31c31d,
            "shaman" : 0x1d2ae2,
            "warrior" : 0x9d5353
        }

        if mode == "tlremoved":
            embed=discord.Embed(title="REMOVED", description=name, color=colours[list])
        elif mode == "modded":
            embed=discord.Embed(title="MODDED", description=name, color=0xfccf03)
        elif mode == "unmodded":
            embed=discord.Embed(title="UNMODDED", description=name, color=0xfccf03)

        embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=author.avatar_url)

        await channel.send(embed=embed)

    @commands.command(name="tierlist")
    async def tierlist(self, ctx, mode, list, *args):
        if ctx.author.id not in self.client.VIP or self.client.scoutGuild.get_member(ctx.author.id) is None:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            if ctx.guild.id != 872255568922947644:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")

        name = " ".join(args)
        if mode == "remove":
            if str(ctx.author.id) in self.trusted:
                try:
                    SPREADSHEET_ID = self.sheetIDs[list.lower()]
                except:
                    return await ctx.send("Tierlist funcitonality not avaiable yet for this class")

                service = build("sheets", "v4", credentials=self.creds)
                sheet = service.spreadsheets()

                #DATA SHEET
                if list.lower() == "warrior":
                    result = sheet.values().get(
                        spreadsheetId=SPREADSHEET_ID,
                        range="data!R2"
                        ).execute()
                else:
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
                elif list.lower() == "warrior":
                    endletter = "H"
                    colummnLen = 8

                result = sheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"data!A2:{endletter}{end}",
                    majorDimension="COLUMNS"
                    ).execute()

                resp = result.get("values", [])
                names = [e.lower() for e in resp[0]]

                if name.lower() in names:
                    loc = names.index(name.lower())
                    for i in range(colummnLen):
                        resp[i].pop(loc)
                        resp[i].append("")
                else:
                    return await ctx.send("Player not found")

                request = sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"data!A2",
                    valueInputOption="USER_ENTERED",
                    body={
                        "values":resp,
                        "majorDimension":"COLUMNS"
                        }
                    ).execute()

                if list.lower() == "warrior":
                    result = sheet.values().get(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"data!O2:P{end}",
                        majorDimension="COLUMNS"
                        ).execute()

                    resp = result.get("values", [])

                    loc = names.index(name)
                    for i in range(2):
                        resp[i].pop(loc)
                        resp[i].append("")


                    request = sheet.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"data!O2",
                        valueInputOption="USER_ENTERED",
                        body={
                            "values":resp,
                            "majorDimension":"COLUMNS"
                            }
                        ).execute()

                await self.tierlistlog("tlremoved", ctx.author, name, list)
                return await ctx.send(f"Removed {name} from {list} tierlist")
            else:
                return await ctx.send("Permission denied")
                
        
    
    @commands.command(name="tierlists")
    async def tierlists(self, ctx):
        if ctx.author.id not in self.client.VIP or self.client.scoutGuild.get_member(ctx.author.id) is None:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            if ctx.guild.id != 872255568922947644:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")

        mage=discord.Embed(title="Mage", url="https://docs.google.com/spreadsheets/d/1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s", description="Scout tierlist | Hordes.io", color=0x42c6ff)
        mage.set_thumbnail(url="https://hordes.io/assets/ui/classes/1.png?v=4648500")
        archer=discord.Embed(title="Archer", url="https://docs.google.com/spreadsheets/d/1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0", description="Scout tierlist | Hordes.io", color=0x31c31d)
        archer.set_thumbnail(url="https://hordes.io/assets/ui/classes/2.png?v=4648500")
        shaman=discord.Embed(title="Shaman", url="https://docs.google.com/spreadsheets/d/1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw", description="Scout tierlist | Hordes.io", color=0x1d2ae2)
        shaman.set_thumbnail(url="https://hordes.io/assets/ui/classes/3.png?v=4648500")
        warrior=discord.Embed(title="Warrior", url="https://docs.google.com/spreadsheets/d/150QNvGaKPkOQ6pKD1z2SPWfXjjYS0p7RrH8LMRWFIC8", description="Scout tierlist | Hordes.io", color=0x9d5353)
        warrior.set_thumbnail(url="https://hordes.io/assets/ui/classes/0.png?v=4648500")
        await ctx.send(embed=mage)
        await ctx.send(embed=archer)
        await ctx.send(embed=shaman)
        await ctx.send(embed=warrior)

    @commands.command(name="moderator")
    async def moderator(self, ctx, mode, user: discord.User = None):
        if ctx.author.id not in self.client.VIP or self.client.scoutGuild.get_member(ctx.author.id) is None:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            if ctx.guild.id != 872255568922947644:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        SPREADSHEET_ID = self.sheetIDs["mage"]

        service = build("sheets", "v4", credentials=self.creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"data!AA2:AB200",
            majorDimension="COLUMNS"
            ).execute()

        currentMods = result.get("values", [])

        if mode == "view":
            msg = ""
            for y in range(len(currentMods[0])):
                msg += f"{currentMods[0][y]} : {currentMods[1][y]}\n"
            return await ctx.send(f"Scout tierlist Moderators:\n{msg}")

        elif mode == "add":
            if ctx.author.id == 225697391926444033: #Desk
                newMods = currentMods
                newMods[0].append(f"{user.name}#{user.discriminator}")
                newMods[1].append(f"{user.id}")

                for spsheet in self.sheetIDs:
                    request = sheet.values().update(
                        spreadsheetId=self.sheetIDs[spsheet],
                        range=f"data!AA2",
                        valueInputOption="USER_ENTERED",
                        body={
                            "values":newMods,
                            "majorDimension":"COLUMNS"
                        }
                    ).execute()

                await self.tierlistlog("modded", ctx.author, f"{user.name}#{user.discriminator}")
                await ctx.send(f"Modded {user.name}#{user.discriminator}")
            else:
                return await ctx.send("Permission denied")

        elif mode == "remove":
            if ctx.author.id == 225697391926444033: #Desk
                deletionIndex = currentMods[0].index(f"{user.name}#{user.discriminator}")
                newMods = currentMods
                for i in range(2):
                    newMods[i].pop(deletionIndex)
                    newMods[i].append("")

                for spsheet in self.sheetIDs:
                    request = sheet.values().update(
                        spreadsheetId=self.sheetIDs[spsheet],
                        range=f"data!AA2",
                        valueInputOption="USER_ENTERED",
                        body={
                            "values":newMods,
                            "majorDimension":"COLUMNS"
                        }
                    ).execute()

                await self.tierlistlog("unmodded", ctx.author, f"{user.name}#{user.discriminator}")
                await ctx.send(f"Unmodded {user.name}#{user.discriminator}")
            else:
                return await ctx.send("Permission denied")

        self.client.reload_extension("cogs.playerstats")
        self.client.reload_extension("cogs.tierlist")

