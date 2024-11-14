import * as buffs from "./res/buffs.js"
import {evalstats, initreal, getbuildscore} from "./res/charstats.js"

export default function playerstats(args, playerinfo, items, tierlist) {
    let charms = ["Tattooed Skull","Hardened Egg","Blue Marble","Little Bell","Ship Pennant"]
    let buffa = {
        "enchant" : buffs.enchantBuff,
        "arctic": buffs.arcticBuff,
        "hypo" : buffs.hypothermicBuff,
        "armor" : buffs.armorBuff,
        "warcry" : buffs.warcryBuff,
        "crusader" : buffs.crusaderBuff,
        "bulwark" : buffs.bulwarkBuff,
        "temporal" : buffs.temporalBuff,
        "cranial" : buffs.cranialBuff,
        "invigorate" : buffs.cranialBuff,
        "canine" : buffs.howlBuff,
        "enrage" : buffs.enrageBuff,
        "plague" : buffs.plagueBuff

    }
    let ranks = [0,4000,8000,12000,16000,20000,24000,28000,32000,36000,40000,44000,48000]
    let rank
    let playerCharms = []

    if (playerinfo["prestige"] > 48000) {
        rank = 12
    } else {
        rank = ranks.indexOf(Math.floor(playerinfo["prestige"]/4000)*4000)
    }

    let name = playerinfo["name"]
    let pclass = playerinfo["pclass"]
    let elo = playerinfo["elo"]
    let level = playerinfo["level"]
    let faction = playerinfo["faction"]
    let currentPrestige = playerinfo["prestige"]
    let nextBracket = Math.ceil(playerinfo["prestige"]/4000)*4000 ? "48.0k" : toString((Math.ceil(playerinfo["prestige"]/4000)*4000)/1000)+"k"
    let unallocated = playerinfo["level"]*3
    
    /*
    if (args.prestige == "max") {
        rank = 12
        currentPrestige = 48000
        nextBracket = "48.0k"
    } else if (args.prestige == "none") {
        rank = 0
        currentPrestige = 0
        nextBracket = "4.0k"
    }
    */

    let allocatedStats = {
        "str": 10,
        "sta": 10,
        "dex": 10,
        "int": 10,
        "wis": 10,
        "luc": 5
    }

    let realStats, realStats_tl
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
        "gs": 0
    }
    realStats_tl = {
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
        "gs": 0
    }

    switch (pclass) {
        case 1:
            var bloodline = "int"
            break
        case 2:
            var bloodline = "dex"
            break
        case 3:
            var bloodline = "wis"
            break
        case 0:
            var bloodline = "str"
            break
    }

    allocatedStats["sta"] += level*2
    realStats["hp"] += level*8
    realStats_tl["hp"] += level*8
    allocatedStats[bloodline] += level
    if (!args.spec) {
        allocatedStats[bloodline] += unallocated
    } else {
        /*
        args.spec.forEach((s) => {
            //allocatedStats[s[0]] += s[1] advanced spec
        })
        */
        allocatedStats[args.spec] += unallocated
    }

    items.forEach(item => {
        for (const stat in item["attr"]) {
            if (allocatedStats.hasOwnProperty(stat)) {
                allocatedStats[stat] += item["attr"][stat]["value"]
            } else {
                realStats[stat] += item["attr"][stat]["value"]
                realStats_tl[stat] += item["attr"][stat]["value"]
            }
        }
        realStats["gs"] += item["gearscore"]
    })

    args.charms.forEach((c) => {
        realStats["gs"] += 30
        playerCharms.push(c)
    })

    if (rank >= 1) {
        realStats["mov"] += 5
    }
    if (rank >= 2) {
        realStats["mp"] += 50
    }
    if (rank >= 3) {
        realStats["if"] += 15
    }
    if (rank >= 4) {
        realStats["min"] += 5
        realStats["max"] += 5
    }
    if (rank >= 5) {
        realStats["hpr"] += 2
        realStats["mpr"] += 2
    }
    if (rank >= 6) {
        realStats["mov"] += 5
    }
    if (rank >= 7) {
        realStats["hp"] += 30
    }
    if (rank >= 8) {
        realStats["if"] += 15
    }
    if (rank >= 9) {
        realStats["cri"] += 5
    }
    if (rank >= 10) {
        realStats["has"] += 3
    }
    if (rank >= 11) {
        realStats["hp"] += 30
    }
    if (rank >= 12) {
        realStats["min"] += 5
        realStats["max"] += 5
    }

    realStats_tl["mov"] += 5
    realStats_tl["mp"] += 50
    realStats_tl["if"] += 15
    realStats_tl["min"] += 5
    realStats_tl["max"] += 5
    realStats_tl["hpr"] += 2
    realStats_tl["mpr"] += 2
    realStats_tl["mov"] += 5
    realStats_tl["hp"] += 30
    realStats_tl["if"] += 15
    realStats_tl["cri"] += 5
    realStats_tl["has"] += 3
    realStats_tl["hp"] += 30
    realStats_tl["min"] += 5
    realStats_tl["max"] += 5

    let activeBuffs = {}
    let dmgMultiplier = 1
    args.buffs.forEach(buff => {
        let level = buff.level
        let stacks = buff.stacks

        if (buff.name == "skull") {
            dmgMultiplier += 0.2
            activeBuffs["skull"] = 1
        } else {
            let effect = stacks ? buffa[buff.name](level, stacks) : buffa[buff.name](level)

            if (!(effect[1] != false && effect[1] != pclass)) {
                Object.keys(effect[0]).forEach(e => {
                    if (e == "dmg") {
                        dmgMultiplier += effect[0][e]
                    } else {
                        realStats[e] += effect[0][e]
                    }
                })
                activeBuffs[buff.name] = stacks ? stacks : level
            }
        }
    })

    realStats = initreal(allocatedStats, realStats, bloodline, dmgMultiplier)
    let evaluated = evalstats(realStats, pclass)

    realStats_tl = initreal(allocatedStats, realStats_tl, bloodline, 1)
    let evaluated_tl = evalstats(realStats_tl, pclass)

    let Overall_Score = parseFloat(getbuildscore(evaluated_tl, realStats_tl, pclass).toFixed(7))
    let pos = 1
    let tlrank = ""
    for (let r = 0; r < tierlist.boundaries.length; r++) {
        if (Overall_Score >= parseFloat(tierlist.boundaries[r][0])) {
            tlrank = tierlist.boundaries[r][1]
            break
        }
    }
    for (let r = 0; r < tierlist.rankings.length; r++) {
        if (Overall_Score >= parseFloat(tierlist.rankings[r])) { break }
        pos++
    }

    return {
        stats: {
            allocated: allocatedStats,
            real: realStats,
            evaluated: {
                "eHp": evaluated["eHp"],
                "DPS": evaluated["DPS"],
                "Burst": evaluated["Burst"],
                "buildscore": Overall_Score
            },
        },
        tierlist: {
            rank: tlrank,
            position: pos
        },
        buffs: activeBuffs,
        charms: playerCharms
    }
}   
