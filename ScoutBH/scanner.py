import json
import requests
from pymongo import MongoClient
from func import decoder
from time import sleep
from collections import Counter

Decoder = decoder.APIDecoder()
cluster = MongoClient("", ssl=True, ssl_cert_reqs='CERT_NONE')
db = cluster["scout"]
collection = db["items"]

minimum_tiers = {
    "hammer" : 6,
    "bow" : 6,
    "staff" : 6,
    "sword" : 6,
    "armlet" : 3,
    "armor" : 3,
    "bag" : 0,
    "boot" : 3,
    "glove" : 3,
    "ring" : 1,
    "amulet" : 1,
    "quiver" : 3,
    "shield" : 3,
    "totem" : 3,
    "orb" : 3
}

good_tiers = {
    "hammer" : 7,
    "bow" : 7,
    "staff" : 7,
    "sword" : 7,
    "armlet" : 4,
    "armor" : 4,
    "bag" : 1,
    "boot" : 4,
    "glove" : 4,
    "ring" : 3,
    "amulet" : 3,
    "quiver" : 4,
    "shield" : 4,
    "totem" : 4,
    "orb" : 4
}


blood_table = {
    "staff" : "int",
    "hammer" : "wis",
    "sword" : "str",
    "bow" : "dex"
}

gen_desireable = [
    ["int","sta","def"],
    ["int","sta","min"],
    ["int","sta","max"],
    ["int","sta","has"],
    ["int","sta","cri"],
    ["int","sta","blo"],

    ["int","def","min"],
    ["int","def","max"],
    ["int","def","has"],
    ["int","def","cri"],
    ["int","def","blo"],

    ["int","min","max"],
    ["int","min","has"],
    ["int","min","cri"],
    ["int","min","blo"],

    ["int","max","has"],
    ["int","max","cri"],
    ["int","max","blo"],

    ["int","has","cri"],
    ["int","has","blo"],

    ["int","cri","blo"],

    ####################
    ["wis","sta","def"],
    ["wis","sta","min"],
    ["wis","sta","max"],
    ["wis","sta","has"],
    ["wis","sta","cri"],
    ["wis","sta","blo"],

    ["wis","def","min"],
    ["wis","def","max"],
    ["wis","def","has"],
    ["wis","def","cri"],
    ["wis","def","blo"],

    ["wis","min","max"],
    ["wis","min","has"],
    ["wis","min","cri"],
    ["wis","min","blo"],

    ["wis","max","has"],
    ["wis","max","cri"],
    ["wis","max","blo"],

    ["wis","has","cri"],
    ["wis","has","blo"],

    ["wis","cri","blo"],

    ####################
    ["dex","sta","def"],
    ["dex","sta","min"],
    ["dex","sta","max"],
    ["dex","sta","has"],
    ["dex","sta","cri"],
    ["dex","sta","blo"],

    ["dex","def","min"],
    ["dex","def","max"],
    ["dex","def","has"],
    ["dex","def","cri"],
    ["dex","def","blo"],

    ["dex","min","max"],
    ["dex","min","has"],
    ["dex","min","cri"],
    ["dex","min","blo"],

    ["dex","max","has"],
    ["dex","max","cri"],
    ["dex","max","blo"],

    ["dex","has","cri"],
    ["dex","has","blo"],

    ["dex","cri","blo"],

    ####################
    ["str","sta","def"],
    ["str","sta","min"],
    ["str","sta","max"],
    ["str","sta","has"],
    ["str","sta","cri"],
    ["str","sta","blo"],

    ["str","def","min"],
    ["str","def","max"],
    ["str","def","has"],
    ["str","def","cri"],
    ["str","def","blo"],

    ["str","min","max"],
    ["str","min","has"],
    ["str","min","cri"],
    ["str","min","blo"],

    ["str","max","has"],
    ["str","max","cri"],
    ["str","max","blo"],

    ["str","has","cri"],
    ["str","has","blo"],

    ["str","cri","blo"],

    ####################
    ["sta","def","blo"],
    ["sta","def","has"],
    ["sta","def","cri"],
    ["sta","blo","has"],
    ["sta","blo","cri"],
    ["sta","has","cri"],

    ["def","blo","has"],
    ["def","blo","cri"],
    ["def","has","cri"],

    ["blo","cri","has"],

    ####################
    ["dex","if","luc"],
    ["dex","if","has"],
    ["dex","if","cri"],

    ["wis","if","luc"],
    ["wis","if","has"],
    ["wis","if","cri"],

    ["int","if","luc"],
    ["int","if","has"],
    ["int","if","cri"],

    ["str","if","luc"],
    ["str","if","has"],
    ["str","if","cri"],

]

