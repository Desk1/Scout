from PIL import Image, ImageDraw, ImageFont, ImageOps
from math import ceil, sqrt
from func.playerCard import initreal, evalstats, getBuildScore

blood_table = {
    0 : "str",
    1 : "int",
    2 : "dex",
    3 : "wis"
}

base = {
    1 : [{'hp': 940, 'hpr': 4.3, 'mp': 310.0, 'mpr': 5.0, 'def': 115, 'blo': 0.0, 'min': 86, 'max': 86, 'att': 10, 'cri': 18.2, 'has': 3.3, 'mov': 115, 'bag': 15, 'if': 33, 'gs': 0},{'str': 10, 'sta': 100, 'dex': 10, 'int': 190, 'wis': 10, 'luc': 5}],
    2 : [{'hp': 940, 'hpr': 4.3, 'mp': 166.0, 'mpr': 5.0, 'def': 115, 'blo': 0.0, 'min': 86, 'max': 86, 'att': 10, 'cri': 20.0, 'has': 3.3, 'mov': 115, 'bag': 15, 'if': 33, 'gs': 0},{'str': 10, 'sta': 100, 'dex': 190, 'int': 10, 'wis': 10, 'luc': 5}],
    3 : [{'hp': 940, 'hpr': 4.3, 'mp': 310.0, 'mpr': 5.0, 'def': 115, 'blo': 0.0, 'min': 86, 'max': 86, 'att': 10, 'cri': 11.0, 'has': 8.7, 'mov': 115, 'bag': 15, 'if': 33, 'gs': 0},{'str': 10, 'sta': 100, 'dex': 10, 'int': 10, 'wis': 190, 'luc': 5}]
}

def getItemScore(item, itemClass, gears):
    return 0
    """if not itemClass:
        return 0
    scores = []
    for p in gears[itemClass]:
        realStats1 =  base[itemClass][0].copy()
        allocatedStats1 =  base[itemClass][1].copy()

        basegear = gears[itemClass][p].copy()
        basegear.pop(item["type"])
        basegear = list(basegear.values())

        for bitem in basegear:
            for stat in bitem["attr"]:
                if stat in allocatedStats1:
                    allocatedStats1[stat] += bitem["attr"][stat]["value"]
                else:
                    realStats1[stat] += bitem["attr"][stat]["value"]
            realStats1["gs"] += bitem["gearscore"]

        realStats2 = realStats1.copy()
        allocatedStats2 = allocatedStats1.copy()

        evaluated1 = evalstats(initreal(allocatedStats1, realStats1,  blood_table[itemClass], 1))
        score1 = getBuildScore(evaluated1, realStats1, itemClass)

        if itemClass in [1,3]:
            score1 += 0.14

        for stat in item["attr"]:
            if stat in allocatedStats2:
                allocatedStats2[stat] += item["attr"][stat]["value"]
            else:
                realStats2[stat] += item["attr"][stat]["value"]
        realStats2["gs"] += item["gearscore"]

        evaluated2 = evalstats(initreal(allocatedStats2, realStats2,  blood_table[itemClass], 1))
        score2 = getBuildScore(evaluated2, realStats2, itemClass)

        if itemClass in [1,3]:
            score2 += 0.14

        pvpScore = int(((score2-score1)*3000))
        scores.append(pvpScore)
        #print("pvpscore:",pvpScore)

    try:
        overallScore = int(sum(scores) / len(scores))
    except:
        overallScore = 0
    return overallScore"""


def getQualityColour(quality):
    if quality >= 200:
        return (255,255,255)
    elif quality >= 99:
        return (249, 59, 59) # 255,128,37
    elif quality >= 90:
        return (158,59,249)
    elif quality >= 70:
        return (6,129,234)
    elif quality >= 50:
        return (52,203,73)
    else:
        return (255,255,255)

