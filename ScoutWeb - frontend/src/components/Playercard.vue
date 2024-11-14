<script>
import decode from "../hordes/itemdecode.js"
import playerstats from "../hordes/playerstats.js"
import Item from "./Item.vue"

export default {
    props: ["charinfo","direction","idx"],
    components: {Item},
    data() {
        return {
            charstats: undefined,
            done: false,
            itemshow: {
                "weapon" : false,
                "armlet" : false,
                "armor" : false,
                "bag" : false,
                "boot" : false,
                "glove" : false,
                "ring" : false,
                "amulet" : false,
                "offhand" : false

            }
        }
    },
    mounted() {
        if (this.charinfo) {
            try {
                this.createcard()
            }
            catch(err) {
                console.log(err)
                this.remove()
            }
        }
    },
    watch: {
        charinfo() {
            if (this.charinfo) {
                try {
                    this.createcard()
                }
                catch(err) {
                    console.log(err)
                    this.remove()
                }
            }
        }
    },
    methods: {
        getColour(e,i,col) {
            if (e.length > 2) {
                return {
                    "color" : "#d1d1d1",
                    "font size" : "1em"
                }
            }
            switch(e) {
                case "SS":
                    var colour = "rgb(198,70,160)"
                    break
                case "S":
                    var colour = "rgb(159,70,198)"
                    break
                case "A+":
                    var colour = "rgb(90,70,198)"
                    break
                case "A":
                    var colour = "rgb(70,123,198)"
                    break
                case "A-":
                    var colour = "rgb(70,192,198)"
                    break
                case "B+":
                    var colour = "rgb(70,198,149)"
                    break
                case "B":
                    var colour = "rgb(70,198,97)"
                    break
                case "B-":
                    var colour = "rgb(129,198,70)"
                    break
                case "C+":
                    var colour = "rgb(184,198,70)"
                    break
                case "C":
                    var colour = "rgb(198,186,70)"
                    break
                case "C-":
                    var colour = "rgb(198,147,70)"
                    break
                case "D+":
                    var colour = "rgb(198,117,70)"
                    break
                case "D":
                    var colour = "rgb(198,100,70)"
                    break
                case "D-":
                    var colour = "rgb(198,87,70)"
                    break
                case "E":
                    var colour = "rgb(185,21,21)"
                    break
                case "F":
                    var colour = "rgb(116,0,0)"
                    break
            }

            switch(i) {
                case 0:
                    var colour = "-webkit-linear-gradient(left, rgb(198, 255, 221), rgb(251, 215, 134), rgb(247, 121, 125))"
                    break
                case 1:
                    var colour = "-webkit-linear-gradient(left,rgb(0, 195, 255), rgb(255, 255, 28))"
                    break
                case 2:
                    var colour = "-webkit-linear-gradient(left,rgb(18, 194, 233), rgb(196, 113, 237), rgb(246, 79, 89))"
                    break
                case 3:
                    var colour = "-webkit-linear-gradient(left,rgb(239, 50, 217), rgb(137, 255, 253))"
                    break
                case 4:
                    var colour = "-webkit-linear-gradient(left,rgb(255, 0, 204), rgb(51, 51, 153))"
                    break
            }

            return {
                "background" : colour,
                "-webkit-background-clip": "text",
                "-webkit-text-fill-color": "transparent",
                "width": "fit-content",
                "font weight": "bold"
            }
        },
        remove() {
            this.$emit("remove", this.idx)
        },
        extrainfostyle() {
            if (!this.direction) {
                return
            }
            return this.direction == "right" ? "display: grid; grid-template-columns: 1fr 4fr; align-items: center;" : "display: grid; grid-template-columns: 4fr 1fr; align-items: center;"
        },
        getextrainfo() {
            let s = "ITEMS\n\n"
            let order = ["weapon","armlet","armor","bag","boot","glove","ring","amulet","offhand"]

            order.forEach(t => {
                if (this.charinfo.itemsparsed[t]) {
                    s += `${this.charinfo.itemsparsed[t].type}: ${this.charinfo.itemsparsed[t].ID} +${this.charinfo.itemsparsed[t].upgrade}\n`
                }
            })

            s += "\n\nBUILDSCORE\n\n"
            s += this.charinfo.buildscore
            return s
        },
        createcard() {
            let items = {}
            let itemsdecoded = []

            let charmids = ["Little Bell", "Hardened Egg","Tattooed Skull","Ship Pennant","Blue Marble"]

            let args = this.charinfo.args
            if (!args.charms.length) {
                args.charms = ["Tattooed Skull","Hardened Egg"] 
            }

            if (!this.charinfo["items"]["fail"]) {
                this.charinfo["items"].forEach(i => {
                let item = decode(i, { maxupgrade: args.maxupgrade })
                itemsdecoded.push(item)

                if (["sword","staff","bow","hammer"].includes(item["type"].toLowerCase())) {
                    items["weapon"] = item
                } else if (["shield","orb","quiver","totem"].includes(item["type"].toLowerCase())) {
                    items["offhand"] = item
                } else {
                    items[item["type"]] = item
                }

            })
            }
            console.log(this.charinfo)
            var stats = playerstats(args, this.charinfo, itemsdecoded, this.charinfo["tierlist"])
            
            this.charinfo.stats = stats
            this.charinfo.tierlistparsed = stats.tierlist
            this.charinfo.itemsparsed = items
            let cid = [] 
            stats.charms.forEach(c => {
                cid.push(String(charmids.indexOf(c)))
            })
            this.charinfo.buildscore = stats.stats.evaluated.buildscore.toFixed(6)
            this.charstats = {
                player: {
                    name: this.charinfo.name,
                    level: this.charinfo.level.toFixed(),
                    class: this.charinfo.pclass==0 ? "Warrior" : this.charinfo.pclass==1 ? "Mage" : this.charinfo.pclass==2 ? "Archer" : "Shaman",
                    faction: this.charinfo.faction==0 ? "Vanguard" : "Bloodlust",
                    prestige: this.charinfo.prestige.toFixed() + " / " + Math.min(Math.ceil(this.charinfo.prestige/4000)*4, 48).toFixed(1) + "k (Rank " + Math.min(Math.floor(this.charinfo.prestige/4000), 12).toFixed() + "/12)",
                    rating: this.charinfo.elo.toFixed(),
                    rank: this.charinfo.tierlistparsed.rank=="SS" ? "#"+this.charinfo.tierlistparsed.position.toFixed()+" "+this.charinfo.tierlistparsed.rank : this.charinfo.tierlistparsed.rank
                },
                buffs: stats.buffs,
                charms: cid,
                tierlist: stats.tierlist,
                allocated: stats.stats.allocated,
                block1: {
                    "HP": stats.stats.real.hp.toFixed(),
                    "HP Reg./5s": stats.stats.real.hpr.toFixed(1),
                    "MP": stats.stats.real.mp.toFixed(1),
                    "MP Reg./5s": stats.stats.real.mpr.toFixed(1),
                    "Defense": stats.stats.real.def.toFixed(),
                    "Block": stats.stats.real.blo.toFixed(1)+"%"
                },
                block2: {
                    "Min Dmg.": stats.stats.real.min.toFixed(),
                    "Max Dmg.": stats.stats.real.max.toFixed(),
                    "Attack Spd.": stats.stats.real.att.toFixed(),
                    "Critical": stats.stats.real.cri.toFixed(1)+"%",
                    "Haste": stats.stats.real.has.toFixed(1)+"%"
                },
                block3: {
                    "Effective HP": stats.stats.evaluated.eHp.toFixed(),
                    "DPS": stats.stats.evaluated.DPS.toFixed(),
                    "Burst": stats.stats.evaluated.Burst.toFixed(),
                    "Item Find": stats.stats.real.if.toFixed()+"%",
                    "Gear Score": stats.stats.real.gs.toFixed(),
                    "Build Score": stats.stats.evaluated.buildscore.toFixed()
                }
            }
            this.done = true
            this.$emit("done")
            console.log(Object.values(this.charinfo.itemsparsed))
        }
    }
}
</script>

