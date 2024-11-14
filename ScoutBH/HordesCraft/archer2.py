from HordesCraft.classes import archer
from HordesCraft.targets import dummy
from math import ceil
from random import uniform
from itertools import cycle


def run(skills, stats, config):
    """
    def addRevit(time, target):
        targets[target] = min(targets[target] + 1, 3)
        player.cds["player"] = time + gcd
        if time > 30000: casts["revitalize"] += 1

        log.append(f"cast revit on {target}")
        tickStart = time+(hasteAffected(1)) # delay = 1s
        revitEnd = time+(12*1000) # duration = 12s
        events["revitEnd"][target] = serverTick(revitEnd)
        if targets[target] == 1: addRevitTick(target, tickStart, revitEnd)

    def addRevitTick(target, tickStart, revitEnd):
        if tickStart > revitEnd: 
            log.append(f"rev dropped -> {target}")
            player.revStacks = 0
            player.revdropped += 1
            return
        events["revitTick"][target] = serverTick(tickStart)

    def canine(time):
        if player.cds["player"] > time: return
        ability = player.canine()
        player.cds["canine"] = time + hasteAffected(ability["cooldown"])
        player.cds["player"] = time + gcd
        casts["canine"] += 1
        player.nextcanine = time+(14000*3)
        #player.stats["haste"] += ability["hasteBuff"]

        #log.append(f"gained canine +{ability['hasteBuff']} haste")
        log.append("used canine")
        canineEnd = serverTick(time+ability["duration"]*1000)
        events["canineEnd"] = [canineEnd, ability["hasteBuff"]]

    def decay(time):
        if player.cds["player"] > time: return
        ability = player.decay()
        player.cds["decay"] = time + hasteAffected(ability["cooldown"])
        player.cds["player"] = time + gcd
        casts["decay"] += 1
        log.append("cast decay")

        if player.skills["plaguespreader"] == 0: return
        buff = player.plagueBuff()
        plagueEnd = serverTick(time+buff["duration"]*1000)
        events["plagueEnd"] = [plagueEnd, buff["hasteBuff"]]

        if player.plagueStacks == 5: return
        player.plagueStacks += 1
        player.stats["haste"] += buff["hasteBuff"]
        log.append(f"+{buff['hasteBuff']} haste, {player.plagueStacks} plague stacks ")

    def totem(time):
        if player.cds["player"] > time: return
        player.cds["totem"] = time + hasteAffected(60)
        player.cds["player"] = time + gcd
        casts["totem"] += 1
        player.casting = True
        player.lastTotem = serverTick(time)

        if events["totemTick"] == [-1, -1]:
            events["totemTick"] = [serverTick(time+hasteAffected(2.3)), -1]
            events["totemEnd"] = serverTick(time+30*1000)
        else:
            events["totem2Tick"] = [serverTick(time+hasteAffected(2.3)), -1]
            events["totem2End"] = serverTick(time+30*1000)
        log.append("casting healing totem")

    def mend(time, target):
        if player.cds["player"] > time: return
        player.cds["player"] = time + gcd
        casts["mend"] += 1
        player.casting = True

        events["mendTick"] = [serverTick(time+hasteAffected(1.7)), target]
        log.append("casting mend")
    
    """


    def skull(time):
        player.cds["skull"] = time + 60*1000
        casts["skull"] += 1
        player.dmgMultiplier += 0.2
        events["skullEnd"] = serverTick(time + 10*1000)
        log.append("gained skull")


    def hasteAffected(time):
        return (time/(1+(player.stats["haste"]/100))) * 1000

    def serverTick(time):
        return serverTickrate * ceil((time)/serverTickrate)

    def dmg(d, ability, msg):
        player.dmg[ability] += d
        if dmgLogs: log.append(f"{msg} {d}")

    def dmg(d, ability):
        critRoll = uniform(1, 101)
        critChance = player.crit

        msg = ""

        if critRoll <= critChance:
            d *= 2
            msg += "CRIT "

        d = round(d * target.mitigation * player.dmgMultiplier)
        msg += f"{ability} {d}"

        if dmgLogs: log.append(msg)
        player.dmg[ability] += d

    def output(time):
        nonlocal runlog
        if log != []:
            log.insert(0, f"{time}ms")
            runlog += f'{" | ".join(log)}\n'

    """
    skills = {
        "revitalize" : 5,
        "mend" : 5,
        "decay" : 1,
        "canine howl" : 5,
        "plaguespreader" : 5,
        "healing totem" : 4
    }


    stats = { # max buffs
        "min" : 261,
        "max" : 323,
        "crit" : 54.3,
        "haste" : 89.3
    }

    config = {
        "duration" : 149,
        "tickrate" : 40,
        "healLogs" : False
    }
    """
    simDuration = config["duration"]*1000
    serverTickrate = config["tickrate"]
    dmgLogs = config["dmgLogs"]
    runlog = ""

    player = archer(stats, skills)
    target = dummy()

    casts = {
        "swift shot" : 0,
        "precise shot" : 0,
        "invigorate" : 0,
        "dash" : 0,
        "bone shot" : 0,
        "skull" : 0,
        "auto attack" : 0
    }
    events = {
        "poisonTick" : [-1, -1], # dmg, interval
        "poisonEnd" : -1,
        "invigEnd" : [-1, -1],
        "skullEnd" : -1
    }

    for time in range(0, simDuration+30*1000, serverTickrate):
        log = []

        # EVENTS
        if events["invigEnd"][0] == time:
            player.dmgMultiplier  -= events["invigEnd"][1]
            log.append(f"lost invig -{events['invigEnd'][1]} dmg multiplier")

        if events["poisonEnd"][0] == time:
            target["poisonDot"] = 0
            log.append(f"lost poison stacks")

        if events["skullEnd"] == time:
            player.dmgMultiplier -= 0.2
            log.append("lost skull")

        
        


        # ABILITY USE
        if not player.casting:
            gcd = max(hasteAffected(1.5), 800)

            if time < 30*1000: # pre boss

                if player.cds["canine"] <= time and player.nextcanine <= time:
                    canine(time)
                    player.nextcanine = time+(14000*3)

                if player.cds["revitalize"] <= time and player.cds["player"] <= time:
                    addRevit(time, next(targetCycle))

            else: # boss start
                
                if time < 40*1000 and 1==0: # inital boss phase

                    if events["plagueEnd"][0]-1000 <= time:
                        decay(time)
                    
                    if player.cds["player"] <= time:
                        addRevit(time, next(targetCycle))

                else:

                    if player.cds["skull"] <= time and player.cds["totem"]-8000 <= time:
                        skull(time)

                    if events["plagueEnd"][0]-1000 <= time:
                        decay(time)

                    if player.cds["totem"] <= time:
                        totem(time)

                    if player.cds["canine"] <= time and player.nextcanine <= time:
                        canine(time)
                        
                    if player.cds["player"] <= time:
                        addRevit(time, next(targetCycle))
                
            """
            if player.cds["skull"] <= time and 1==0:
                skull(time)

            if player.cds["mend"] <= time and 1==0:
                mend(time, 0)

            if player.cds["totem"] <= time and 1==0:
                totem(time)

            if player.cds["decay"] <= time and 1==0:
                decay(time)
            
            if player.cds["canine"] <= time and 1==0:
                canine(time)
                nextCanine = time+(15*1000*3)
            """
            
                
            

        output(time)
    """
    print("------------------------------")
    print(f"hps : {sum(player.healing.values())/(simDuration/1000)} \ntotem ticks : {totaltotemticks}\nrev ticks : {totalrevticks}\nrev dropped : {player.revdropped}\nplague dropped : {player.plaguedropped}")
    print("casts:")
    for a in casts:
        print(f"  {a} : {casts[a]}")
    print("healing:")
    for a in player.healing:
        print(f"  {a} : {player.healing[a]}")
    print(f"  total : {sum(player.healing.values())}"""
    return {
        "healing" : player.healing,
        "ticks" : {
            "revitalize" : totalrevticks,
            "totem" : totaltotemticks
        },
        "dropped" : {
            "revitalize" : player.revdropped,
            "plague" : player.plaguedropped
        },
        "casts" : casts,
        "log" : runlog
    }

