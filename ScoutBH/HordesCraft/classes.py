from random import uniform, randint
from math import floor

class shaman:
    def __init__(self, stats, skills):
        self.stats = stats
        self.skills = skills
        self.plagueStacks = 0
        self.dmgMultiplier = 1
        self.casting = False
        self.buffs = []

        self.revdropped = 0
        self.plaguedropped = 0
        self.nextcanine = 0
        self.healing = {
            "revitalize" : 0,
            "totem" : 0
        }

        self.cds = {
            "player" : 0,
            "skull" : 0,
            "revitalize" : 0,
            "decay" : 0,
            "canine" : 0,
            "plague" : 0,
            "mend" : 0,
            "mimir" : 0,
            "totem" : 0,
            "cleanse" : 0
        }
    
    def revitalize(self, revStacks):
        level = self.skills["revitalize"]
        dmgRoll = uniform(self.stats["min"],self.stats["max"])

        return {
            "heal" : (6 + dmgRoll * (0.028 + 0.024 * level)) * (1 + 0.3 * (revStacks -1)),
            "interval" : 1
        }

    def mend(self, revStacks):
        level = self.skills["mend"]
        dmgRoll = uniform(self.stats["min"],self.stats["max"])

        return {
            "heal" : (15 + dmgRoll * (0.2 + 0.18 * level)) * (1 + 0.3 * revStacks),
            "castTime" : 1.7
        }

    def decay(self):
        return {
            "cooldown" : 3
        }

    def canine(self):
        level =  self.skills["canine howl"]
        return {
            "hasteBuff" : 10 + 6 * level,
            "duration" : 15,
            "cooldown" : 60
        }

    def plagueBuff(self):
        level = self.skills["plaguespreader"]
        return {
            "hasteBuff" : 1 + 2 * level,
            "duration" : 7
        }

    def totem(self):
        level = self.skills["healing totem"]
        dmgRoll = uniform(self.stats["min"],self.stats["max"])
        return {
            "heal" : dmgRoll * (0.08 + 0.05 * level),
            "castTime" : 2.3,
            "duration" : 30,
            "interval" : 2,
            "cooldown" : 60
        }

    def cleanse(self, debuffs):
        level = self.skills["mimirs cleanse"]
        debuffs = min([level, debuffs])
        dmgRoll = uniform(self.mindmg,self.maxdmg)
        return {
            "heal" : (1 + debuffs) * (15 + 0.25 * dmgRoll),
            "cooldown" : 12
        }


