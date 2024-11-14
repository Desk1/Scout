<script>
export default {
	methods: {
		getloginURL() {
			const discord = {
				CLIENT_ID : "=",
				redirect : encodeURIComponent(`${this.$store.state.backend}/loginredirect`)
			}
			return `https://discordapp.com/api/oauth2/authorize?client_id=${discord.CLIENT_ID}&scope=identify&response_type=code&redirect_uri=${discord.redirect}`
		},
		logout() {
			this.$store.commit("logout")
		},
		getAvatarURL() {
			if (!this.$store.state.user.avatar) { 
				return "/src/assets/deafultpfp.png"
			}
			return `https://cdn.discordapp.com/avatars/${this.$store.state.user.id}/${this.$store.state.user.avatar}.png?size=2048`
		}
	},
	computed: {
		user() {
			return this.$store.state.user
		}
	}
}
</script>

<template>
    <div class="navbar">
		<img id="logo" src="/src/assets/scout.png">
		<div class="navlink">
			<router-link to="/">Home</router-link>
		</div>
		<div class="navlink">
			<router-link to="/tierlists">Tierlists</router-link>
		</div>
		<div class="navlink">
			<router-link to="/playerstats">Playerstats</router-link>
		</div>
		<span class="spacer"></span>
		<div v-if="user" class="navlink login">
			<img id="avatar" :src="getAvatarURL()">
			<a v-on:click="logout">Logout</a>
		</div>
        
    </div>
	<div id="navspacer"></div>
</template>

<style>
a, #login {
	color: #d1d1d1;
    text-decoration: none;
}

a:hover {
	color: #27bd90;
	cursor: pointer;
}

#avatar {
	height: 2.1rem;
	width: 2.1rem;
	border-radius: 999px;
	margin-right: 15px;
}

.navbar {
    position: fixed;
    width: 100%;
    height: 70px;
    left: 0;
    top: 0;
    background-color: #131212;
	text-align: left;
	display: flex;
    align-items: center;
	z-index: 99;
}

#navspacer {
    width: 100%;
    height: 70px;
}

.spacer {
	flex: 1 1 auto;
}

.navlink {
	height: 50px;
	float: left;
	justify-content: space-between;
    display: flex;
    align-items: center;
	margin-left: 10px;
	margin-right: 10px;
}

.login {
	float: right;
	margin-right: 40px;
}

#logo {
    width: 50px;
    border-color: rgb(255, 255, 255);
    float: left;
	margin-left: 20px;
	margin-right: 10px;
}
</style>