gen2_desireable = [
    ["sta","def","blo"],
    ["sta","def","has"],
    ["sta","def","cri"],
    ["sta","blo","has"],
    ["sta","blo","cri"],
    ["sta","has","cri"],

    ["def","blo","has"],
    ["def","blo","cri"],
    ["def","has","cri"],

    ["blo","cri","has"]
]

archer_desireable = [
    ["dex","sta","def"],
    ["dex","sta","min"],
    ["dex","sta","max"],
    ["dex","sta","has"],
    ["dex","sta","cri"],
    ["dex","sta","blo"],

    ["dex","def","min"],
    ["dex","def","max"],
    ["dex","def","has"],
    ["dex","def","cri"],
    ["dex","def","blo"],

    ["dex","min","max"],
    ["dex","min","has"],
    ["dex","min","cri"],
    ["dex","min","blo"],

    ["dex","max","has"],
    ["dex","max","cri"],
    ["dex","max","blo"],

    ["dex","has","cri"],
    ["dex","has","blo"],

    ["dex","cri","blo"],

    ["dex","if","luc"],
    ["dex","if","has"],
    ["dex","if","cri"],
]

mage_desireable = [
    ["int","sta","def"],
    ["int","sta","min"],
    ["int","sta","max"],
    ["int","sta","has"],
    ["int","sta","cri"],
    ["int","sta","blo"],

    ["int","def","min"],
    ["int","def","max"],
    ["int","def","has"],
    ["int","def","cri"],
    ["int","def","blo"],

    ["int","min","max"],
    ["int","min","has"],
    ["int","min","cri"],
    ["int","min","blo"],

    ["int","max","has"],
    ["int","max","cri"],
    ["int","max","blo"],

    ["int","has","cri"],
    ["int","has","blo"],

    ["int","cri","blo"],

    ["int","if","luc"],
    ["int","if","has"],
    ["int","if","cri"],
]

shaman_desireable = [
    ["wis","sta","def"],
    ["wis","sta","min"],
    ["wis","sta","max"],
    ["wis","sta","has"],
    ["wis","sta","cri"],
    ["wis","sta","blo"],

    ["wis","def","min"],
    ["wis","def","max"],
    ["wis","def","has"],
    ["wis","def","cri"],
    ["wis","def","blo"],

    ["wis","min","max"],
    ["wis","min","has"],
    ["wis","min","cri"],
    ["wis","min","blo"],

    ["wis","max","has"],
    ["wis","max","cri"],
    ["wis","max","blo"],

    ["wis","has","cri"],
    ["wis","has","blo"],

    ["wis","cri","blo"],

    ["sta","def","blo"],
    ["sta","def","has"],
    ["sta","def","cri"],
    ["sta","blo","has"],
    ["sta","blo","cri"],
    ["sta","has","cri"],

    ["def","blo","has"],
    ["def","blo","cri"],
    ["def","has","cri"],

    ["blo","cri","has"],

    ["wis","if","luc"],
    ["wis","if","has"],
    ["wis","if","cri"],
]

warrior_desireable = [
    ["str","sta","def"],
    ["str","sta","min"],
    ["str","sta","max"],
    ["str","sta","has"],
    ["str","sta","cri"],
    ["str","sta","blo"],

    ["str","def","min"],
    ["str","def","max"],
    ["str","def","has"],
    ["str","def","cri"],
    ["str","def","blo"],

    ["str","min","max"],
    ["str","min","has"],
    ["str","min","cri"],
    ["str","min","blo"],

    ["str","max","has"],
    ["str","max","cri"],
    ["str","max","blo"],

    ["str","has","cri"],
    ["str","has","blo"],

    ["str","cri","blo"],

    ["sta","def","blo"],
    ["sta","def","has"],
    ["sta","def","cri"],
    ["sta","blo","has"],
    ["sta","blo","cri"],
    ["sta","has","cri"],

    ["def","blo","has"],
    ["def","blo","cri"],
    ["def","has","cri"],

    ["blo","cri","has"],
    ["blo","max","has"],
    ["blo","min","has"],

    ["str","has","if"],
    ["str","if","luc"],
    ["str","if","cri"],
]

orb_desireable = [
    ["min","max","cri"],
    ["min","max","has"],
    ["min","max","sta"],
    ["min","max","def"],
    ["min","cri","has"],
    ["max","cri","has"],


    ["sta","def","blo"],
    ["sta","def","cri"],
    ["sta","def","min"],
    ["sta","def","max"],
    ["sta","def","has"],

    ["sta","blo","has"],
    ["sta","blo","cri"],

    ["sta","cri","has"],
    ["sta","cri","min"],
    ["sta","cri","max"],

    ["sta","has","min"],
    ["sta","has","max"],


    ["def","min","has"],
    ["def","min","cri"],
    ["def","max","has"],
    ["def","max","cri"],

    ["def","blo","has"],
    ["def","blo","cri"],

    ["def","cri","has"],
    ["def","cri","min"],
    ["def","cri","max"],

    ["def","has","min"],
    ["def","has","max"]
]

