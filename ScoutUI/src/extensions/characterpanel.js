class CharacterPanel {
    getMutationCondition(mutation) {
        return (
            mutation.target.className == "titleframe svelte-yjs4p5" &&
            mutation.previousSibling == null &&
            extensions["Settings"].getModSetting("Characterpanel")
        )
    }

    initialise(target) {
        this.modifying = false

        this.column1 = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div.grid.three.stats2 > div:nth-child(1)")
        this.column2 = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div.grid.three.stats2 > div:nth-child(2)")
        this.column3 = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div.grid.three.stats2 > div:nth-child(3)")
        
        if (!this.column1) {
            return
        }
        this.reorganiseStats()
        
        $(".statnumber").on("DOMSubtreeModified", () => {
            if (!this.modifying) {
                this.evalStats()
            }
        })
    }

    reorganiseStats() {
        this.column1 = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div.grid.three.stats2 > div:nth-child(1)")
        this.column2 = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div.grid.three.stats2 > div:nth-child(2)")
        this.column3 = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div.grid.three.stats2 > div:nth-child(3)")

        if (this.column1.childElementCount > 12) { return }

        //move
        this.createStat("Move Spd.", this.column3.querySelector("span:nth-child(2)").innerHTML, this.column1)
        this.createStat("Bag Slots", this.column3.querySelector("span:nth-child(4)").innerHTML, this.column2)

        //swap
        this.column3.querySelector("span:nth-child(7)").innerHTML = "PvP Level"
        this.column3.querySelector("span:nth-child(9)").innerHTML = "Gear Score"
        let temp = this.column3.querySelector("span:nth-child(8)").innerHTML
        this.column3.querySelector("span:nth-child(8)").innerHTML = this.column3.querySelector("span:nth-child(10)").innerHTML
        this.column3.querySelector("span:nth-child(10)").innerHTML = temp

        //delete
        this.column3.querySelector("span:nth-child(1)").remove()
        this.column3.querySelector("span:nth-child(1)").remove()
        this.column3.querySelector("span:nth-child(1)").remove()
        this.column3.querySelector("span:nth-child(1)").remove()

        //add
        let ehp = this.createStat("Effective HP", 0, null, true)
        let dps = this.createStat("DPS", 0, null, true)
        let burst = this.createStat("Burst", 0, null, true)
        this.createStat("Build Score", 0, this.column3, true)

        this.column3.prepend(burst[1])
        this.column3.prepend(burst[0])
        this.column3.prepend(dps[1])
        this.column3.prepend(dps[0])
        this.column3.prepend(ehp[1])
        this.column3.prepend(ehp[0])
        
        this.evalStats()

    }

    evalStats() {
        this.modifying = true

        let pclass = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled > div > div.slot > div:nth-child(1) > div:nth-child(1) > span:nth-child(6)").textContent
        let stats = {
            hp : parseInt(this.column1.querySelector("span:nth-child(2)").innerHTML),
            def : parseInt(this.column1.querySelector("span:nth-child(10)").innerHTML),
            block : parseFloat(this.column1.querySelector("span:nth-child(12)").innerHTML),
            min : parseInt(this.column2.querySelector("span:nth-child(2)").innerHTML),
            max : parseInt(this.column2.querySelector("span:nth-child(4)").innerHTML),
            crit : parseFloat(this.column2.querySelector("span:nth-child(8)").innerHTML),
            haste : parseFloat(this.column2.querySelector("span:nth-child(10)").innerHTML)
        }

        let defReduced = (1-Math.exp(-stats.def*0.0022))*0.87
        let defTaken = 1 - defReduced
        let blockReduced = (pclass == " Warrior") ? (stats.block/100)*0.6 : (stats.block/100)*0.45
        let blockTaken = 1 - blockReduced
        let totalTaken = defTaken*blockTaken
        let hpValue = 1/totalTaken
        let dmgRed = defReduced+blockReduced

        let ehp = stats.hp*hpValue
        let dps = ((stats.min+stats.max)/2)*(1+(stats.crit/100))*(1+(stats.haste/100))
        let burst = ((stats.min+stats.max)/2)*(1+(stats.crit/100))

        let DPS_Score, Tank_Score, Hybrid_Score, Overall_Score

        const log = (n, base) => Math.log(n) / Math.log(base);

        if (pclass == " Shaman") {
            DPS_Score = (log(dps,2) + log(burst,2)  + log(ehp,10))/3
            Tank_Score = (log(dps,10) + log(burst,11)  + log(ehp,2)  + log(hpValue*60,7)  + log(stats.haste*8,16))/5
            Hybrid_Score = (log(dps,3) + log(burst,4)  + log(ehp,6)  + log(hpValue*50,10)  + log(stats.haste*8,9))/5

            Overall_Score = ((DPS_Score/1.75) + Tank_Score + Hybrid_Score)*235/3
        } else if (pclass == " Archer") {
            DPS_Score = (log(dps,2) + log(burst,2))/2
            Tank_Score = (log(ehp,2.5) + log(dps,6) + log(burst,6))/3
            Hybrid_Score = (log(ehp,5) + log(dps,4) + log(burst,5))/3

            Overall_Score = ((DPS_Score/3) + Tank_Score + Hybrid_Score)*226/3
        } else if (pclass == " Mage") {
            DPS_Score = (log((dps + burst)/2,2))
            Tank_Score = (log(ehp,2.5) + log(dps,6) + log(burst,6))/3
            Hybrid_Score = (log(ehp,5) + log(dps,4) + log(burst,5))/3

            Overall_Score = ((DPS_Score/3) + Tank_Score + Hybrid_Score)*225/3
        } else if (pclass == " Warrior") {
            DPS_Score = (log(ehp,5) + log(dps,2) + log(burst,2))/3
            Tank_Score = (log(ehp,2) + log(dmgRed*100,2) + log(stats.haste,6))/3
            Hybrid_Score = (log(ehp,5) + log(dps,4) + log(burst,5) + log(dmgRed*100,5))/4

            Overall_Score = (DPS_Score + (Tank_Score/3) + Hybrid_Score)*210/3
        }

        this.column3.querySelector("span:nth-child(2)").innerHTML = Math.round(ehp)
        this.column3.querySelector("span:nth-child(4)").innerHTML = Math.round(dps)
        this.column3.querySelector("span:nth-child(6)").innerHTML = Math.round(burst)
        this.column3.querySelector("span:nth-child(14)").innerHTML = Math.round(Overall_Score)

        this.modifying = false
    }

    createStat(name, value, target, custom=false) {
        let stat = document.createElement("span")
        let number = document.createElement("span")
        stat.innerHTML = name
        number.innerHTML = value
        number.classList = "statnumber textprimary"

        if (custom) {
            stat.classList += " statcustom"
        }
        if (target != null) {
            target.appendChild(stat)
            target.appendChild(number)
        }
        
        return [stat, number]
    }
}
