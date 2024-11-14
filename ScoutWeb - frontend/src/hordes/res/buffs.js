//MAGE
export function enchantBuff(level) {
    return [{
        "min": Math.floor(2 + 1.5*level),
        "max": Math.floor(3 + 3.5*level)
    },false]
}

export function arcticBuff(level) {
    return [{
        "cri": 3 * level
    },false]
}

export function hypothermicBuff(level) {
    return [{
        "has": 3 + 7*level,
        "dmg": (2 + 7*level)/100 
    },1]
}

//WARRIOR
export function armorBuff(level) {
    return [{
        "def": Math.round(40 + 40*level)
    },0]
}

export function warcryBuff(level) {
    return [{
        "min": 3*level,
        "max": 4*level,
        "hp": 50*level
    },false]
}

export function crusaderBuff(level) {
    return [{
        "def": Math.round(30*level)
    },false]
}

export function bulwarkBuff(level) {
    return [{
        "blo": 30 + 4*level
    },0]
}

export function enrageBuff(level, stacks) {
    return [{
        "dmg" : (stacks * (2 * level + 2))/100
    },0]
}

//ARCHER
export function temporalBuff(level) {
    return [{
        "has": 3*level
    },false]
}

export function cranialBuff(level) {
    return [{
        "cri": Math.round(3*level)
    },2]
}

export function invigorateBuff(level) {
    return [{
        "dmg": (9*level)/100 
    },2]
}

//SHAMAN
export function howlBuff(level) {
    return [{
        "has": 10 + 6*level
    },false]
}

export function plagueBuff(level, stacks) {
    return [{
        "has": (1 + 2*level)*stacks
    },3]
}

