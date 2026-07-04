import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/mainPage',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/org/:subdomain',
      name: 'PublicOrg',
      component: () => import('../views/PublicOrgView.vue')
    },
    {
      path: '/',
      name: 'LandingPage',
      component: () => import('../views/LandingView.vue')
    }
  ],
})

router.beforeEach((to, form, next) => {
  const authStore = useAuthStore();

  if(to.meta.requiresAuth && !authStore.isAuthenticated){
    next('/login');
  } else {
    next();
  }
});

export default router
