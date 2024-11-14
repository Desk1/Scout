<script>
import axios from "axios";
import Playercard from "../components/Playercard.vue";
import Chart from 'chart.js/auto';

export default {
    data() {
        return {
            selected: undefined,
            selectedStyle: {
                color: "#27bd90"
            },
            charInfo: undefined,
			gloomInfo: undefined,
			gloomStats: undefined,
			prestigeStats: undefined,
			chart: undefined,
			showcag: false,
			loading: false
        };
    },
    methods: {
		getLoginURL() {
			console.log(this.$store.state.backend)
			const discord = {
				CLIENT_ID : "",
				redirect : encodeURIComponent(`${this.$store.state.backend}/loginredirect`)
			}
			return `https://discordapp.com/api/oauth2/authorize?client_id=${discord.CLIENT_ID}&scope=identify&response_type=code&redirect_uri=${discord.redirect}`
		},
		startloading() {
			this.loading = true
			document.getElementById("loading").style.visibility = "visible"
			document.getElementById("loading").style.borderBottom = "2px solid #27bd90"
			document.getElementById("loading").style.width = "100%"
		},
		finishloading() {
			setTimeout(() => {this.loading = false}, 3000)
			document.getElementById("loading").style.visibility = "hidden"
			document.getElementById("loading").style.width = "0%"
		},
		donecard() {
			this.showcag = true
			this.finishloading()
			this.gloom()
		},
		prestige() {
			axios.get(`${this.$store.state.backend}/pvp`).then(r => {
				let percentiles = r.data

				let ranks = {
					0     : ["None","None"],
					4000  : ["Recruit","Unclean"],
					8000  : ["Novice","Brawler"],
					12000 : ["Squire","Slayer"],
					16000 : ["Apprentice","Ravager"],
					20000 : ["Adept","Breaker"],
					24000 : ["Fierce Master","Ruthless Demolisher"],
					28000 : ["Valiant Knight","Savage Marauder"],
					32000 : ["Gallant Soldier","Wild Reaper"],
					36000 : ["Famous Veteran","Defiant Liberator"],
					40000 : ["Fearless Warden","Bold Champion"],
					44000 : ["Supreme Commander","Restless Hero"],
					48000 : ["Lord","Chosen"]
				}
				let pawards = [2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000]
				let currentRank, currentBracket
				for (const i in ranks) {
					if (this.charInfo["prestige"] > 48000) {
						currentRank = ranks[48000][this.charInfo["faction"]]
						currentBracket = 48000
						break
					} else if (this.charInfo["prestige"] < i) {
						currentRank = ranks[i-4000][this.charInfo["faction"]]
						currentBracket = i-4000
						break
					}
				}
				let prestigeNeeded = currentBracket-(this.charInfo["prestige"]*0.8)

				let bracketMaintain, fameMaintain, bracketNext, fameNext

				if (prestigeNeeded <= 0) {
					bracketMaintain = "None"
					fameMaintain = "None"
				} else if (prestigeNeeded < 1001) {
					bracketMaintain = 1
					fameMaintain = percentiles[this.charInfo["faction"]][bracketMaintain-1]
				} else {
					bracketMaintain = pawards.indexOf(Math.ceil(prestigeNeeded/1000)*1000)+1
					fameMaintain = percentiles[this.charInfo["faction"]][bracketMaintain-1]
				}

				if (currentBracket == 48000) {
					bracketNext = "0"
					fameNext = "0"
				} else if (currentBracket == 0) {
					bracketNext = pawards.indexOf(Math.ceil((4000-prestigeNeeded)/1000)*1000)+1
					fameNext = percentiles[this.charInfo["faction"]][bracketNext-1]
				} else if (prestigeNeeded <= 0) {
					bracketNext = pawards.indexOf(Math.ceil(((currentBracket+4000)-(this.charInfo["prestige"]*0.8))/1000)*1000)+1
					fameNext = percentiles[this.charInfo["faction"]][bracketNext-1]
				} else {
					bracketNext = bracketMaintain + 4
					fameNext = percentiles[this.charInfo["faction"]][bracketNext-1]
				}

				this.prestigeStats = {
					rank: currentRank,
					bracketMaintain,
					bracketNext,
					fameMaintain,
					fameNext
				}
			})
		},
        gloom() {
			if (this.chart) {
				this.chart.destroy()
			}
			if (!this.gloomInfo) {
				return
			}
            const ctx = document.getElementById('chart').getContext('2d');

			const killdata = []
			const scoredata = []
			const daycount = {}
			const recordcount = {}
			const dates = [];
			var mode = ""
			switch (Math.max(this.gloomInfo["dps"]["record"][0],this.gloomInfo["hps"]["record"][0],this.gloomInfo["mps"]["record"][0])) {
				case this.gloomInfo["dps"]["record"][0]:
					mode = "dps"
					break
				case this.gloomInfo["hps"]["record"][0]:
					mode = "hps"
					break
				default:
					mode = "mps"
					break
			}
			for (let date = new Date(this.gloomInfo["kills"][0][1]); date <= Date.now(); date.setDate(date.getDate() + 1)) {
				const cloned = new Date(date.valueOf());
				dates.push(cloned.toISOString().split('T')[0])
			}
			this.gloomStats = {
				totalkills: this.gloomInfo["kills"].length,
				avgkills: this.gloomInfo["kills"].length / dates.length,
				deaths: this.gloomInfo["deaths"],
				records: {
					DPS: this.gloomInfo["dps"]["record"],
					HPS: this.gloomInfo["hps"]["record"],
					MPS: this.gloomInfo["mps"]["record"]
				},
				mode: mode.toUpperCase()
			}

			this.gloomInfo["kills"].forEach(k => {
				if (daycount[k[1]]) {
					daycount[k[1]]++
				} else {
					daycount[k[1]] = 1
				}
			})
			this.gloomInfo[mode]["records"].forEach(k => {
				recordcount[k[1]] = k[0]
			})
			let prevrecord = this.gloomInfo[mode]["records"][0][0]
			dates.forEach(d => {
				
				killdata.push({
					x: d,
					y: daycount[d] ? daycount[d] : 0
				})
				
				if (recordcount[d]) {prevrecord = recordcount[d]}
				scoredata.push({
					x: d,
					y: recordcount[d] ? recordcount[d] : prevrecord
				})
			})
			const totalDuration = 1000;
			const delayBetweenPoints = 14;
			const previousY = (ctx) => ctx.index === 0 ? ctx.chart.scales.y1.getPixelForValue(100) : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y;
			const animation = {
			x: {
				type: 'number',
				easing: 'linear',
				duration: delayBetweenPoints,
				from: NaN, // the point is initially skipped
				delay(ctx) {
				if (ctx.type !== 'data' || ctx.xStarted) {
					return 0;
				}
				ctx.xStarted = true;
				return ctx.index * delayBetweenPoints;
				}
			},
			y: {
				type: 'number',
				easing: 'linear',
				duration: delayBetweenPoints,
				from: previousY,
				delay(ctx) {
				if (ctx.type !== 'data' || ctx.yStarted) {
					return 0;
				}
				ctx.yStarted = true;
				return ctx.index * delayBetweenPoints;
				}
			}
			};
			this.chart = new Chart(ctx, {
				type: 'line',
				data: {
					datasets:
					[
						{
							borderColor: '#bf42f5',
							borderWidth: 2,
							pointBackgroundColor: 'white',
							radius: 0,
							data: killdata,
							label: "kills",
							yAxisID: "y1"
						},
						{
							borderColor: '#f54242',
							borderWidth: 2,
							pointBackgroundColor: 'white',
							radius: 0,
							data: scoredata,
							label: "record",
							yAxisID: "y2"
						}
					]
				},
				options: {
					animation,
					responsive: true, 
  					maintainAspectRatio: false,
					interaction: {
					intersect: false
					},
					plugins: {
					legend: true
					},
					scales: {
						x: {
							min: this.gloomInfo["kills"][0][1],
							ticks: {
								maxTicksLimit: 10
							}
						},
						y1: {
							min: 0,
							position: "left",
							title: {
								display: true,
								text: 'kills'
							}
						},
						y2: {
							position: "right",
							title: {
								display: true,
								text: mode
							}
						}
					},
					grid: {
						color: "#131212"
					}
				}
			});
        },
        selectChar(c) {
			if (this.loading) {
				return
			}
            this.selected = c
			this.startloading()
			let playerinfo, itemIDs, items, tierlist

			//playerstats
			
			axios.get(`${this.$store.state.backend}/players?player=${c}`).then(r => {
				playerinfo = r.data

				if (playerinfo["pclass"] >= 0) {
					axios.get(`${this.$store.state.backend}/tierlist?items=true&name=${c.toLowerCase()}&pclass=${playerinfo["pclass"]}`).then(r => {
						itemIDs = r.data;

						axios.post(`${this.$store.state.backend}/items`, {"ids" : itemIDs}).then(r => {
							items = r.data

							axios.get(`${this.$store.state.backend}/tierlist?pclass=${playerinfo["pclass"]}`).then(r => {
								tierlist = {
									boundaries: r.data["boundaries"],
									rankings: r.data["rankings"]
								}

								this.charInfo = Object.assign(playerinfo, {
									itemIDs,
									items,
									tierlist,
									done: true
								})

								this.charInfo.args = {
									spec: false,
									maxupgrade: false,
									buffs: [],
									charms: ["Tattooed Skull","Hardened Egg"]
								}
								this.prestige()
							})

						})
					})
				}
			})
			
			//gloom
			axios.get(`${this.$store.state.backend}/gloom?player=${c}`).then(r => {
				this.gloomInfo = r.data
			})
			
			
        }
    },
    computed: {
        user() {
            return this.$store.state.user;
        },
        characters() {
            return this.$store.state.characterNames;
        }
    },
    created() {
		if (this.user) {
			axios.get(`${this.$store.state.backend}/characters?userid=${this.$store.state.user.id}`)
				.then(r => {
				this.$store.commit("pushcharacternames", r.data);
			});
		}
		
		if (this.$route.query.token) {
			axios.get(
				"https://discord.com/api/users/@me",
				{ headers : {"Authorization" : `Bearer ${this.$route.query.token}`} }
			)
			.then(r => {
				this.$store.commit("login", r.data)
			})

			this.$router.push({name:"login"})
		}
		
    
    },
    components: { Playercard }
}