<template>
    <div :style="extrainfostyle()">
        <div class="sidepanel" v-if="direction == 'left' && done">
            <div id="removebtn" class="btn" @click="$emit('remove', idx)">remove</div>
            <textarea :value="getextrainfo()" id="extrainfo"></textarea>
        </div>
        <div v-if="charstats" class="bgoverlay">
            <div class="window panel-black">
                <div class="titleframe">
                    <img src="/icons/char.svg" class="titleicon svgicon">
                    <div class="textprimary title">
                        <div class="title" name="title">Character</div>
                    </div>
                    <div v-for="l, buff in charstats.buffs" style="position: relative;">
                        <img style="width: 25px;" :src="`/icons/buffs/${buff}.jpg`"/>
                        <div class="bufftext">{{l}}</div>
                    </div>
                </div>
                <div class="slot">
                    <div class="grid" style="grid-template-columns: 3fr 2fr;">
                        <div class="statcol panel-black" style="grid-template-columns: 1fr 2fr;">
                            <span>Name</span>
                            <span class="bold textwhite">{{this.charstats.player.name}}</span>
                            <span>Level</span>
                            <span class="bold textwhite">{{this.charstats.player.level}}</span>
                            <span>Class</span>
                            <span :class="`bold textc${this.charinfo.pclass}`">
                                <img class="texticon" :src='"/icons/classes/" + this.charinfo.pclass.toFixed() + ".webp"'>
                                {{this.charstats.player.class}}
                            </span>
                            <span>Faction</span>
                            <span :class="`bold textf${this.charinfo.faction}`">
                                <img class="texticon" :src="`/icons/factions/${this.charinfo.faction}.webp`">
                                Bloodlust
                            </span>
                            <span>Prestige</span>
                            <span class="bold textprestige">
                                <img class="texticon" src="/icons/currency/prestige.svg">
                                {{this.charstats.player.prestige}}
                            </span>
                            <span>Rating</span>
                            <span>
                                <span class="bold textpvp">
                                    <img class="svgicon" :src="`/icons/elo/${this.charinfo.elo<1600 ? 0 : this.charinfo.elo<1800 ? 1 : this.charinfo.elo<2000 ? 2 : this.charinfo.elo<2200 ? 3 : 4}.svg`">
                                    {{this.charstats.player.rating}}
                                </span>
                            </span>
                            <span class="scout">Rank</span>
                            <span :style="getColour(this.charinfo.tierlistparsed.rank, this.charinfo.tierlistparsed.position-1, 1)">
                                {{this.charstats.player.rank}}
                            </span>
                        </div>
                        <div id="statpoints" class="statcol panel-black " style="grid-template-columns: 1fr auto auto;">
                            <span>Strength</span>
                            <span class="statnumber textgreen">{{this.charstats.allocated.str}}</span>
                            <img src="/icons/arrow.svg" class="btn disabled svgicon statbtn ">
                            <span>Stamina</span>
                            <span class="statnumber textgreen">{{this.charstats.allocated.sta}}</span>
                            <img src="/icons/arrow.svg" class="btn disabled svgicon statbtn ">
                            <span>Dexterity</span>
                            <span class="statnumber textgreen">{{this.charstats.allocated.dex}}</span>
                            <img src="/icons/arrow.svg" class="btn disabled svgicon statbtn ">
                            <span>Intelligence</span>
                            <span class="statnumber textgreen">{{this.charstats.allocated.int}}</span>
                            <img src="/icons/arrow.svg" class="btn disabled svgicon statbtn ">
                            <span>Wisdom</span>
                            <span class="statnumber textgreen">{{this.charstats.allocated.wis}}</span>
                            <img src="/icons/arrow.svg" class="btn disabled svgicon statbtn ">
                            <span>Luck</span><span class="statnumber textgreen">{{this.charstats.allocated.luc}}</span>
                            <img src="/icons/arrow.svg" class="btn disabled svgicon statbtn ">
                            <span>Stat Points</span>
                            <span class="statnumber textgreen">0</span>
                        </div>
                    </div>
                    <div id="equipslots" class="items ">
                        <div v-for="(item) in ['weapon','armlet','armor','bag','boot','glove','ring','amulet','offhand']" id="" :class="`border ${!this.charinfo.itemsparsed[item] ? 'grey' : this.charinfo.itemsparsed[item]['tier_quality']==0 ? 'white' : this.charinfo.itemsparsed[item]['tier_quality']==1 ? 'green' : this.charinfo.itemsparsed[item]['tier_quality']==2 ? 'blue' : 'purple'} slot filled`">
                            <div v-if="this.charinfo.itemsparsed[item]" @mouseover="this.charinfo.itemsparsed[item].show = true" @mouseleave="this.charinfo.itemsparsed[item].show = false">
                                <Item :itemInfo="[charinfo.itemsparsed[item]]" class="item" v-show="this.charinfo.itemsparsed[item].show"/>
                                <span v-if="this.charinfo.itemsparsed[item].upgrade > 0" class="slottext">+{{this.charinfo.itemsparsed[item].upgrade}}</span>
                                <img class="icon " :src="`https://hordes.io/assets/items/${this.charinfo.itemsparsed[item].type}/${this.charinfo.itemsparsed[item].type}${this.charinfo.itemsparsed[item].tier}_q${this.charinfo.itemsparsed[item]['tier_quality']}.webp`">
                            </div>
                            <div v-else>
                                <img class="icon " :src="`/icons/slotbg/${item}.webp`"/>
                            </div>
                        </div>
                        <div v-for="(charm) in this.charstats.charms" id="" :class="`border ${charm ? 'purple' : 'grey'} slot filled`">
                            <img class="icon " :src="charm ? `https://hordes.io/assets/items/charm/charm${charm}_q3.webp` : '/icons/slotbg/charm.webp'">
                        </div>
                    </div>
                    <div class="grid three stats2 ">
                        <div class="statcol panel-black ">
                            <template v-for="(value, stat) in this.charstats.block1">
                                <span>{{stat}}</span>
                                <span class="statnumber textprimary">{{value}}</span>
                            </template>
                        </div>
                        <div class="statcol panel-black ">
                            <template v-for="(value, stat) in this.charstats.block2">
                                <span>{{stat}}</span>
                                <span class="statnumber textprimary">{{value}}</span>
                            </template>
                        </div>
                        <div class="statcol panel-black ">
                            <template v-for="(value, stat) in this.charstats.block3">
                                <span :class="`${['Item Find','Gear Score'].includes(stat) ? '' : 'scout'}`">{{stat}}</span>
                                <span class="statnumber textprimary">{{value}}</span>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="sidepanel" v-if="direction == 'right' && done">
            <div id="removebtn" class="btn" @click="remove">remove</div>
            <textarea :value="getextrainfo()" id="extrainfo"></textarea>
        </div>
    </div>
