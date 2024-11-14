from math import ceil, floor, exp, log
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests

def evalstats(stats, pclass=9):
    defReduced = (1-exp(-stats["def"]*0.0022))*0.87
    defTaken = 1 - defReduced
    if pclass == 0:
        blockReduced = (stats["blo"]/100)*0.6
    else:
        blockReduced = (stats["blo"]/100)*0.45
    blockTaken = 1 - blockReduced
    totalTaken = defTaken*blockTaken
    hpValue = 1/totalTaken
    eHp = stats["hp"]*hpValue

    dps = ((stats["min"]+stats["max"])/2)*(1+(stats["cri"]/100))*(1+(stats["has"]/100))

    burst = ((stats["min"]+stats["max"])/2)*(1+(stats["cri"]/100))

    return {
        "eHp":eHp,
        "DPS":dps,
        "Burst":burst,
        "hpValue":hpValue,
        "dmgRed": defReduced+blockReduced
    }

def getBuildScore(evaluated, realstats, pclass):
    eHp = round(evaluated["eHp"])
    DPS = round(evaluated["DPS"])
    Burst = round(evaluated["Burst"])
    Haste = float(f'{realstats["has"]:.1f}')
    hpVal = evaluated["hpValue"]
    DmgRed = evaluated["dmgRed"]

    if pclass == 3:
        DPS_Score = (log(DPS,2) + log(Burst,2)  + log(eHp,10))/3
        Tank_Score = (log(DPS,10) + log(Burst,11)  + log(eHp,2)  + log(hpVal*60,7)  + log(Haste*8,16))/5
        Hybrid_Score = (log(DPS,3) + log(Burst,4)  + log(eHp,6)  + log(hpVal*50,10)  + log(Haste*8,9))/5

        Overall_Score = ((DPS_Score/1.75) + Tank_Score + Hybrid_Score)*235/3

    elif pclass == 2:
        DPS_Score = (log(DPS,2) + log(Burst,2))/2
        Tank_Score = (log(eHp,2.5) + log(DPS,6) + log(Burst,6))/3
        Hybrid_Score = (log(eHp,5) + log(DPS,4) + log(Burst,5))/3

        Overall_Score = ((DPS_Score/3) + Tank_Score + Hybrid_Score)*226/3
    
    elif pclass == 1:
        DPS_Score = (log((DPS + Burst)/2,2))
        Tank_Score = (log(eHp,2.5) + log(DPS,6) + log(Burst,6))/3
        Hybrid_Score = (log(eHp,5) + log(DPS,4) + log(Burst,5))/3

        Overall_Score = ((DPS_Score/3) + Tank_Score + Hybrid_Score)*225/3
    
    elif pclass == 0:
        DPS_Score = (log(eHp,5) + log(DPS,2) + log(Burst,2))/3
        Tank_Score = (log(eHp,2) + log(DmgRed*100,2) + log(Haste,6))/3
        Hybrid_Score = (log(eHp,5) + log(DPS,4) + log(Burst,5) + log(DmgRed*100,5))/4

        Overall_Score = (DPS_Score + (Tank_Score/3) + Hybrid_Score)*210/3

    return Overall_Score