</script>

<template>
	<div v-if="!user" id="notLoggedIn">
		<div id="loginPanel" style="color: white">
			<h1>
				Login to
				<span style="color:#27bd90">Scout</span>
			</h1>
			<p>
				Sign in with your
				<strong style="color: lightblue">Discord account</strong>
				to see your characters.
			</p>
			<a :href="getLoginURL()" class="btn" id="loginbtn">Login</a>
			<small>
				Need help? Try our
				<a href="https://discord.gg/MFyd7WRYHF" style="color: lightblue">discord</a>
			</small>
		</div>
	</div>
	<div v-else id="loggedin">
		<div id="loading"></div>
		<div v-if="characters.length" id="characterselect">
			<ul>
				<li :style="selected==char ? selectedStyle : null" @click="selectChar(char)"
					v-for="char in characters">{{char}}</li>
			</ul>
		</div>
		<div v-else>
			<h4 style="top: 25%">Add characters via the discord bot</h4>
			<a href="https://discord.gg/MFyd7WRYHF" target="_blank">link</a>
		</div>
		<div id="cag" :style="`visibility: ${showcag ? 'visisble' : 'hidden'}`">
			<div class="statboard prestige" v-if="prestigeStats">
				<span style="color: #27bd90;grid-column: span 2; font-weight: bold;">Prestige</span>
				<span style="justify-self: left">Rank</span>
				<span style="justify-self: right">{{prestigeStats.rank}}</span>
				<span></span>
				<span></span>
				<span style="justify-self: center;grid-column: span 2;">Maintain Rank</span>
				<span style="justify-self: left">Bracket {{prestigeStats.bracketMaintain}}</span>
				<span style="justify-self: right">{{prestigeStats.fameMaintain}} Fame</span>
				<span></span>
				<span></span>
				<span style="justify-self: center;grid-column: span 2;">Next Rank</span>
				<span style="justify-self: left">Bracket {{prestigeStats.bracketNext}}</span>
				<span style="justify-self: right">{{prestigeStats.fameNext}} Fame</span>
			</div>
			<Playercard v-if="charInfo" :charinfo="charInfo" @done="donecard"/>
			<div class="statboard gloom" v-if="gloomStats">
				<span style="grid-column: span 6; color: #27bd90; font-weight: bold;">Gloom</span>
				<span style="justify-self: left">Total Kills</span>
				<span style="justify-self: right">{{gloomStats.totalkills}}</span>
				<span style="justify-self: left">Avg. Kills</span>
				<span style="justify-self: right">{{gloomStats.avgkills.toFixed(1)}} / day</span>
				<span style="justify-self: left">Deaths</span>
				<span style="justify-self: right">{{gloomStats.deaths}}</span>
				<span></span>
				<span></span>
				<span></span>
				<span></span>
				<span style="grid-column: span 6;">Records</span>
				<span class="centerstat" v-for="(item, key) in gloomStats.records">{{key}}</span>
				<span class="centerstat" :style="gloomStats.mode == key ? 'color: #27bd90' : 1" v-for="(item, key) in gloomStats.records">{{item[0]}}</span>
			</div>
			<div v-if="gloomInfo" class="chart-container" @click="test()">
				<canvas id="chart"></canvas>
			</div>
		</div>
	</div>