</template>

<style>
.window {
    padding: 5px;
    display: grid;
    grid-template-rows: 30px 1fr;
    grid-gap: 4px;
    transform-origin: inherit;
    min-width: fit-content;
    text-align: left;
    width: max-content;
    height: max-content;
    font-size: 15px;
    font-family: "hordes", sans-serif;
    line-height: normal;
    letter-spacing: normal;
}

.sidepanel {
    display: flex;
    flex-direction: column;
    align-items: center;
}

#extrainfo {
    height: 260px;
    width: 190px;
    resize: none;
    background: #1f2020;
    color: #27bd90;
    border: none;
    text-align: left;
    outline: none;
    border: 4px;
}

#removebtn {
    width: 100px;
    height: 25px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}
#removebtn:hover {
    background-color: #dd3b35;
}

.bgoverlay {
    background-image: url("@/assets/panelbg.png");
    border-radius: 4px;
    justify-self: center;
    width: fit-content;
    height: 341px;
}

.item {
    position: absolute;
    transform: translateY(-250px);
}

.panel-black {
    background-color: rgba(16, 19, 29, 0.8);
    color: #a6dcd5;
    border-radius: 3px;
    pointer-events: all;
    padding: 4px;
}

.titleframe {
    line-height: 1em;
    display: flex;
    align-items: center;
    position: relative;
    letter-spacing: 0.5px;
}

