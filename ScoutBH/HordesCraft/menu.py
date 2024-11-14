from archer import archerSim
from mage import mageSim
from multiprocessing import Process
from time import time
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#MAGE
"""
stats = {
    "min" : 98,
    "max" : 98,
    "crit" : 42.6,
    "haste" : 17.4,
    "atkspeed" : 10
}
skills = {
    "icebolt" : 5,
    "iceorb" : 4,
    "hypothermic frenzy" : 5,
    "chilling radiance" : 5,
    "enchantment" : 4,
    "arctic aura" : 4
}
"""
#ARCHER
stats = {
    "min" : 88,
    "max" : 88,
    "crit" : 28.8,
    "haste" : 17.8,
    "atkspeed" : 10
}
skills = {
    "swift shot" : 5,
    "precise shot" : 5,
    "poison arrows" : 5,
    "invigorate" : 5,
    "dash" : 1,
    "temporal dilation" : 3,
    "cranial punctures" : 0
}
x = "archer"

#APL = ["arctic IFnobuff:arctic","orb IFtarget:frozen","hypo IFcooldown:orb","chilling IFcooldown:hypo","bolt"]
APL = ["skull","invigorate","dash IFcooldown:precise","precise","swift"]

fightTime = 120
simulations = 100
interval = 50

processes = []
results = {
    "archer" : []
}
data = {
    "Time" : [],
    "DPS" : [],
    "Sim" : [],
}
startTime = time()

if x == "mage":
    for i in range(simulations):
        mageSim(fightTime, stats, skills, APL, results, interval, data, "dmg/crit/haste glass build")
            
elif x == "archer":
    for i in range(simulations):
        archerSim(fightTime, stats, skills, APL, results, interval, data, "archer")

  
avgDPS = sum(results["archer"])/len(results["archer"])
minDPS = min(results["archer"])
maxDPS = max(results["archer"])
endTime = time()

print(f"""
Avg. DPS: {avgDPS}
Max DPS: {maxDPS}
Min DPS: {minDPS}
Fight Length: {fightTime} seconds
Simulations ran: {simulations}
Simulation interval: {interval} ms
Time taken: {endTime-startTime:.5f} seconds
""")


"""
df = pd.DataFrame(data)

palette = sns.color_palette("mako_r", 1)
sns.set_theme()
sns.lineplot(data=df, x=df["Time"], y=df["DPS"], palette=palette, hue=df["Sim"], ci="sd").set(title=f' DPS | Target: Training dummy Lv.40 (faivel)')

plt.show()
"""