<script>
import axios from "axios";

export default {
    data() {
        return {
            data : [],
            sheets : {
                "Mage" : "1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s",
                "Archer" : "1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0",
                "Shaman" : "1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw",
                "Warrior" : "150QNvGaKPkOQ6pKD1z2SPWfXjjYS0p7RrH8LMRWFIC8"
            },
            tableKey: 0,
            playerclass: "Mage"
        }
    },
    methods: {
        getData(apiUrl) {
            axios.get(apiUrl).then((res) => {
                var resp = res.data.valueRanges[0].values
                var newd = []
                for (let i=0; i < resp.length; i++) {
                    if (!resp[i][0] == "") {
                        var parsed = []
                        resp[i].forEach(d => {
                            if (!d == "") {
                                parsed.push(d)
                            }
                        })
                        newd.push(parsed)
                    }  
                }
                this.data = newd
            })
            .catch(error => console.log(error));
            this.tableKey += 1;
        },
        getApiurl() {
            if (this.playerclass == "Shaman" || this.playerclass == "Warrior") {
                var endcol = "K"
            } else {
                var endcol = "I"
            }
            return "https://sheets.googleapis.com/v4/spreadsheets/" + this.sheets[this.playerclass] + "/values:batchGet?ranges=Overall "+this.playerclass+" Rankings!A2:" + endcol + "1000&majorDimension=ROWS&key="
        },
        getColour(e,i,col) {
            if (e.length > 2) {
                return {
                    "color" : "#d1d1d1",
                    "font size" : "1em"
                }
            }
            if (col >= 4 && ((this.playerclass == 'Warrior' || this.playerclass == 'Shaman') ? col <= 8 : col <= 6)) {
                var nogradient = true
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
            if (!nogradient) {
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
            }

            return {
                "background" : colour,
                "-webkit-background-clip": "text",
                "-webkit-text-fill-color": "transparent",
            }


        },
        setClass(c) {
            this.playerclass = c
            this.getData(this.getApiurl())
        }
    },
    mounted() {
        this.getData(this.getApiurl())
    }
}
</script>

<template>
    <h1 id="Title">{{playerclass}}</h1>
    <div class="classButtons">
        <div class="classicon" @click="setClass('Mage')">
            <img src="/icons/classes/Mage.png"/>
        </div>
        <div class="classicon" @click="setClass('Archer')">
            <img src="/icons/classes/Archer.png"/>
        </div>
        <div class="classicon" @click="setClass('Shaman')">
            <img src="/icons/classes/Shaman.png"/>
        </div>
        <div class="classicon" @click="setClass('Warrior')">
            <img src="/icons/classes/Warrior.png"/>
        </div>
    </div>
    <table>
        <thead>
            <tr :key="tableKey">
                <th style="width: 2%">#</th>
                <th style="width: 12%">PLAYER</th>
                <th>DPS</th>
                <th>BURST</th>
                <th>EHP</th>
                <th v-if="playerclass == 'Shaman'">HP VALUE</th>
                <th v-if="playerclass == 'Warrior'">DMG RED.</th>
                <th v-if="playerclass == 'Warrior' || playerclass == 'Shaman'">HASTE</th>
                <th>TANK</th>
                <th>HYBRID</th>
                <th>DPS</th>
                <th>RANK</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(p, i) in data">
                <td v-bind:style="getColour(p[p.length-1],i,0)">{{i + 1}}</td>
                <td v-bind:style="getColour(p[i2],i,i2)" v-for="(e,i2) in p">{{e}}</td>
            </tr>
        </tbody>
    </table>
</template>

<style>
#topbar {
    position: fixed;
    top: 0px;
    left: 0px;
    width: 100%;
    height: 60px;
}

#Title {
    position: fixed;
    top: 10px;
    width: 20%;
    margin: 0px;
    margin-left: 40%;
    color: #d1d1d1;
}

img {
    max-width: 100%;
}
.classButtons {
    position: relative;
    top: 117px;
    left: 140px;
    float: left;
}

.classicon {
    width: 30px;
    height: 30px;
    margin-bottom: 10px;
    transition: background-color 0.5s;
    float: left;
    margin-right: 5px;
}

.classicon:hover{
    background-color: #27bd90;
}

table {
    top: 100px;
    text-align: center;
    background-color: #1f2020;
    color: rgb(255, 255, 255);
    overflow: hidden;
    border-collapse: collapse;
    font-size: 1.3em;
    margin: 100px;
    margin-top: 150px;
}

thead {
    background-color: #131212;
}

th {
    font-family: "MoonBold";
    letter-spacing: 3px;
    width: 8%;
}

tbody tr {
    border: 0.5px solid #5a5a5a;
}


th, td {
    padding: 9px;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.7em;
    font-weight: bold;
}

td {
    border-left: 0.5px solid #5a5a5a;
    border-right: 0.5px solid #5a5a5a;
}


</style>