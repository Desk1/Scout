<script>
import axios from 'axios';
import Playercard from "../components/Playercard.vue";

export default {
    data() {
        return {
            search_terms: [],
            search_result: [],
            search_show: false,
            playerquery: {
                items: [],
                charms: [],
                combos: false,
                maxupgrade: false
            },
            buffs: {
                enchant: {
                    max: 4,
                    val: 0
                },
                arctic: {
                    max: 4,
                    val: 0
                },
                hypo: {
                    max: 5,
                    val: 0
                },
                warcry: {
                    max: 4,
                    val: 0
                },
                crusader: {
                    max: 4,
                    val: 0
                },
                armor: {
                    max: 5,
                    val: 0
                },
                enrage: {
                    max: 5,
                    val: 0
                },
                temporal: {
                    max: 4,
                    val: 0
                },
                cranial: {
                    max: 5,
                    val: 0
                },
                invigorate: {
                    max: 5,
                    val: 0
                },
                canine: {
                    max: 5,
                    val: 0
                },
                plague: {
                    max: 5,
                    val: 0
                },
                skull: {
                    max: 1,
                    val: 0
                },
            },
            sheets: {},
            sheets_order: [],
            count: 0
        };
    },
    created() {
        axios.get(`${this.$store.state.backend}/names`)
            .then(r => {
            this.search_terms = r.data;
        });
    },
    methods: {
        ordersheets(){
            let ordered = []
            for (const id in this.sheets) {
                let pos = 0
                let sheet = this.sheets[id]
                for (let i=0; i < ordered.length; i++) {
                    if (sheet.stats.stats.evaluated.buildscore > this.sheets[ordered[i]].stats.stats.evaluated.buildscore) {
                        break
                    }
                    pos++
                }
                ordered.splice(pos, 0, id)
            }
            this.sheets_order = ordered
        },
        showResults(val) {
            this.search_show = true;
            let list = [];
            let terms = this.autocompleteMatch(val);
            for (let i = 0; i < terms.length; i++) {
                list.push(terms[i]);
            }
            this.search_result = list;
        },
        autocompleteMatch(input) {
            if (input == "") {
                return [];
            }
            var reg = new RegExp(input.toLowerCase());
            return this.search_terms.filter(function (term) {
                if (term.toLowerCase().match(reg)) {
                    return term;
                }
            });
        },
        parseitems(data) {
            data = data.split("\n");
            let charms = ["tattooed skull", "hardened egg", "little bell", "blue marble", "ship pennant"];
            let parsed = [];
            let charmsparsed = [];
            let p =["-","-"]
            const capitalize = s => s.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
            for (let i = 0; i < data.length; i++) {
                let s = "";
                let u = "-";
                if (data[i].includes("Charm") || data[i].includes("pID:")) {
                    continue;
                }
                if (data[i].includes("%")) {
                    s = data[i].split("%")[1].replace(/[^\d\+\n]/g, "");
                    i++;
                    u = data[i].replace(/[^\d\+\n]/g, "");
                }
                else if (charms.includes(data[i].toLowerCase())) {
                    charmsparsed.push(capitalize(data[i].toLowerCase()));
                }
                else {
                    p = data[i].replace(/[^\d\+\n]/g, "").split("+");
                    s = p[0];
                    if (p[1]) {
                        u = "+" + p[1];
                    } else {
                        p[1] = "-"
                    }
                }
                if (s != "" && s.length > 3) {
                    if (!(i == 0 && s.length < 4)) {
                        parsed.push([s, u]);
                        this.playerquery.itemupgrades[s] = p[1]
                    }
                }
            }

            this.playerquery.items = parsed.slice(0,9);
            this.playerquery.charms = charmsparsed;
            this.playerquery.itemsfull = undefined
            this.playerquery.combos = false

            if (parsed.length > 9) {
                this.playerquery.itemsfull = parsed
            }
        },
        unfocused(val) {
            this.search_show = false;
            this.setName(val);
        },
        assignName(c) {
            document.getElementById("playername").value = c;
        },
        setName(c) {
            if (c == "") {
                return
            }
            let tlname = c
            c = c.split("(")[0].replace(" ","")
            this.playerquery.name = c;
            document.getElementById("playername").value = tlname;
            let playerinfo, itemIDs;
            let bloodline = {
                1: "int",
                2: "dex",
                3: "wis",
                0: "str"
            };
            axios.get(`${this.$store.state.backend}/players?player=${c}`).then(r => {
                playerinfo = r.data;
                this.playerinfo = r.data;
                this.playerinfo["name"] = tlname
                axios.get(`${this.$store.state.backend}/tierlist?items=true&name=${tlname.toLowerCase()}&pclass=${playerinfo["pclass"]}`).then(r => {
                    itemIDs = r.data;
                    let s = "";
                    this.playerquery.items = [];
                    this.playerquery.itemupgrades = {}
                    r.data.forEach(id => {
                        this.playerquery.items.push([id, "-"]);
                        this.playerquery.itemupgrades[id] = "-"
                        s += id + "\n";
                    });
                    document.getElementById("iteminput").value = s;
                    this.checkbox(document.getElementById(bloodline[playerinfo.pclass]), true);
                    document.getElementById("prestigeslider").value = playerinfo.prestige;
                    document.getElementById("prestigeslider").nextElementSibling.value = playerinfo.prestige;
                });
            });
        },
        checkbox(curr, direct = false) {
            let x = document.getElementsByName("allocated");
            x.forEach(e => {
                e.checked = false;
            });
            if (direct) {
                curr.checked = true;
                this.playerquery.spec = String(curr.id)
            }
            else {
                curr.target.checked = true;
                this.playerquery.spec = String(curr.target.id)
            }
        },
        setbuff(curr) {
            if (curr == "all") {
                for (const b in this.buffs) {
                    let btns = [...document.getElementById(b).children];
                    btns.forEach(btn => {
                        btn.style.backgroundColor = "#27bd90";
                    });
                    this.buffs[b].val = this.buffs[b].max;
                }
            }
            else if (curr == "none") {
                for (const b in this.buffs) {
                    let btns = [...document.getElementById(b).children];
                    btns.forEach(btn => {
                        btn.style.backgroundColor = "#1f2020";
                    });
                    this.buffs[b].val = 0;
                }
            }
            else {
                let btns = [...curr.target.parentNode.children];
                let index = btns.indexOf(curr.target);
                if (curr.target.style.backgroundColor == "rgb(39, 189, 144)") {
                    index -= 1;
                }
                this.buffs[curr.target.parentNode.id].val = index + 1;
                for (let i = 0; i < btns.length; i++) {
                    if (i <= index) {
                        btns[i].style.backgroundColor = "#27bd90";
                    }
                    else {
                        btns[i].style.backgroundColor = "#1f2020";
                    }
                }
            }
        },
        addplayer() {
            if (!this.playerinfo || !this.playerquery) { 
                return
            }

            let itemIDs = [];
            if (this.playerquery.combos && this.playerquery.itemsfull) {
                this.playerquery.itemsfull.forEach(i => {
                    itemIDs.push(i[0]);
                });
            } else {
                this.playerquery.items.forEach(i => {
                    itemIDs.push(i[0]);
                });
            }
            axios.post(`${this.$store.state.backend}/items`, { "ids": itemIDs }).then(r => {
                let items = r.data;
                items.forEach(i => {
                    if (this.playerquery.itemupgrades[i.id] != "-") {
                        i.upgrade = Number(this.playerquery.itemupgrades[i.id])
                    }
                })

                axios.get(`${this.$store.state.backend}/tierlist?pclass=${this.playerinfo["pclass"]}`).then(r => {
                    let tierlist = {
                        boundaries: r.data["boundaries"],
                        rankings: r.data["rankings"]
                    };
                    this.playerinfo.prestige = Number(document.getElementById("prestigeslider").nextElementSibling.value)

                    let qbuffs = []
                    for (const k in this.buffs) {
                        let v = this.buffs[k]
                        if (v.val) {
                            if (["plague","enrage"].includes(k)) {
                                qbuffs.push({
                                    name: k,
                                    stacks: v.val,
                                    level: 5
                                })
                            } else {
                                qbuffs.push({
                                    name: k,
                                    level: v.val,
                                    stacks: false
                                })
                            }
                        }
                    }
                    this.playerinfo.args = {
                        spec: this.playerquery.spec,
                        maxupgrade: this.playerquery.maxupgrade,
                        buffs: qbuffs,
                        charms: this.playerquery.charms
                    }

                    let char = Object.assign(this.playerinfo, {
                        itemIDs,
                        tierlist
                    });

                    if (this.playerquery.combos && this.playerquery.itemsfull) {
                        let itemarrs = {
                            "weapon" : [],
                            "armlet" : [],
                            "armor" : [],
                            "bag" : [],
                            "boot" : [],
                            "glove" : [],
                            "ring" : [],
                            "amulet" : [],
                            "offhand" : []
                        }
                        for (const k in items) {
                            if (["sword","staff","bow","hammer"].includes(items[k]["type"].toLowerCase())) {
                                itemarrs["weapon"].push(items[k])
                            } else if (["shield","orb","quiver","totem"].includes(items[k]["type"].toLowerCase())) {
                                itemarrs["offhand"].push(items[k])
                            } else {
                                itemarrs[items[k]["type"]].push(items[k])
                            }
                        }

                        function combos(list, n = 0, result = [], current = []){
                            if (n === list.length) result.push(current)
                            else list[n].forEach(item => combos(list, n+1, result, [...current, item]))
                        
                            return result
                        }

                        let gearcombos = combos(Object.values(itemarrs))
                        for (let g=0; g < Math.min(gearcombos.length, 1500); g++) {
                            let guh = JSON.parse(JSON.stringify(char))
                            guh.items = gearcombos[g]
                            if (guh.prestige && guh.name) {
                                this.sheets[this.count] = guh
                                this.sheets_order.push(this.count)
                                this.count++
                            }
                        }

                    } else {
                        let guh = JSON.parse(JSON.stringify(char))
                        guh.items = items

                        if (guh.items && guh.prestige && guh.name && !guh.items.fail) {
                            this.sheets[this.count] = guh
                            this.sheets_order.push(this.count)
                            this.count++
                        }
                    }

                });
            });
        },
        removeplayer(idx) {
            this.sheets_order.splice(this.sheets_order.indexOf(idx), 1)
            delete this.sheets[idx]
        }
    },
    components: { Playercard }
}