class mage:
    def __init__(self, stats, skills):
        self.mindmg = stats["min"]
        self.maxdmg = stats["max"]
        self.atkspeed = stats["atkspeed"]
        self.crit = stats["crit"]
        self.haste = stats["haste"]
        self.skills = skills
        self.dmgMultiplier = 1
        self.buffs = []

        self.boltChargeCD = 6000
        self.boltCharges = 3

        self.boltCritBuff = 0
        self.orbCritBuff = 0

        self.playerReady = 0
        self.skullReady = 0
        self.boltReady = 0
        self.orbReady = 0
        self.hypoReady = 0
        self.chillingReady = 0
        self.enchReady =  0
        self.arcticReady = 0


    def iceorb(self, m):
        level = self.skills["iceorb"]
        dmgRoll = uniform(self.mindmg,self.maxdmg) * m
        return {
            "cost" : 5 + 5*level,
            "dmg" : 10 + dmgRoll*(0.51 + 0.56*level),
            "castTime" : 1.5,
            "cooldown" : 15,
        }

    def icebolt(self, m):
        level = self.skills["icebolt"]
        dmgRoll = uniform(self.mindmg,self.maxdmg)* m
        return {
            "cost" : 1 + 2*level,
            "dmg" : 5 + dmgRoll*(0.38 + 0.38*level),
            "castTime" : 1.5,
            "cooldown" : 0,
        }

    def hypo(self):
        level = self.skills["hypothermic frenzy"]
        return {
            "cost" : 0,
            "hasteBuff" : 3 + 7*level,
            "dmgBuff" : (2 + 7*level)/100,
            "duration" : 12,
            "castTime" : 0,
            "cooldown" : 45,
        }

    def chilling(self, m):
        level = self.skills["chilling radiance"]
        dmgRoll = uniform(self.mindmg,self.maxdmg)* m
        return {
            "cost" : 4*level,
            "boltCritBuff" : 1 +  3*level,
            "orbCritBuff" : 2 + 3*level,
            "dmg" : dmgRoll * (0.1 + 0.3*level),
            "duration" : 5.5 + 0.5*level,
            "tickDelay" : 1.5,
            "tickInterval" : 1.5,
            "castTime" : 0,
            "cooldown" : 25,
            "level" : level
        }

    def enchant(self):
        level = self.skills["enchantment"]
        return {
            "cost" : 2 + 3*level,
            "mindmgBuff" : floor(2 + 1.5*level),
            "maxdmgBuff" : floor(3 + 3.5*level),
            "duration" : 300,
            "castTime" : 1.5,
            "cooldown" : 0,
        }

    def arctic(self):
        level = self.skills["arctic aura"]
        return {
            "cost" : 5 + 10*level,
            "critBuff" : 3*level,
            "duration" : 300,
            "castTime" : 0,
            "cooldown" : 120,
        }

class archer:
    def __init__(self, stats, skills):
        self.stats = stats
        self.skills = skills
        self.dmgMultiplier = 1
        self.casting = False

        self.dmg = {
            "swift shot" : 0,
            "precise shot" : 0,
            "invigorate" : 0,
            "bone shot" : 0,
            "poison arrows" : 0,
            "auto attack" : 0
        }

        self.cds = {
            "player" : 0,
            "skull" : 0,
            "revitalize" : 0,
            "decay" : 0,
            "canine" : 0,
            "plague" : 0,
            "mend" : 0,
            "mimir" : 0,
            "totem" : 0,
            "cleanse" : 0
        }

    def auto(self, m):
        dmgRoll = uniform(self.mindmg,self.maxdmg) * m
        return {
            "dmg" : dmgRoll
        }

    def swiftshot(self, m):
        level = self.skills["swift shot"]
        dmgRoll = uniform(self.mindmg,self.maxdmg) * m
        return {
            "cost" : 1 + 1*level,
            "dmg" : 5 + dmgRoll*(0.28 + 0.28*level),
            "castTime" : 1.5,
            "cooldown" : 0
        }

    def preciseshot(self, m):
        level = self.skills["precise shot"]
        dmgRoll = uniform(self.mindmg,self.maxdmg) * m
        return {
            "cost" : 2 + 3*level,
            "dmg" : 5 + dmgRoll*(0.6 + 0.46*level),
            "castTime" : 1.7,
            "cooldown" : 6
        }

    def dash(self):
        return {
            "cost" : 5,
            "locktime" : 0.3,
            "duration" : 6,
            "castTime" : 0,
            "cooldown" : 10,
        }

    def invigorate(self):
        level = self.skills["invigorate"]
        return {
            "cost" : 0,
            "mpBuff" : (3+5*level)/100,
            "dmgBuff" : (9*level)/100,
            "duration" : 17,
            "castTime" : 0,
            "cooldown" : 50,
        }

    def temporal(self):
        level = self.skills["invigorate"]
        return {
            "cost" : 5 + 5*level,
            "hasteBuff" : 3*level,
            "duration" : 300,
            "castTime" : 0,
            "cooldown" : 120,
        }

    def poison(self):
        level = self.skills["poison arrows"]
        return {
            "dmg" : ((5 + 25*level))/1000,
            "level" : level,
            "duration" : 10,
            "tickInterval" : 1.5
        }
