<script>
import Navbar from './components/Navbar.vue'

export default {
	components : {
		Navbar
	}
}
</script>

<template>
    <Navbar/>
    <router-view/>
</template>

<style>

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #27bd90;
  min-height: 100vh;
}

body {
  color: var(--color-text);
  transition: color 0.5s, background-color 0.5s;
  line-height: 1.6;
  font-family: "Moon";
  font-size: 15px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #181817;
  letter-spacing: 0.09em;
  margin: 0;
  min-height: 100vh;
}

a {
	color: #d1d1d1;
    text-decoration: none;
}

a:active {
	color: #27bd90;
}

@font-face {
  font-family: "Moon";
  src: url("src/assets/fonts/Moon2.0-Regular.otf") format("opentype");
}

@font-face {
  font-family: "MoonBold";
  src: url("src/assets/fonts/Moon2.0-Bold.otf") format("opentype");
}


</style>
