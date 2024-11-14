from HordesCraft.classes import *
from HordesCraft.targets import *
from random import uniform
from math import exp


def output(time, msg):
    pass
    #print(f"{time}ms : {' | '.join(msg)}")


def archerSim(fightTime, stats, skills, APL, out, interval, dataout, ID):
    dmgTotal = 0
    player = archer(stats, skills)
    target = dummy()
    timePassed = 0
    cast = None
    currentObjective = ["None"]
    futureEvents = {}

    poisonInfo = player.poison()

    
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
        
        if dotDmg:
            baseDmg = dotDmg
        elif ability == "auto":
            baseDmg = autoInfo["dmg"]
        elif ability == "instaswift":
            baseDmg = actionInfo["dmg"] * 1.5
        else:
            baseDmg = actionInfo["dmg"]

        if critRoll <= critChance:
            baseDmg *= 2
            msg += "CRIT "

        dmgDealt = round(baseDmg * target.mitigation)
        msg += f"{dmgDealt} dmg"

        if ability == "preciseshot":
            return dmgDealt, msg, actionInfo["dmg"]
           
        return dmgDealt, msg

    def shootauto():
        nonlocal currentObjective
        currentObjective = ["shooting auto attack"]

        dmgDealt, msg = getDmg("auto")
        currentObjective.append(msg)

        return dmgDealt

    def shootswift(instant=False):
        nonlocal cast
        nonlocal currentObjective
        cast = None
        currentObjective = ["shooting swiftshot"]

        if instant:
            dmgDealt, msg = getDmg("instaswift")
        else:
            dmgDealt, msg = getDmg("swift")
        currentObjective.append(msg)


        return dmgDealt

    def shootprecise():
        nonlocal cast
        nonlocal currentObjective
        cast = None
        currentObjective = ["shooting preciseshot"]

        dmgDealt, msg, poisonDmg = getDmg("preciseshot")
        currentObjective.append(msg)
        player.swiftCharges += 2

        target.poisonDot = [0, timePassed + poisonInfo["tickInterval"], poisonDmg, poisonInfo["duration"]]
        if target.poisonDot[0] != 3:
            target.poisonDot[0] +=1
        target.poisonDot[2] *= target.poisonDot[0]

        if "poison" in target.dots:
            if target.dots["poison"]["stacks"] < 3:
                target.dots["poison"]["stacks"] += 1
            target.dots["poison"]["dmg"] = poisonDmg
            futureEvents["unpoison"][0] = timePassed + poisonInfo["duration"]*1000
        else:
            target.dots["poison"] = {
                "level" : poisonInfo["level"],
                "dmg" : poisonDmg,
                "nextTick" : (timePassed + poisonInfo["tickInterval"]*1000)/(1+(player.haste/100)),
                "interval" : poisonInfo["tickInterval"]*1000,
                "stacks" : 1
            }
            futureEvents["unpoison"] = [timePassed + poisonInfo["duration"]*1000, unpoison, [], "poison arrows wears off"]

        return dmgDealt

    def unpoison():
        del target.dots["poison"]

    def dash():
        nonlocal currentObjective
        currentObjective = ["dash"]

        player.dashBuff = True
        player.preciseReady = 0
        futureEvents["undash"] = [timePassed + actionInfo["duration"]*1000, undash, [], "dash buff wears off"]

    def undash():
        player.dashBuff = False

    def invigorate():
        nonlocal currentObjective
        currentObjective = ["used invigorate"]

        player.dmgMultiplier += actionInfo["dmgBuff"]
        futureEvents["uninvigorate"] = [timePassed + actionInfo["duration"]*1000, uninvigorate, [actionInfo["dmgBuff"]], "invigorate wears off"]

    def uninvigorate(dmg):
        player.dmgMultiplier -= dmg

    def skull():
        nonlocal currentObjective
        currentObjective = ["used tattooed skull"]

        player.buffs.append("skull")
        player.dmgMultiplier += 0.2
        futureEvents["unskull"] = [timePassed + 10*1000, unskull, [], "tattooed skull wears off"]
        return 0

    def unskull():
        player.dmgMultiplier -= 0.2
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

                if dot == "chilling":
                    dmgRoll = uniform(player.mindmg,player.maxdmg)
                    dmg = dmgRoll * (0.1 + 0.3*target.dots[dot]["level"])

                elif dot == "poison":
                    dmg = floor(((5+target.dots[dot]["level"]*25)/1000 * target.dots[dot]["dmg"]) + 3) * target.dots[dot]["stacks"]
                    currentObjective.append(f"{target.dots[dot]['stacks']} stacks")
                    #currentObjective.append(str(player.dmgMultiplier))

                dmgDealt, msg = getDmg(dot, dmg)
                dmgTotal += dmgDealt

                currentObjective.append(msg)
                target.dots[dot]["nextTick"] += target.dots[dot]["interval"]/(1+(player.haste/100))
                output(timePassed, currentObjective)


        if player.autoReady <= timePassed and not player.dashBuff:
            autoInfo = player.auto(player.dmgMultiplier)
            dmgTotal += shootauto()
            player.autoReady = timePassed + (100/player.atkspeed)/(1+(player.haste/100))*1000
            output(timePassed, currentObjective)
            

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
                    "swift":player.swiftReady,
                    "precise":player.preciseReady,
                    "invig":player.invigReady,
                    "dash":player.dashReady,
                    "temp":player.tempReady
                }
                for x in APL:
                    content = x.split(" ")
                    if len(content) > 1:
                        condition = content[1][2:].split(":")
                        condType = condition[0]
                        param = condition[1]
                        if condType == "target":
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


                    if action == "swift":
                        actionInfo = player.swiftshot(player.dmgMultiplier)
                        if player.swiftReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            if player.swiftCharges > 0:
                                dmgTotal += shootswift(True)
                                player.swiftCharges -= 1
                            else:
                                castTime = (actionInfo["castTime"]*1000)/(1+(player.haste/100))
                                cast = createCast("swiftshot",timePassed + castTime, shootswift)

                            player.swiftReady = timePassed + cd
                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break

                    elif action == "precise":
                        actionInfo = player.preciseshot(player.dmgMultiplier)
                        if player.preciseReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            if player.dashBuff:
                                dmgTotal += shootprecise()
                                player.preciseReady = timePassed + cd
                                player.dashBuff = False
                                del futureEvents["undash"]
                            else:
                                castTime = (actionInfo["castTime"]*1000)/(1+(player.haste/100))
                                cast = createCast("preciseshot",timePassed + castTime, shootprecise)
                                player.preciseReady = timePassed + cd + castTime

                            player.playerReady = timePassed + gcd
                            output(timePassed, currentObjective)
                            break

                    elif action == "dash":
                        actionInfo = player.dash()
                        if player.dashReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            dash()

                            player.dashReady = timePassed + cd
                            player.playerReady = timePassed + actionInfo["locktime"]*1000
                            output(timePassed, currentObjective)
                            break

                    elif action == "invigorate":
                        actionInfo = player.invigorate()
                        if player.invigReady <= timePassed:
                            cd = (actionInfo["cooldown"]*1000)/(1+(player.haste/100))
                            invigorate()
                            player.invigReady = timePassed + cd
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