/* 
name input -> charinfo
items input -> decoded items
args selection -> spec, prestige, buffs, charms
spec: str stam dex int wis luck
*/
//<Playercard :charinfo="sheets[0]"/>

</script>

<template>
    <div class="statoptions">
        <form autocomplete="off" onsubmit="return false">
            <input type="text" placeholder="player name" id="playername" @focus="search_show = true" @blur="unfocused($event.target.value)" @keyup="showResults($event.target.value)" />
            <div id="result">
                <ul v-if="search_show">
                    <li @mousedown.prevent @click="assignName(res)" v-for="res in search_result">{{res}}</li>
                </ul>
            </div>
        </form>
        <div id="itemarea">
            <textarea :placeholder="'Paste auxi/itemID info\nEach id on new line'" id="iteminput" @blur="parseitems($event.target.value)"></textarea>
            <div style="cursor: text;">
                <span>ID</span>
                <span style="margin-left: 88px;">+</span>
                <div v-for="i in playerquery.items" class="itemsparsed">
                    <input style="width: 100px" type="text" :value="i[0]"/>
                    <input style="width: 20px" type="text" :value="i[1]"/>
                </div>
            </div>
            <div style="cursor: text; align-self: center;">
                <div v-for="i in playerquery.charms" class="itemsparsed">
                    <input style="width: 100px" type="text" :value="i"/>
                </div>
                <div style="margin-top: 25px;">
                    <label for="combos">maxupgrade</label>
                    <input type="checkbox" id="maxupgrade" style="width: inherit;" @click="playerquery.maxupgrade = !playerquery.maxupgrade">
                </div>
                <div v-if="playerquery.itemsfull" style="margin-top: 25px;">
                    <label for="combos">combinations</label>
                    <input type="checkbox" id="combos" style="width: inherit;" @click="playerquery.combos = !playerquery.combos">
                </div>
            </div>
        </div>
        <div id="argsarea">
            <form id="spec">
                <label for="str">str</label>
                <input name="allocated" @click="checkbox" type="checkbox" id="str">
                <label for="str">sta</label>
                <input name="allocated" @click="checkbox" type="checkbox" id="sta">
                <label for="str">dex</label>
                <input name="allocated" @click="checkbox" type="checkbox" id="dex">
                <label for="str">int</label>
                <input name="allocated" @click="checkbox" type="checkbox" id="int">
                <label for="str">wis</label>
                <input name="allocated" @click="checkbox" type="checkbox" id="wis">
                <label for="str">luck</label>
                <input name="allocated" @click="checkbox" type="checkbox" id="luc">
            </form>
            <div id="buffs">
                <div v-for="item, key in buffs" class="buffcontainer">
                    <img style="width: 20px;" :src="`/icons/buffs/${key}.jpg`"/>
                    <div class="skillpoints" :id="key">
                        <div v-for="index in (buffs[key].max)" @click="setbuff" class="btn grey"></div>
                    </div>
                </div>
            </div>
            <div id="prestige">
                <span style="grid-column: span 2;">Prestige</span>
                <input id="prestigeslider" class="standard" style="width: 80%;" type="range" min="0" max="48000" oninput="this.nextElementSibling.value = this.value"/>
                <input class="standard" style="width: 80px; pointer-events: none;" type="text"/>
            </div>
            <div id="buffbtns">
                <button class="btn" @click="setbuff('all')">Max</button>
                <button class="btn" @click="setbuff('none')">Reset</button>
            </div>
        </div>
        <div id="endbtns">
            <div id="addbtn" class="btn" @click="addplayer">+</div>
            <button id="orderbtn" class="btn" @click="ordersheets">Order</button>
        </div>
    </div>
    <div id="sheets">
        <Playercard v-for="(id, index) in sheets_order" :key="id" :idx="id" :charinfo="sheets[id]" :direction="(index%2 == 0) ? 'left' : 'right'" @remove="removeplayer"/>
    </div>
