export function evalstats(stats, pclass) {
    let defReduced = (1-Math.exp(-stats["def"]*0.0022))*0.87
    let defTaken = 1 - defReduced
    let blockReduced = (pclass == 0) ? (stats["blo"]/100)*0.6 : (stats["blo"]/100)*0.45
    let blockTaken = 1 - blockReduced
    let totalTaken = defTaken*blockTaken
    let hpValue = 1/totalTaken
    let eHp = stats["hp"]*hpValue

    let dps = ((stats["min"]+stats["max"])/2)*(1+(stats["cri"]/100))*(1+(stats["has"]/100))

    let burst = ((stats["min"]+stats["max"])/2)*(1+(stats["cri"]/100))

    return {
        "eHp":eHp,
        "DPS":dps,
        "Burst":burst,
        "hpValue":hpValue,
        "dmgRed": defReduced+blockReduced
    }
}

export function initreal(allocated, real, bloodline, multiplier) {
    //STR
    real["hp"] += allocated["str"]*2
    real["hpr"] += allocated["str"]*0.03
    //STA
    real["hp"] += allocated["sta"]*4
    real["def"] += allocated["sta"]
    //DEX
    real["cri"] += allocated["dex"]*0.05
    //INT
    real["cri"] += allocated["int"]*0.04
    real["mp"] += allocated["int"]*0.8
    //WIS
    real["has"] += allocated["wis"]*0.03
    real["mp"] += allocated["wis"]*0.8
    //LUCK
    real["cri"] += allocated["luc"]*0.02
    real["if"] += allocated["luc"]*0.5

    //BLOODLINE
    if (bloodline == "int") {
        real["min"] += 0.4*allocated["int"]
        real["max"] += 0.4*allocated["int"]
    } else if (bloodline == "dex") {
        real["min"] += 0.4*allocated["dex"]
        real["max"] += 0.4*allocated["dex"]
    } else if (bloodline == "wis") {
        real["min"] += 0.4*allocated["wis"]
        real["max"] += 0.4*allocated["wis"]
    } else if (bloodline == "str") {
        real["min"] += 0.3*allocated["str"]
        real["max"] += 0.3*allocated["str"]
        real["hpr"] += 0.03*allocated["str"]
        //real["def"] += 60
    }


    //ROUNDING
    real["if"] = Math.ceil(real["if"])
    real["min"] = Math.floor(real["min"])
    real["max"] = Math.floor(real["max"])
    real["cri"] = (Math.floor(real["cri"]*10)/10)

    //BUFF
    real["min"] = Math.floor(real["min"]*multiplier)
    real["max"] = Math.floor(real["max"]*multiplier)

    return real
}

export function getbuildscore(evaluated, realStats, pclass) {
    let eHp = Math.round(evaluated["eHp"])
    let DPS = Math.round(evaluated["DPS"])
    let Burst = Math.round(evaluated["Burst"])
    let Haste = parseFloat(realStats["has"]).toFixed(1)
    let hpVal = evaluated["hpValue"]
    let DmgRed = evaluated["dmgRed"]
    let DPS_Score, Tank_Score, Hybrid_Score, Overall_Score

    const log = (n, base) => Math.log(n) / Math.log(base);

    if (pclass == 3) {
        DPS_Score = (log(DPS,2) + log(Burst,2)  + log(eHp,10))/3
        Tank_Score = (log(DPS,10) + log(Burst,11)  + log(eHp,2)  + log(hpVal*60,7)  + log(Haste*8,16))/5
        Hybrid_Score = (log(DPS,3) + log(Burst,4)  + log(eHp,6)  + log(hpVal*50,10)  + log(Haste*8,9))/5

        Overall_Score = ((DPS_Score/1.75) + Tank_Score + Hybrid_Score)*235/3
    } else if (pclass == 2) {
        DPS_Score = (log(DPS,2) + log(Burst,2))/2
        Tank_Score = (log(eHp,2.5) + log(DPS,6) + log(Burst,6))/3
        Hybrid_Score = (log(eHp,5) + log(DPS,4) + log(Burst,5))/3

        Overall_Score = ((DPS_Score/3) + Tank_Score + Hybrid_Score)*226/3
    } else if (pclass == 1) {
        DPS_Score = (log((DPS + Burst)/2,2))
        Tank_Score = (log(eHp,2.5) + log(DPS,6) + log(Burst,6))/3
        Hybrid_Score = (log(eHp,5) + log(DPS,4) + log(Burst,5))/3

        Overall_Score = ((DPS_Score/3) + Tank_Score + Hybrid_Score)*225/3
    } else if (pclass == 0) {
        DPS_Score = (log(eHp,5) + log(DPS,2) + log(Burst,2))/3
        Tank_Score = (log(eHp,2) + log(DmgRed*100,2) + log(Haste,6))/3
        Hybrid_Score = (log(eHp,5) + log(DPS,4) + log(Burst,5) + log(DmgRed*100,5))/4

        Overall_Score = (DPS_Score + (Tank_Score/3) + Hybrid_Score)*210/3
    }

    return Overall_Score
}