def generateItemCard(items, args):
    title = ""
    for i in args:
        title += i + " "
    qualities = ["Common","Uncommon","Rare","Epic"]

    panelWidth = ceil(sqrt(len(items)))
    sheetWidth = (249*ceil(sqrt(len(items))))-5
    sheetHeight = (ceil(len(items) / panelWidth) * 229)-5
    sheetSize = (sheetWidth, sheetHeight)
    sheet = Image.new("RGB", sheetSize, (16, 19, 29))

    sheetx = []
    sheety = []
    startx = 0
    starty = 0
    for i in range(ceil(len(items)/panelWidth)):
        for x in range(panelWidth):
            sheety.append(starty)
            sheetx.append(startx)
            startx += 249
        starty += 229
        startx = 0

    if title != "":
        titlesheet = Image.new("RGB", (sheetWidth, sheetHeight + 150), (16, 19, 29))
        title_editable = ImageDraw.Draw(titlesheet)
        titlesize = 50
        titlefont = ImageFont.truetype('static/fonts/Quicksand-Bold.ttf', titlesize)
        while titlefont.getsize(title)[0] > 0.95*titlesheet.size[0]:
            titlesize -= 1
            titlefont = ImageFont.truetype('static/fonts/Quicksand-Bold.ttf', titlesize)
        title_editable.text((sheetWidth/2,35), title, (255,255,255), font=titlefont, anchor="mt")
        title_editable.rectangle([35,110,sheetWidth-35,110+3], fill=(255,255,255))

    for e in items:
        item = e[0]
        pvpScore = e[1]
        itemClass = e[2]
        baseColour = getQualityColour(item["quality"])
        itemSquare = Image.new("RGB", (238, 218), (16, 19, 29))
        itemSquare = ImageOps.expand(itemSquare, border=3, fill=baseColour)
        font = ImageFont.truetype('static/fonts/Quicksand-Bold.ttf', 20)
        image_editable = ImageDraw.Draw(itemSquare)


        if item["type"] == "itemSet":
            cube = Image.open("static/misc/cube5.png")
            cube.thumbnail((130,130))
            image_editable.text((10,10), item["ID"], baseColour, font=font)
            itemSquare.paste(cube, (65,60), cube)
            sheet.paste(itemSquare, (sheetx[items.index(e)],sheety[items.index(e)]))
        else:
            image_editable.text((10,10), item["name"], baseColour, font=font)
            width, height = image_editable.textsize(item["name"], font=font)
            if item["upgrade"] == 0:
                pass
            elif item["name"] == "Adventurer's Rucksack":
                image_editable.text((205,40), f'+{item["upgrade"]}', (245,194,71), font=font)
            else:
                image_editable.text((15+width,10), f'+{item["upgrade"]}', (245,194,71), font=font)

            font = ImageFont.truetype('static/fonts/Quicksand-Bold.ttf', 15)
            if item["quality"] >= 99:
                image_editable.text((10,15+height), f'Legendary {item["type"].capitalize()} {item["quality"]}%', (255,255,255), font=font)
            else:
                image_editable.text((10,15+height), f'{qualities[item["tier_quality"]]} {item["type"].capitalize()} {item["quality"]}%', (255,255,255), font=font)

            image_editable.text((10,15+height+23), f'GS: {item["gearscore"]}', (52,203,73), font=ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 13))
            gswidth, gsheight = image_editable.textsize(f'GS: {item["gearscore"]}', font=ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 13))

            IDxpos = 60
            if pvpScore > 0:
                cl = {
                    1 : "M",
                    2 : "A",
                    3 : "S"
                }
                image_editable.text((16+gswidth,15+height+23), f'{cl[itemClass]}GS: {pvpScore}', baseColour, font=ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 13))
                pvpwidth, pvpheight = image_editable.textsize(f'{cl[itemClass]}GS: {pvpScore}', font=ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 13))
                IDxpos = 23+gswidth+pvpwidth

            
            image_editable.text((IDxpos,15+height+23), f'ID: {item["ID"]}', (66,77,88), font=ImageFont.truetype('static/fonts/Quicksand-Medium.ttf', 13))
            idwidth, idheight = image_editable.textsize(f'ID: {item["ID"]}', font=ImageFont.truetype('static/fonts/Quicksand-Medium.ttf', 13))

            if item["bound"] == 2:
                image_editable.text((IDxpos + 13 + idwidth,15+height+23), 'CB', (52,203,73), font=ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 13))

            font = ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 17)
            x = 10
            if len(item["attr"]) > 6:
                y = 78
                font = ImageFont.truetype('static/fonts/Quicksand-SemiBold.ttf', 16)
            else:
                y = 90
            for stat in item["attr"]:
                name = item["attr"][stat]["attr_info"]["long"]
                value = item["attr"][stat]["value"]
                quality = ceil(item["attr"][stat]["quality"])
                colour = getQualityColour(quality)
                msg = ""
                if item["attr"][stat]["bonus"]:
                    msg += "+ "
                if item["attr"][stat]["attr_info"]["%"]:
                    msg += str(round(value, 1))
                    msg += "%"
                else:
                    msg += str(round(value))
                msg += " " + name
                if item["attr"][stat]["bonus"]:
                    msg += f' {quality:.0f}%'
                image_editable.text((x,y), msg, colour, font=font)
                y += 20
            if panelWidth == 1:
                if title == "":
                    return itemSquare
                    #return itemSquare.save("items/output.png")
                else:
                    titlesheet.paste(itemSquare, (0,150))
                    return titlesheet
                    #return titlesheet.save("items/output.png")
            else:
                sheet.paste(itemSquare, (sheetx[items.index(e)],sheety[items.index(e)]))
        
    if title == "":
        return sheet
        #sheet.save("items/output.png")
    else:
        titlesheet.paste(sheet, (0,150))
        return titlesheet
        #titlesheet.save("items/output.png")