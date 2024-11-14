import { createApp } from 'vue'
import { createStore } from 'vuex'
import App from './App.vue'
import router from './router'
import createPersistedState from "vuex-persistedstate"
import styles from "./base.css"


const store = createStore({
    state () {
      return {
        user: undefined,
        characterInfo: [],
        characterNames : [],
        backend: "https://pear-funny-drill.cyclic.app" // rip heroku 2022 https://scout-backend.herokuapp.com http://localhost:3001
      }
    },
    mutations: {
        login (state, data) {
            state.user = data
        },
        logout (state) {
            state.user = undefined
        },
        pushcharacternames (state, c) {
            state.characterNames = c
            let newchars = []
            c.forEach(char => {
                newchars.push({
                    [char] : {}
                })
            })
            state.characterInfo = newchars
        },
        pushcharacterinfo (state, info) {
            state.characterInfo[info.name] = info.data
        }
    },
    plugins: [createPersistedState({
        paths: [
            "user",
            "characterInfo",
            "characterNames"
        ]
    })]
})

const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')