</template>

<style>
.statoptions {
    width: 100%;
    height: 222px;
    display: grid;
    grid-template-columns: 2fr 2fr 3fr 1fr;
    padding-top: 25px;
    padding-bottom: 25px;
    border-bottom: 2px solid #d1d1d1;
    border-top: 2px solid #d1d1d1;
    color: #d1d1d1;
    justify-items: center;
    font-family: monospace !important;
}

.statoptions input {
    background: #1f2020;
    color: #27bd90;
    border: none;
    height: 20px;
    width: 200px;
    text-align: center;
    outline: none;
}

#sheets {
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding-inline: 133px;
    row-gap: 2vw;
    column-gap: 2vw;
    margin-top: 50px;
    margin-bottom: 50px;
}

.btn {
    text-align: center;
    padding: 0;
    border: 0 !important;
    font-family: monospace;
    font-weight: bolder;
    line-height: 1;
    background-color: #1f2020;
}

#itemarea {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    justify-items: center;
    column-gap: 50px;
}

#argsarea {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: start;
}

#iteminput {
    height: 218px;
    width: 240px;
    resize: none;
    background: #1f2020;
    color: #27bd90;
    border: none;
    text-align: left;
    outline: none;
}

.itemsparsed {
    display: grid;
    grid-template-columns: 1fr 1fr;
    pointer-events: none;
}

