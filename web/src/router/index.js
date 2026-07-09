import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Detail from '../views/Detail.vue'
import Search from '../views/Search.vue'
import Category from '../views/Category.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/news/:id', name: 'Detail', component: Detail },
  { path: '/search', name: 'Search', component: Search },
  { path: '/category/:name', name: 'Category', component: Category },
  { path: '/login', name: 'Login', component: Login },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