type_table = {
    "staff" : mage_desireable,
    "orb" : mage_desireable,
    "bow" : archer_desireable,
    "quiver" : archer_desireable,
    "hammer" : shaman_desireable,
    "totem" : shaman_desireable,
    "sword" : warrior_desireable,
    "shield" : warrior_desireable,
}

def find_common(a,b):
    common = 0
    for i in a:
        if i in b:
            common += 1
    return common

startID = 150000001
endID = 0
url = 'https://hordes.io/api/item/get'
cookies = {"sid":''}

rang = 150
checkpoints = [endID+((x+1)*1000000) for x in range(150)]
empty = 0
itemsRaw = []
count = 0
itemsChecked = 0
items = []
goodcount = 0
while startID > endID:
    try:
        gooditems = []
        itemsFound = 0
        itemsToCheck = []
        x = []
        for i in range(rang):
            x.append(startID - i - 1)

        data = {"ids":x}    
        r = requests.post(url, data=json.dumps(data),cookies=cookies)
        itemsRaw = json.loads(r.text)

        count += 1
        itemsFound += len(itemsRaw)
        if len(itemsRaw) > 0:
            empty = 0
            for i in itemsRaw:
                itemsToCheck.append(i)
        else:
            empty += 1  

        for cp in checkpoints:
            if startID < cp:
                print(f"reached {cp}")
                checkpoints.remove(cp)
                break

        if itemsFound > 0:

            for itemRaw in itemsToCheck:
                item = Decoder.decode(itemRaw)


                if "if" in item['bonus_attr_keys'] and "luc" in item['bonus_attr_keys'] and item["tier"] >= good_tiers[item["type"]]:
                    ifquality = item["attr"]["if"]["quality"]
                    luckquality = item["attr"]["luc"]["quality"]

                    if (ifquality + luckquality)/2 >= 65:
                        gooditems.append(item)
                        continue

                if (len(item['bonus_attr_keys']) >= 3 and item["tier"] >= minimum_tiers[item["type"]]) or len(item['bonus_attr_keys']) == 4:
                    #items.append(item)

                    if len(item["bonus_attr_keys"]) == 4:
                        gooditems.append(item)

                    else:
                        if item["tier"] >= good_tiers[item["type"]]:

                            if item["type"] in ["staff","sword","hammer","bow"] and item["quality"] >= 90 and item["tier"] > minimum_tiers[item["type"]]:
                                check1 = blood_table[item["type"]] in item["bonus_attr_keys"]
                                check2 = False
                                for s in gen2_desireable:
                                    if find_common(item["bonus_attr_keys"], s) == 2:
                                        check2 = True
                                        break

                                if check1 or check2:
                                    gooditems.append(item)
                                    continue


                            

                            if item["type"] == "orb":
                                for combo in orb_desireable:
                                    if Counter(combo) == Counter(item['bonus_attr_keys']):
                                        gooditems.append(item)
                            else:
                                if item["type"] in type_table.keys():
                                    toCheck = type_table[item["type"]]
                                else:
                                    toCheck = gen_desireable

                                found = False

                                for combo in toCheck:      
                                    if Counter(combo) == Counter(item['bonus_attr_keys']):
                                        gooditems.append(item)
                                        break

                                    if item["type"] in ["staff","sword","hammer","bow"] and blood_table[item["type"]] in item["bonus_attr_keys"]:
                                        
                                        for roll in [y for y in item["bonus_attr_keys"] if y!=blood_table[item["type"]]]:
                                            if roll in combo:
                                                gooditems.append(item)
                                                found = True
                                                break

                                        if found:
                                            break

        for itemg in gooditems:
            goodcount += 1

            x = {
                "_id" : itemg["ID"]
            }

            y = {
                "type" : itemg['type'],
                "tier" : itemg['tier'],
                "quality" : itemg["quality"],
                "gearscore" : itemg["gearscore"],
                "name" : itemg["name"],
                "base_stats" : {},
                "bonus_stats" : {},
                "bonus_stats_keys" : itemg["bonus_attr_keys"]
            }

            for st in itemg["attr"]:
                if itemg["attr"][st]["bonus"]:
                    y["bonus_stats"][st] = {
                        "value" : itemg["attr"][st]["value"],
                        "quality" : itemg["attr"][st]["quality"]
                    }
                else:
                    y["base_stats"][st] = {
                        "value" : itemg["attr"][st]["value"],
                        "quality" : itemg["attr"][st]["quality"]
                    }

            collection.update_one(x, {"$set" : y}, upsert=True)
            #print(f"updated {itemg['ID']}\n{itemg['bonus_attr_keys']}")

        startID  -= rang
        itemsChecked += rang
    except Exception as e:
        print(e)
        sleep(15)



print(
f"""
checked : {itemsChecked}
found : {goodcount}
"""
)