.statcol {
    display: grid;
    grid-template-columns: auto auto;
    align-content: start;
    column-gap: 3px;
    align-items: center
}

.slot {
    position: relative;
}

.bufftext {
    background-color: rgba(16, 19, 29, 0.8);
    position: absolute;
    color: #DAE8EA;
    right: 0;
    bottom: 3px;
    line-height: 8px;
    font-size: 13px;
    padding: 2px 1px 3px 1px;
    border-radius: 2px;
    z-index: 10;
    font-weight: bold;
}

.slottext {
    color: #DAE8EA;
    right: 3px;
    bottom: 3px;
    pointer-events: none;
    position: absolute;
    line-height: 8px;
    font-size: 13px;
    background-color: rgba(16, 19, 29, 0.8);
    padding: 2px 1px 3px 1px;
    border-radius: 2px;
    z-index: 10;
    font-weight: bold;
}

.btn {
    padding: 3px;
    cursor: pointer;
    border: 3px solid rgba(0, 0, 0, 0);
    color: #DAE8EA;
    transition: background-color 0.15s, color 0.15s, border 0.15s;
    font-weight: bold;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden
}

.btn.black {
    background-color: rgba(16, 19, 29, 0.8)
}

.statbtn {
    opacity: 0.5;
    background-color: #5b858e;
    pointer-events: all;
    border: unset !important;
    color: #364c56;
    border: 3px solid #364c56;
    cursor: auto;
    pointer-events: none;
}

