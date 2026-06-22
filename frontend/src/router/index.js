import { createRouter as _createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { requireAuth, requireAdmin, requireSuperAdmin, requireOrganizationAdmin, requirePermissions, requireOrganizationAccess, requireOrganizationViewAccess } from './guards'

export function createRouter() {
  const router = _createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/login',
        name: 'login',
        component: () => import('../views/auth/LoginView.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/register',
        name: 'register',
        component: () => import('../views/auth/RegisterView.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/pending-approval',
        name: 'pending-approval',
        component: () => import('../views/auth/PendingApproval.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/unauthorized',
        name: 'unauthorized',
        component: () => import('../views/auth/Unauthorized.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/organization',
        component: () => import('@/views/organization/Layout.vue'),
        meta: { requiresAuth: true },
        beforeEnter: requireOrganizationAccess,
        children: [
          {
            path: '',
            name: 'organization-dashboard',
            component: () => import('@/views/organization/Dashboard.vue')
          },
          {
            path: 'generate-image',
            name: 'organization-image-generation',
            component: () => import('@/views/organization/ImageGeneration.vue')
          },
          {
            path: 'events',
            name: 'event-management',
            component: () => import('@/views/organization/EventManagement.vue'),
            beforeEnter: requireOrganizationViewAccess
          },
          {
            path: 'events/:id',
            name: 'event-detail',
            component: () => import('@/views/organization/EventDetail.vue'),
            props: true,
            beforeEnter: requireOrganizationViewAccess
          },
          {
            path: 'staff',
            name: 'staff-management',
            component: () => import('@/views/organization/StaffManagement.vue'),
            beforeEnter: requireOrganizationViewAccess
          },
          {
            path: 'settings',
            name: 'organization-settings',
            component: () => import('@/views/organization/Settings.vue'),
            beforeEnter: requireOrganizationViewAccess
          },
          {
            path: 'profile',
            name: 'organization-profile',
            component: () => import('../views/organization/Profile.vue')
          },
          {
            path: 'billing',
            name: 'organization-billing',
            component: () => import('../views/organization/Billing.vue'),
            beforeEnter: requireOrganizationViewAccess
          },
          {
            path: 'image-gallery',
            name: 'organization-image-gallery',
            component: () => import('@/views/organization/OrganizationImageGallery.vue'),
            beforeEnter: requireOrganizationViewAccess
          }
        ]
      },
      {
        path: '/event/:id',
        component: () => import('@/views/event/EventMode.vue'),
        meta: { requiresAuth: true },
        beforeEnter: requirePermissions(['view_events', 'participate_events'], false),
        children: [
          {
            path: '',
            name: 'event-mode',
            component: () => import('@/views/event/QuickCapture.vue')
          },
          {
            path: 'gallery',
            name: 'event-gallery',
            component: () => import('@/views/event/EventGallery.vue')
          }
        ]
      },
      {
        path: '/super-admin',
        name: 'super-admin',
        component: () => import('../views/admin/SuperAdminDashboard.vue'),
        meta: { requiresAuth: true },
        beforeEnter: requireSuperAdmin,
        children: [
          {
            path: 'users',
            name: 'admin-users',
            component: () => import('../views/admin/UserManagement.vue')
          },
          {
            path: 'models',
            name: 'admin-models',
            component: () => import('../views/admin/ModelManagement.vue')
          },
          {
            path: 'analytics',
            name: 'admin-analytics',
            component: () => import('../views/admin/Analytics.vue')
          },
          {
            path: 'event-management',
            name: 'admin-event-management',
            component: () => import('../views/admin/EventManagement.vue')
          },
          {
            path: 'system-logs',
            name: 'admin-system-logs',
            component: () => import('../views/admin/SystemLogs.vue')
          },
          {
            path: 'billing-subscription',
            name: 'admin-billing-subscription',
            component: () => import('../views/admin/BillingSubscription.vue')
          },
          {
            path: 'notifications',
            name: 'admin-notifications',
            component: () => import('../views/admin/Notifications.vue')
          },
          {
            path: 'permissions',
            name: 'admin-permissions',
            component: () => import('../views/admin/PermissionsManagement.vue')
          },
          {
            path: 'profile',
            name: 'admin-profile',
            component: () => import('../views/admin/Profile.vue')
          },
          {
            path: 'settings',
            name: 'admin-settings',
            component: () => import('../views/admin/Settings.vue')
          }
        ]
      },
      {
        path: '/fullscreen-image-generation',
        name: 'fullscreen-image-generation',
        component: () => import('@/views/organization/ImageGeneration.vue'),
        meta: { requiresAuth: true, standalone: true }
      },
      {
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('../views/user/UserDashboard.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: 'generate',
            name: 'image-generation',
            component: () => import('../views/user/ImageGeneration.vue')
          },
          {
            path: 'gallery',
            name: 'image-gallery',
            component: () => import('../views/user/ImageGallery.vue')
          },
          {
            path: 'profile',
            name: 'user-profile',
            component: () => import('../views/user/Profile.vue')
          },
          {
            path: 'settings',
            name: 'user-settings',
            component: () => import('../views/user/Settings.vue')
          },
          {
            path: 'events-overview',
            name: 'events-overview',
            component: () => import('../views/user/EventsOverview.vue')
          },
          {
            path: 'model-library',
            name: 'model-library',
            component: () => import('../views/user/ModelLibrary.vue')
          },
          {
            path: 'tutorials',
            name: 'tutorials',
            component: () => import('../views/user/Tutorials.vue')
          },
          {
            path: 'feedback-support',
            name: 'feedback-support',
            component: () => import('../views/user/FeedbackSupport.vue')
          }
        ]
      },
      {
        path: '/error-test',
        name: 'error-test',
        component: () => import('../components/ErrorTest.vue'),
        beforeEnter: (to, from, next) => {
          // Only allow access in development mode
          if (import.meta.env.DEV) {
            next()
          } else {
            next('/')
          }
        }
      }
    ]
  })

  // Global navigation guard
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // Check if route requires authentication
    if (to.meta.requiresAuth && !authStore.is_authenticated) {
      to.meta.returnTo = to.fullPath
      return next({ name: 'login' })
    }

    // Allow navigation
    next()
  })

  return router
}
