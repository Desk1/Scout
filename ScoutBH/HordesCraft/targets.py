from math import exp
class dummy:
    def __init__(self):
        self.health = 749900
        self.defense = 133 # 132
        self.mitigation = 1-((1-exp(-self.defense*0.0022))*0.87)
        self.dmgMultiplier = 1
        self.debuffs = {
            "iceboltCharge" : 0,
            "frozen" : False,
        }
        self.dots = {}
        self.chillingDot = None
        self.poisonDot = 0 # stacks
        self.name = "Training dummy Lv.40 (faivel)"

    def freeze(self):
        self.debuffs["frozen"] = True
        self.debuffs["iceboltCharge"] = 0
        self.dmgMultiplier *= 1.5

    def unfreeze(self):
        self.debuffs["frozen"] = False
        self.dmgMultiplier /= 1.5