def generateCard(name,level,pclass,faction,currentPrestige,nextBracket,rank,elo,allocatedStats,realStats,evaluated,items,playerCharms,buffs,tierlistrank=None,score=None,pos=9999):
    block1 = {
        "hp": realStats["hp"],
        "hpr": round(realStats["hpr"], 1),
        "mp": f'{realStats["mp"]:.1f}',
        "mpr": round(realStats["mpr"], 1),
        "def": realStats["def"],
        "blo": f'{realStats["blo"]:.1f}%'
    }
    block2 = {
        "min": realStats["min"],
        "max": realStats["max"],
        "att": realStats["att"],
        "cri": f'{realStats["cri"]}%',
        "has": f'{realStats["has"]:.1f}%'
    }
    block3 = {
        "eHp": round(evaluated["eHp"]),
        "DPS": round(evaluated["DPS"]),
        "Burst": round(evaluated["Burst"]),
        "if": f'{realStats["if"]}%',
        "gs": realStats["gs"]
    }
    if score:
        block3["score"] = f'{floor(score)}'

    image = Image.open("static/misc/newtemplate_tl_2.png")

    font = ImageFont.truetype('static/fonts/Quicksand-Bold.ttf', 17)


    image_editable = ImageDraw.Draw(image)

    image_editable.text((130,52), name, (255,255,255), font=font)
    image_editable.text((130,72), f"{level}", (255,255,255), font=font)
    classIcon = Image.open("static/classes/"+str(pclass)+".png").resize((17,17))
    image.paste(classIcon, (130,95), mask=classIcon)
    if pclass == 1:
        image_editable.text((150,93), "Mage", (33,169,225), font=font)
    elif pclass == 2:
        image_editable.text((150,93), "Archer", (152,206,100), font=font)
    elif pclass == 3:
        image_editable.text((150,93), "Shaman", (79,120,255), font=font)
    elif pclass == 0:
        image_editable.text((150,93), "Warrior", (199,150,111), font=font)
    classIcon = Image.open("static/factions/"+str(faction)+".png").resize((17,17))
    image.paste(classIcon, (130,115), mask=classIcon)
    if faction == 1:
        image_editable.text((150,113), "Bloodlust", (195,41,41), font=font)
    elif faction == 0:
        image_editable.text((150,113), "Vanguard", (69,139,217), font=font)
    classIcon = Image.open("static/misc/prestige.png").resize((17,17))
    image.paste(classIcon, (130,136), mask=classIcon)
    image_editable.text((150,134), f"{currentPrestige:,}/{nextBracket} (Rank {rank}/12)", (234,179,121), font=font)
    if elo < 1600:
        classIcon = Image.open("static/elo/0.png").resize((17,17))
    elif elo < 1800:
        classIcon = Image.open("static/elo/1.png").resize((17,17))
    elif elo < 2000:
        classIcon = Image.open("static/elo/2.png").resize((17,17))
    elif elo < 2200:
        classIcon = Image.open("static/elo/3.png").resize((17,17))
    else:
        classIcon = Image.open("static/elo/4.png").resize((17,17))
    image.paste(classIcon, (130,156), mask=classIcon)
    image_editable.text((150,154), f"{elo:,}", (234,0,255), font=font)
    if tierlistrank:
        rankColours = {
            "SS" : (198,70,160),
            "S" : (159,70,198),
            "A+" : (90,70,198),
            "A" : (70,123,198),
            "A-" : (70,192,198),
            "B+" : (70,198,149),
            "B" : (70,198,97),
            "B-" : (129,198,70),
            "C+" : (184,198,70),
            "C" : (198,186,70),
            "C-" : (198,147,70),
            "D+" : (198,117,70),
            "D" : (198,100,70),
            "D-" : (198,87,70),
            "E" : (185,21,21),
            "F" : (116,0,0)
        }
        msg = ""
        if tierlistrank == "SS":
            msg += f"#{pos} "
        
        msg += tierlistrank
        if pos <= 5:
            wr, hr = image_editable.textsize(msg, font=font)
            gradient = Image.open(f"static/fonts/colours/{pos}.png").resize((wr, hr))
            alpha = Image.new("L", size=(wr, hr))
            ad = ImageDraw.Draw(alpha)
            ad.text((0,0), msg,  fill="white", font=font)
            gradient.putalpha(alpha)
            image.paste(gradient, (130,176), mask=gradient)
        else:
            image_editable.text((130,176), msg, rankColours[tierlistrank], font=font)
    

    xstart = 580
    ystart = 55
    for stat in allocatedStats:
        x = xstart
        y = ystart
        image_editable.text((x,y), str(allocatedStats[stat]), (52,203,73), font=font, align="right", anchor="rt")
        ystart += 21

    font = ImageFont.truetype('static/fonts/Quicksand-Bold.ttf', 15)
    xstart = 199
    ystart = 268
    for stat in block1:
        x = xstart
        y = ystart
        image_editable.text((x,y), str(block1[stat]), (245,194,71), font=font, align="right", anchor="rt")
        ystart += 18
    xstart = 400
    ystart = 268
    for stat in block2:
        x = xstart
        y = ystart
        image_editable.text((x,y), str(block2[stat]), (245,194,71), font=font, align="right", anchor="rt")
        ystart += 18
    xstart = 601
    ystart = 268
    for stat in block3:
        x = xstart
        y = ystart
        image_editable.text((x,y), str(block3[stat]), (245,194,71), font=font, align="right", anchor="rt")
        ystart += 18

    xstart = 8
    ystart = 206
    for item in items:
        x = xstart
        y = ystart
        response = requests.get(f'https://hordes.io/assets/items/{item["type"]}/{item["type"]}{item["tier"]}_q{item["tier_quality"]}.webp')
        itemIcon = Image.open(BytesIO(response.content)).resize((45,45))
        if item["tier_quality"] == 0:
            colour = (255,255,255)
        elif item["tier_quality"] == 1:
            colour = (52,203,73)
        elif item["tier_quality"] == 2:
            colour = (6,129,234)
        elif item["tier_quality"] == 3:
            colour = (158,59,249)
        itemIcon = ImageOps.expand(itemIcon, border=3, fill=colour)
        if item["type"] in ["sword","staff","bow","hammer"]:
            pos = 0
        elif item["type"] == "armlet":
            pos = 1
        elif item["type"] == "armor":
            pos = 2
        elif item["type"] == "bag":
            pos = 3
        elif item["type"] == "boot":
            pos = 4
        elif item["type"] == "glove":
            pos = 5
        elif item["type"] == "ring":
            pos = 6
        elif item["type"] == "amulet":
            pos = 7
        elif item["type"] in ["shield","orb","quiver","totem"]:
            pos = 8
        x += 55*pos
        image.paste(itemIcon, (x,y))
        x += 27
        y += 27
        image_editable.rectangle([x,y+4,x+17,y+16], fill=(16, 19, 29, 80))
        image_editable.text((x,y), f"+{item['upgrade']}", (255,255,255), font=font)

    xstart = 503
    ystart = 206
    for charm in playerCharms:
        x = xstart
        y = ystart
        charmIcon = Image.open(f"static/charms/{charm}.jpg").resize((45,45))
        charmIcon = ImageOps.expand(charmIcon, border=3, fill=(158,59,249))
        image.paste(charmIcon, (x,y))
        xstart += 55

    xstart = 130
    ystart = 12
    for buff in buffs:
        x = xstart
        y = ystart
        buffIcon = Image.open(f"static/buffs/{buff}.jpg").resize((30,30))
        image.paste(buffIcon, (x,y))
        image_editable.rectangle([x+18,y+17,x+28,y+28], fill=(16, 19, 29, 80))
        image_editable.text((x+20,y+14), f"{buffs[buff]}", (255,255,255), font=font)
        xstart += 32

    return image
    #image.save("static/misc/output.png")

