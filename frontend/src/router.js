import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'map', component: () => import('./views/MapView.vue') },
  { path: '/module/:moduleId', name: 'module', component: () => import('./views/ModuleView.vue') },
  {
    path: '/module/:moduleId/knowledge/:knowledgeId',
    name: 'knowledge',
    component: () => import('./views/KnowledgeView.vue')
  },
  {
    path: '/module/:moduleId/problem/:problemId',
    name: 'problem',
    component: () => import('./views/ProblemView.vue')
  },
  { path: '/wrongbook', name: 'wrongbook', component: () => import('./views/WrongBookView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    if (to.name === 'problem') return { top: 0 }
    return { top: 0 }
  }
})

export default router
