from os import name
from HordesCraft.classes import *
from HordesCraft.targets import *
from random import uniform
from time import sleep, time
from math import exp, floor


def output(time, msg):
    pass
    #print(f"{time}ms : {' | '.join(msg)}")


def mageSim(fightTime, stats, skills, APL, out, interval, dataout, ID):
    dmgTotal = 0
    player = mage(stats, skills)
    target = dummy()
    timePassed = 0
    cast = None
    currentObjective = ["None"]
    futureEvents = {}
    nextBoltCharge = player.boltChargeCD

    
    def createCast(name, timeReady, function):
        nonlocal currentObjective
        cast = {
            "name" : name,
            "timeReady" : timeReady,
            "function" : function
        }
        currentObjective = [f"casting {name}"]
        return cast

    def getDmg(ability, dotDmg=False):
        msg = ""
        critRoll = uniform(1, 101)
        critChance = player.crit

        if ability == "bolt":
            critChance += player.boltCritBuff
        elif ability == "orb":
            critChance += player.orbCritBuff

        if dotDmg:
            baseDmg = dotDmg
        else:
            baseDmg = actionInfo["dmg"]

        if critRoll <= critChance:
            baseDmg *= 2
            msg += "CRIT "

        dmgDealt = floor(baseDmg * target.mitigation  * target.dmgMultiplier)
        msg += f"{dmgDealt} dmg"
        return dmgDealt, msg

    def shootbolt():
        nonlocal cast
        nonlocal currentObjective
        cast = None
        currentObjective = ["shooting icebolt"]
        if not target.debuffs["frozen"]:
            target.debuffs["iceboltCharge"] += 1
        dmgDealt, msg = getDmg("bolt")
        currentObjective.append(msg)

        if target.debuffs["iceboltCharge"] == 5:
            target.freeze()
            currentObjective.append("Target frozen")
            futureEvents["unfreeze"] = [timePassed + 5000, target.unfreeze, [], "Target unfrozen"]

        player.orbReady -= 500
        return dmgDealt

    def shootorb():
        nonlocal cast
        nonlocal currentObjective
        cast = None
        currentObjective = ["shooting iceOrb"]
        dmgDealt, msg = getDmg("orb")
        currentObjective.append(msg)

        return dmgDealt

    def hypo():
        nonlocal currentObjective
        currentObjective = ["used hypothermic frenzy"]

        player.haste += actionInfo["hasteBuff"]
        player.dmgMultiplier += actionInfo["dmgBuff"]
        player.orbReady = 0
        futureEvents["unhypo"] = [timePassed + actionInfo["duration"]*1000, unhypo, [actionInfo["hasteBuff"],actionInfo["dmgBuff"]], "hypothermic frenzy wears off"]

    def unhypo(haste, dmg):
        player.haste -= haste
        player.dmgMultiplier -= dmg

    def chilling():
        nonlocal currentObjective
        currentObjective = ["used chilling radiance"]

        player.boltCritBuff = actionInfo["boltCritBuff"]
        player.orbCritBuff = actionInfo["orbCritBuff"]

        target.dots["chilling"] = {
            "level" : actionInfo["level"],
            "nextTick" : timePassed + (actionInfo["tickInterval"]*1000)/(1+(player.haste/100)),
            "interval" : actionInfo["tickInterval"]*1000
        }
        futureEvents["unchilling"] = [timePassed + actionInfo["duration"]*1000, unchilling, [], "chilling radiance wears off"]

        return 0

    def unchilling():
        player.boltCritBuff = 0
        player.orbCritBuff = 0

        target.debuffs["chillingRooted"] = False
        del target.dots["chilling"]

    def enchant():
        nonlocal cast
        nonlocal currentObjective
        cast = None
        currentObjective = ["used enchant"]

        player.mindmg += actionInfo["mindmgBuff"]
        player.maxdmg += actionInfo["maxdmgBuff"]
        player.buffs.append("enchant")
        futureEvents["unenchant"] = [timePassed + actionInfo["duration"]*1000, unenchant, [actionInfo["mindmgBuff"],actionInfo["maxdmgBuff"]], "enchant wears off"]

        return 0

    def unenchant(mindmg, maxdmg):
        player.mindmg -= mindmg
        player.maxdmg -= maxdmg
        player.buffs.remove("enchant")

    def arctic():
        nonlocal currentObjective
        currentObjective = ["used arctic aura"]

        player.crit += actionInfo["critBuff"]
        player.buffs.append("arctic")
        futureEvents["unarctic"] = [timePassed + actionInfo["duration"]*1000, unarctic, [actionInfo["critBuff"]], "arctic aura wears off"]

        return 0

    def unarctic(crit):
        player.crit -= crit
        player.buffs.remove("arctic")

    def skull():
        nonlocal currentObjective
        currentObjective = ["used tattooed skull"]

        player.buffs.append("skull")
        player.dmgMultiplier += 0.2
        futureEvents["unskull"] = [timePassed + 10*1000, unskull, [], "tattooed skull wears off"]
        return 0

    def unskull():
        player.dmgMultiplier -= 0.2 # wow
        player.buffs.remove("skull")


    while timePassed <= fightTime*1000:

        dataout["Time"].append(timePassed/1000)
        dataout["Damage"].append(dmgTotal)
        dataout["Sim"].append(ID)


        gcd = (1.5/(1+(player.haste/100)))*1000

        for event in list(futureEvents.keys()):
            if timePassed >= futureEvents[event][0]:
                futureEvents[event][1](*futureEvents[event][2])
                output(timePassed, [futureEvents[event][3]])
                del futureEvents[event]
            

        for dot in target.dots:
            if timePassed >= target.dots[dot]["nextTick"]:
                currentObjective = [f"{dot} tick"]

                dmgRoll = uniform(player.mindmg,player.maxdmg) * player.dmgMultiplier
                if dot == "chilling":
                    dmg = dmgRoll * (0.1 + 0.3*target.dots[dot]["level"])
                dmgDealt, msg = getDmg(dot, dmg)
                dmgTotal += dmgDealt

                currentObjective.append(msg)
                target.dots[dot]["nextTick"] += target.dots[dot]["interval"]/(1+(player.haste/100))
                output(timePassed, currentObjective)


        if player.boltCharges < 3 and nextBoltCharge <= timePassed:
            player.boltCharges += 1
            output(timePassed, ["gained boltCharge"])
            nextBoltCharge = timePassed + player.boltChargeCD

        if cast:
            if cast["timeReady"] <= timePassed:
                    dmgTotal += cast["function"]()
                    output(timePassed, currentObjective)
                    continue

        else: 
            action = None
            if player.playerReady <= timePassed:
                cdMap = {
                    "skull":player.skullReady,
                    "bolt":player.boltReady,
                    "orb":player.orbReady,
                    "hypo":player.hypoReady,
                    "chilling":player.chillingReady,
                    "enchant":player.enchReady,
                    "arctic":player.arcticReady
                }
                for x in APL:
                    content = x.split(" ")
                    if len(content) > 1:
                        condition = content[1][2:].split(":")
                        condType = condition[0]
                        param = condition[1]
                        if condType == "target":
                            try:
                                if target.debuffs[param] == 4:
                                    action = content[0]
                            except:
                                if target.debuffs[param]:
                                    action = content[0]
                        elif condType == "nobuff":
                            if param not in player.buffs:
                                action = content[0]
                        elif condType == "cooldown":
                            if cdMap[param] > timePassed+100:
                                action = content[0]
                                
                    else:
                        action = content[0]


                    if action == "bolt":
                        actionInfo = player.icebolt(player.dmgMultiplier)
                        if player.boltReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            if player.boltCharges > 0:
                                dmgTotal += shootbolt()
                                player.boltCharges -= 1
                            else:
                                castTime = (actionInfo["castTime"]*1000)/(1+(player.haste/100))
                                cast = createCast("icebolt",timePassed + castTime, shootbolt)

                            player.boltReady = timePassed + cd
                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break

                    elif action == "orb":
                        actionInfo = player.iceorb(player.dmgMultiplier)
                        if player.orbReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            castTime = (actionInfo["castTime"]*1000)/(1+(player.haste/100))

                            cast = createCast("iceorb", timePassed + castTime, shootorb)
                            player.orbReady = timePassed + cd + castTime
                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break

                    elif action == "hypo":
                        actionInfo = player.hypo()
                        if player.hypoReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            hypo()
                            player.hypoReady = timePassed + cd
                            output(timePassed, currentObjective)
                            break

                    elif action  == "chilling":
                        actionInfo = player.chilling(player.dmgMultiplier)
                        if player.chillingReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            chilling()
                            player.chillingReady = timePassed + cd
                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break

                    elif action == "enchant":
                        actionInfo = player.enchant()
                        if player.enchReady <= timePassed:
                            castTime = (actionInfo["castTime"]*1000)/(1+(player.haste/100))
                            cast = createCast("enchant", timePassed + castTime, enchant)
                            player.enchReady = timePassed + actionInfo["cooldown"]*1000
                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break
                    
                    elif action == "arctic":
                        actionInfo = player.arctic()
                        if player.arcticReady <= timePassed and action not in player.buffs:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            arctic()
                            player.arcticReady = timePassed + cd
                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break

                    elif action == "skull":
                        if player.skullReady <= timePassed:
                            cd = 80*1000
                            skull()
                            player.skullReady = timePassed + cd
                            output(timePassed, currentObjective)
                            break

        timePassed += interval

    output(timePassed, ["Simulation finished"])

    out.append(round(dmgTotal/fightTime))


#mageSim(44)