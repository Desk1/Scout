from math import floor, pow

#MAGE
def enchantBuff(level):
    return [{
        "min": floor(2 + 1.5*level),
        "max": floor(3 + 3.5*level)
    },False]

def arcticBuff(level):
    return [{
        "cri": 3 * level
    },False]

def hypothermicBuff(level):
    return [{
        "has": 3 + 7*level,
        "dmg": (2 + 7*level)/100 #multiplier
    },1]

#WARRIOR
def armorBuff(level):
    return [{
        "def": round(40 + 40*level)
    },0]

def warcryBuff(level):
    return [{
        "min": 3*level,
        "max": 4*level,
        "hp": 50*level
    },False]

def crusaderBuff(level):
    return [{
        "def": round(30*level)
    },False]

def bulwarkBuff(level):
    return [{
        "blo": 30 + 4*level
    },0]

def enrageBuff(level, stacks):
    return [{
        "dmg" : (stacks * (2 * level + 2))/100
    },0]

#ARCHER
def temporalBuff(level):
    return [{
        "has": 3*level
    },False]

def cranialBuff(level):
    return [{
        "cri": round(3*level)
    },2]

def invigorateBuff(level):
    return [{
        "dmg": (9*level)/100 #multiplier
    },2]

#SHAMAN
def howlBuff(level):
    return [{
        "has": 10 + 6*level
    },False]

def plagueBuff(level, stacks):
    return [{
        "has": (1 + 2*level)*stacks
    },3]