.items {
    display: grid;
    grid-gap: 4px;
    max-width: 575px;
    grid-auto-rows: 46px;
    grid-template-columns: repeat(11, 46px);
    margin: 4px 0
}

.svgicon {
    height: 1.15em;
    vertical-align: -0.2em;
    padding: 0
}

.title {
    width: 90px;
    padding-left: 4px;
    font-weight: bold;
}

.titleicon {
    margin: 3px
}

.texticon {
    height: 1em;
    vertical-align: -0.23em
}

.texticon:not(:last-child) {
    padding-right: 0.15em
}

.grid {
    display: grid;
    grid-gap: 4px
}

.grid.three {
    grid-template-columns: 1fr 1fr 1fr
}

.stats2 {
    font-size: 13px
}

.border {
    border-radius: 3px
}

.border.grey {
    border: 3px solid #293c40
}

.border.white {
    border: 3px solid #5b858e
}

.border.white.glow {
    box-shadow: inset 0 0 0px 3px #323232, inset 0 0 6px 7px #354e53
}

.border.green {
    border: 3px solid #34CB49
}

.border.green.glow {
    box-shadow: inset 0 0 0px 3px #162818, inset 0 0 6px 7px #185d22
}

.border.blue {
    border: 3px solid #0681EA
}

.border.blue.glow {
    box-shadow: inset 0 0 0px 3px #0d283f, inset 0 0 6px 7px #034278
}

.border.purple {
    border: 3px solid #9E3BF9
}
.statnumber {
    font-weight: bold;
    justify-self: end
}

.bold {
    font-weight: bold
}

.textprimary {
    color: #F5C247
}

.textwhite {
    color: #DAE8EA
}

.textc0 {
    color: #C7966F
}

.textc1 {
    color: #21A9E1
}

.textc2 {
    color: #98CE64
}

.textc3 {
    color: #4f78ff
}

.textprestige {
    color: #eab379
}

.textpvp {
    color: #EA00FF
}

.textf0 {
    color: #458BD9
}

.textf1 {
    color: #C32929
}

.textgold {
    color: #FBD08D
}

.textgreen {
    color: #34CB49
}

.scout {
    color: #5ffdca
}
</style>