def initreal(allocated, real, bloodline, multiplier):
    #STR
    real["hp"] += allocated["str"]*2
    real["hpr"] += allocated["str"]*0.03
    #STA
    real["hp"] += allocated["sta"]*4
    real["def"] += allocated["sta"]
    #DEX
    real["cri"] += allocated["dex"]*0.05
    #INT
    real["cri"] += allocated["int"]*0.04
    real["mp"] += allocated["int"]*0.8
    #WIS
    real["has"] += allocated["wis"]*0.03
    real["mp"] += allocated["wis"]*0.8
    #LUCK
    real["cri"] += allocated["luc"]*0.02
    real["if"] += allocated["luc"]*0.5

    #BLOODLINE
    if bloodline == "int":
        real["min"] += 0.4*allocated["int"]
        real["max"] += 0.4*allocated["int"]
    elif bloodline == "dex":
        real["min"] += 0.4*allocated["dex"]
        real["max"] += 0.4*allocated["dex"]
    elif bloodline == "wis":
        real["min"] += 0.4*allocated["wis"]
        real["max"] += 0.4*allocated["wis"]
    elif bloodline == "str":
        real["min"] += 0.3*allocated["str"]
        real["max"] += 0.3*allocated["str"]
        real["hpr"] += 0.03*allocated["str"]
        #real["def"] += 60


    #ROUNDING
    real["if"] = ceil(real["if"])
    real["min"] = floor(real["min"])
    real["max"] = floor(real["max"])
    real["cri"] = (floor(real["cri"]*10)/10)

    #BUFF
    real["min"] = floor(real["min"]*multiplier)
    real["max"] = floor(real["max"]*multiplier)
    return real
