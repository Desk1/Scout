import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../views/Login.vue'
import Tierlists from '../views/Tierlist.vue'
import Playerstats from '../views/Playerpage.vue'
import Items from '../views/Items.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/tierlists',
    name: 'tierlists',
    component: Tierlists
  },
  {
    path: '/playerstats',
    name: 'playerstats',
    component: Playerstats
  },
  {
    path: '/items',
    name: 'items',
    component: Items
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
]

const router = createRouter({
  history: createWebHistory(),
  base: "/",
  routes, // short for `routes: routes`
})

export default router