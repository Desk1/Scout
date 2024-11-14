import discord
from discord.ext import commands


def setup(client):
    client.add_cog(Help(client))

class Help(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(name="help")
    async def help(self, ctx, *args):
        if self.client.scoutGuild.get_member(ctx.author.id) is None:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.id not in self.client.VIP:
                return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
        elif ctx.guild.id != 872255568922947644:
            return await ctx.send("Scout is now only available for use in the official server:\nhttps://discord.gg/tXddmeHtzD")
            
        if len(args) == 0:
            await ctx.send("""```
Available commands:
    prestige
    playerstats
    viewgear
    builditem
    tierlists
    wishlist
    gloomfury
    tierlist (moderator)
    findgear (VIP)
    storage (VIP)

For more information about a command, type >help [command]```""")
        else:
            if args[0] == "prestige":
                await ctx.send("""```
Description:
    Calculates fame/bracket needed for player to maintain or ascend their rank each week. Values change every Wednesday.

Usage:
    >prestige [player name]```""")
            elif args[0] == "viewgear":
                await ctx.send("""```
Description:
    Generates neatly formatted item collage

Usage:
    >viewgear [optional title]
    Once prompted, enter item IDs on seperate lines OR paste info from auxi.
    Enter '+[number]' after item ID to indicate item upgrade level (optional).
    
    E.G '100621449 +6
    
    Sending >viewgear [playername] followed by 'tierlist' will automatically show the gear of the respective player which was used in the tierlists
    E.g >viewgear broku tierlist

    Add "raw" to have the output be in text format, where ids can be copied
    ```""")
            elif args[0] == "playerstats":
                if len(args) > 1:
                    if args[1] == "modifiers":
                        await ctx.send("""```
Change allocated stats:
    fullstr, fullstam, fulldex, fullint, fullwis, fullluck

Add buffs:
    must add number 1-9 after buff name with no space to indicate level, e.g enchant4
    enchant, arctic, hypo, armor, warcry, crusader, bulwark, temporal, cranial, invigorate, howl, plague, skull
    'maxbuff' will add: enchant4 arctic4 warcry4 crusader4 temporal4

Misc:
    maxprestige, noprestige, maxupgrade, maxtier, customspec, maxbuff

Tierlist (automatically show the gear of the respective player which was used in the tierlists):
    tierlist```""")
                    else:
                        await ctx.send(f"No info found for argument '{args[1]}'")
                else:
                    await ctx.send("""```
Description:
    Generates a player's stat sheet with calculated Effective HP and DPS included

Usage:
    >playerstats [player name] [modifiers]
    You can add as many modifiers as you like. Class locked buffs such as invigorate will be locked to their appropriate class.
    Once prompted, paste info from auxi. This can be obtained by going to the main hordes.io discord and typing !playergear [name].
    *If adding 'tierlist' modifier, no info needs to be copy/pasted

Example Usage:
    >playerstats desk arctic4 enchant4 hypo5 warcry4 fullstam crusader4 armor4 temporal4 cranial4 maxprestige
    >playerstats desk noprestige maxupgrade maxtier
    >playerstats desk tierlist maxprestige
    >playerstats desk

For a list of all available modifiers, type >help playerstats modifiers```""")
            elif args[0] == "builditem":
                await ctx.send("""```
Description:
    Generates a simulated item

Usage:
    >builditem (tier) (type) (quality) (upgrade [optional])
    E.G >builditem T6 glove 98% +3


    Add "store" to the end of the command to use generated items in >playerstats/>viewgear (VIP)
    E.G >builditem T6 glove 98% +3 store
    See >help storage for more info

    Once prompted, enter bonus stat info.
    Use '=' to indicate stat value desired
    Use ':' to indicate stat roll desired

    E.G
    str : 99%
    block = 4.5
    max : 69%```""")
            elif args[0] == "tierlists":
                await ctx.send("""```
Description:
    Sends links to tierlists for each class

Usage:
    >tierlists```""")

            elif args[0] == "tierlist":
                await ctx.send("""```
Available tierlist commands:
    remove (moderator)

Usage:
    >tierlist remove [class] [player name]

Example:
    >tierlist remove mage Desk```""")

            elif args[0] == "storage":
                await ctx.send(
"""```
Description:
    Used to display/delete stored generated items
    add "clear" to delete all stored items
    add "remove" followed by the item ids to delete specific items
    add "addset" to add an item set. Enter the desired ID for the set afterwards, otherwise one is generated.
    item sets can be used in playerstats/viewgear commands

    There is a limit of 150 items/item sets max storage per user

Usage:
    >storage
    >storage clear
    >storage remove -DESK1 -DESK6 -DESK34
    >storage addset MageWar
```""")

            elif args[0] == "findgear":
                await ctx.send(
"""```
Description:
    Used to search scout's database of items

    You can search by any of the following parameters in any order:
    item type, tier, stats, quality, bound

    '<', '=', '>' can be used before quality. default option is '>'
    Tier can be stated as "t5" or "t5+", the + means tiers greater than or equal to the tier specified are returned
    Adding :[number] after a stat will indicate the minimum quality the stat must have
    'bound/unbound' can be added to filter gloom drops

    Add "raw" to have the output be in text format, where ids can be copied

Usage:
    >findgear sword t8 str stam:90 haste
    >findgear t7+ sword <85%
    >findgear t5 armor int:84 stam 90%
    >findgear bag 99%
    >findgear staff unbound 100%
```""")

            elif args[0] == "wishlist":
                await ctx.send(
"""```
Description:
    Find players who have wished for an item which you enter

    (VIP) 
    Ability to create a wishlist
    You are notified when an item on your wishlist drops ingame.
    Max 10 wishlist entries per user

Usage:
    >wishlist 151989958

    (VIP):
    >wishlist add sword t8 str:90 stam haste 90%
    >wishlist view
    >wishlist clear
    >wishlist remove 1
```""")     
            elif args[0] == "gloomfury":
                await ctx.send(
"""```
Description:
    Simulate a gloomfury boss battle under perfect conditions
    Uses the gear you specify and runs exactly as the real game does, with all RNG included
    (max buffs, no deaths, perfect skill rotation)
    
    Currently only available for shaman

    (VIP) 
    VIP users can modify the simulation settings, including:
    - Number of simulations by adding a number
    - Duration of simulation in seconds by adding a number with 's' at the end
    - Prestige buffs by adding 'maxprestige' or 'noprestige'
    - Upgrade level of items
    - Add 'log' to get a clickable link showing a rundown of the exact skill rotation used in the fight

Usage:
    >gloomfury sofa

    (VIP):
    >gloomfury sofa 300s
    >gloomfury sofa maxprestige 100 log
    >gloomfury sofa maxprestige 50 300s (50 simulations, 5 minute long battle)
    >gloomfury sofa log maxprestige

```""")

            else:
                await ctx.send("Unknown command")
