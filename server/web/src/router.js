import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Clients from '../views/Clients.vue'
import Actions from '../views/Actions.vue'
import AIAnalysis from '../views/AIAnalysis.vue'
import Recordings from '../views/Recordings.vue'
import PenTestResults from '../views/PenTestResults.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/clients', name: 'Clients', component: Clients },
  { path: '/actions', name: 'Actions', component: Actions },
  { path: '/ai', name: 'AIAnalysis', component: AIAnalysis },
  { path: '/recordings', name: 'Recordings', component: Recordings },
  { path: '/pen-test', name: 'PenTestResults', component: PenTestResults }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