</template>

<style>
#notLoggedIn {
    height: calc(100vh - 70px);
    background-image:
	linear-gradient(to right, rgba(245, 246, 252, 0), rgb(19, 18, 18)),
	url(/src/assets/bg.jpg);
    background-size: cover;
}

#loginPanel {
	float: right;
    width: 30%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-content: center;
    align-items: center;
    justify-content: center;
}

#loginbtn {
	height: 40px;
    width: 85px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #d1d1d1 !important;
    border-radius: 3px;
    font-size: larger;
    justify-self: center;
    align-self: center;
	margin: 80px;
}

#loggedin {
	height: 100%;
}

#cag {
	display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    justify-items: center;
    align-items: start;
	grid-gap: 20px;
	position: relative;
	left: 5%;
	width: 90%;
	top: 75px;
}

#loading {
	width: 0%;
	transition: width 2s;
	border-bottom: 2px solid;
	z-index: 100;
}

.statboard {
	display: grid;
	grid-template-columns: 1fr 1fr;
	align-content: start;
    column-gap: 3px;
	row-gap: 16px;
    align-items: center;
	background-color: #1f2020;
    color: #d1d1d1;
    border-radius: 3px;
    padding: 20px;
	width: 280px;
}

.statboard.gloom {
	grid-template-columns: repeat(6, 1fr);
}

.statboard.gloom span {
	grid-column: span 3;
}

.centerstat {
	justify-self: center;
    grid-column: span 2 !important;
}

.chart-container {
	grid-column: span 3;
    width: 100%;
	height: 400px;
}

ul {
	display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 55px;
	padding: 0;
	left: 50%;
	transform: translateX(-50%);
	z-index: 99;
}

li {
	display: block;
	width: 170px;
    padding-top: 10px;
    padding-bottom: 10px;
    transition: background-color 0.5s;
    color: #d1d1d1;
    font-weight: bold;
    background: #131212;
}

li:hover {
	color: #27bd90;
}

.hidden {
	visibility: hidden;
}

</style>