from textwrap import indent
import requests
import json

kills = {}
dps = {}
hps = {}
mps = {}
deaths = {}

for i in range(8640): # 8640
    print(i+1)
    r = requests.post("https://hordes.io/api/pve/getbosskillplayerlogs", data=json.dumps({"sort" : "dps", "killid" : i+1}))

    killers = json.loads(r.text)

    for k in killers:
        player = k["name"]
        if player in kills:
            kills[player] += 1
            deaths[player] += k["deaths"]
            
            if k["dps"] > dps[player]:
                dps[player] = k["dps"]

            if k["hps"] > hps[player]:
                hps[player] = k["hps"]

            if k["mps"] > mps[player]:
                mps[player] = k["mps"]

        else:
            kills[k["name"]] = 1
            dps[k["name"]] = k["dps"]
            hps[k["name"]] = k["hps"]
            mps[k["name"]] = k["mps"]
            deaths[k["name"]] = k["deaths"]



kills = {k: v for k, v in sorted(kills.items(), reverse=True, key=lambda item: item[1])}
dps = {k: v for k, v in sorted(dps.items(), reverse=True, key=lambda item: item[1])}
hps = {k: v for k, v in sorted(hps.items(), reverse=True, key=lambda item: item[1])}
mps = {k: v for k, v in sorted(mps.items(), reverse=True, key=lambda item: item[1])}
deaths = {k: v for k, v in sorted(deaths.items(), reverse=True, key=lambda item: item[1])}

with open("bosskilldata/kills.json", "w") as f:
    json.dump(kills,f, indent=4, separators=(',', ': '))

with open("bosskilldata/dps.json", "w") as f:
    json.dump(dps,f, indent=4, separators=(',', ': '))

with open("bosskilldata/hps.json", "w") as f:
    json.dump(hps,f, indent=4, separators=(',', ': '))

with open("bosskilldata/mps.json", "w") as f:
    json.dump(mps,f, indent=4, separators=(',', ': '))

with open("bosskilldata/deaths.json", "w") as f:
    json.dump(deaths,f, indent=4, separators=(',', ': '))