#prestige {
    justify-items: center;
    text-align: center;
    row-gap: 5px;
}

#buffs {
    display: grid;
    grid-template-rows: repeat(12, 1fr);
    justify-items: center;
    text-align: center;
    row-gap: 3px;
    height: 0px;
    grid-template-columns: 1fr 1fr;
    column-gap: 8px;
}

.buffcontainer {
    display: grid;
    grid-template-columns: 20px 1fr;
    column-gap: 5px;
}

.skillpoints {
    display: grid;
    grid-template-columns: repeat(5, 20px);
    grid-auto-rows: 15px;
    grid-gap: 4px;
    margin-top: 3px;
}

.standard {
    -webkit-appearance: none;
    padding: 0;
    margin: 0;
}

#result {
    position: absolute;
}

#result ul {
    display: flex;
    align-items: center;
    flex-direction: column;
    justify-content: center;
    margin-top: 0;
    top: 0;
    left: 0;
    transform: none;
    position: inherit;
}

#result li {
    width: 200px;
    font-size: smaller;
    padding: 1px 2px;
}

#spec {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    padding-inline: 20px;
    align-self: center;
}

#spec input {
    background: #1f2020;
    color: #27bd90;
    accent-color: #27bd90;
    border: none;
    height: 20px;
    width: inherit;
    text-align: center;
    outline: none;
}

#buffbtns {
    align-self: center;
    margin-top: 30px;
}

#buffbtns button {
    width: 50px;
    height: 18px
}

#orderbtn {
    margin-top: 50px;
    width: 50px;
    height: 18px
}

#endbtns {
    display: flex;
    flex-direction: column;
    align-content: center;
    justify-content: center;
    align-items: center;
}

.btn:hover {
    background-color: #27bd90;
}

#addbtn {
    height: 40px;
    width: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #d1d1d1 !important;
    border-radius: 3px;
    font-size: larger;
    justify-self: center;
    align-self: center;
}
</style>

