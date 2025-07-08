import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: {
        title: '登录',
        requiresAuth: false
      }
    },
    {
      path: '/dashboard',
      component: () => import('@/views/Layout.vue'),
      meta: {
        requiresAuth: true
      },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: {
            title: '仪表板',
            icon: 'Dashboard'
          }
        },
        {
          path: '/chat',
          name: 'Chat',
          component: () => import('@/views/Chat.vue'),
          meta: {
            title: 'AI 对话',
            icon: 'ChatDotRound'
          }
        },
        {
          path: '/models',
          name: 'Models',
          component: () => import('@/views/Models.vue'),
          meta: {
            title: '模型管理',
            icon: 'Box'
          }
        },
        {
          path: '/api-keys',
          name: 'ApiKeys',
          component: () => import('@/views/ApiKeys.vue'),
          meta: {
            title: 'API 密钥',
            icon: 'Key'
          }
        },
        {
          path: '/profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue'),
          meta: {
            title: '个人资料',
            icon: 'User'
          }
        },
        {
          path: '/admin',
          name: 'Admin',
          component: () => import('@/views/admin/Layout.vue'),
          meta: {
            title: '系统管理',
            icon: 'Setting',
            requiresAdmin: true
          },
          children: [
            {
              path: '',
              name: 'AdminDashboard',
              component: () => import('@/views/admin/Dashboard.vue'),
              meta: {
                title: '管理仪表板'
              }
            },
            {
              path: 'users',
              name: 'AdminUsers',
              component: () => import('@/views/admin/Users.vue'),
              meta: {
                title: '用户管理'
              }
            },
            {
              path: 'models',
              name: 'AdminModels',
              component: () => import('@/views/admin/Models.vue'),
              meta: {
                title: '模型管理'
              }
            },
            {
              path: 'logs',
              name: 'AdminLogs',
              component: () => import('@/views/admin/Logs.vue'),
              meta: {
                title: '系统日志'
              }
            }
          ]
        }
      ]
    },
    {
      path: '/test',
      name: 'Test',
      component: () => import('@/views/Test.vue'),
      meta: {
        title: 'API 测试',
        requiresAuth: true
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: {
        title: '页面不存在'
      }
    }
  ]
})

// Global route guards
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const authStore = useAuthStore()
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - LLM Platform` : 'LLM Platform'
  
  // Check authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      ElMessage.error('请先登录')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // Check admin permission
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      ElMessage.error('需要管理员权限')
      next({ name: 'Dashboard' })
      return
    }
  }
  
  // Redirect to dashboard if already logged in and trying to access login
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router