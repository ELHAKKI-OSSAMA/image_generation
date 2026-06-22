import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'
import { useOrganizationStore } from './organization'
/**
 * Auth store for handling user authentication and authorization.
 */
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    role: null,
    permissions: {},
    organization: null,
    auth_initialized: false,
    isRefreshing: false
  }),

  getters: {
    is_authenticated: (state) => !!state.user,
    is_admin: (state) => state.permissions?.manage_users && state.permissions?.manage_organizations,
    is_super_admin: (state) => state.permissions?.all,
    is_organization_admin: (state) => state.permissions?.manage_org_members && state.permissions?.manage_org_settings,
    is_organization_member: (state) => state.role === 'member',
    is_regular_user: (state) => state.role === 'user',
    organization_id: (state) => {
      // First check if we have an organization in the auth store
      if (state.organization?.id) {
        return state.organization.id;
      }
      
      // If not, try to get it from the organization store
      try {
        const orgStore = useOrganizationStore();
        if (orgStore.organization?.id) {
          return orgStore.organization.id;
        }
        
        // If organization is not loaded yet, try to fetch it
        if (!orgStore.isLoading && orgStore.organizations?.length === 0) {
          orgStore.fetch_organizations();
        }
        
        // Return the first organization ID if available
        return orgStore.organizations?.[0]?.id || null;
      } catch (error) {
        console.error('Error getting organization ID:', error);
        return null;
      }
    },
    organization_status: (state) => {
      const orgStore = useOrganizationStore()
      return orgStore.currentOrganization?.status || null
    },
  },

  persist: {
    key: 'auth',
    storage: sessionStorage,
    paths: ['user', 'role', 'permissions', 'organization']
  },

  actions: {
    async register(userData) {
      try {
        const response = await axiosInstance.post('/api/v1/auth/register', userData)
        
        this.user = {
          id: response.data.id,
          email: response.data.email,
          first_name: response.data.first_name,
          last_name: response.data.last_name,
          role: response.data.role,
          is_verified: response.data.is_verified
        }
        this.role = response.data.role
        this.permissions = response.data.permissions

        if (response.data.organization) {
          this.organization = response.data.organization
        }

        // Navigate based on role and permissions
        if (this.is_super_admin) {
          window.router.push('/super-admin')
        } else if (this.is_admin) {
          window.router.push('/admin')
        } else if (this.is_organization_admin) {
          if (this.organization?.status === 'pending') {
            window.router.push('/pending-approval')
          } else {
            window.router.push('/organization')
          }
        } else {
          window.router.push('/dashboard')
        }

      } catch (error) {
        console.error('Registration error:', error)
        throw new Error(error.response?.data?.detail || error.message || 'Failed to register')
      }
    },

    async login(email, password, remember_me = false) {
      console.log('Attempting login...')
      try {
        const response = await axiosInstance.post('/api/v1/auth/login', {
          email,
          password,
          remember_me
        })
        console.log('Login response:', response.data)
        
        // Set user data from response
        const { user } = response.data
        console.log('Setting user data:', user)
        
        // Add these lines:
        console.log('User data from backend:', {
          user: response.data.user,
          organizations: response.data.user.organizations,
          memberships: response.data.user.memberships
        })
        this.user = {
          id: user.id,
          email: user.email,
          role: user.role,
          is_verified: user.is_verified
        }
        this.role = user.role
        this.permissions = user.permissions
        console.log('Updated user state:', {
          id: this.user.id,
          email: this.user.email,
          role: this.role,
          permissions: this.permissions
        })

        // Add detailed logging for role and permissions
        console.log('DETAILED USER ROLE INFO:', {
          role: this.role,
          is_super_admin: this.is_super_admin,
          is_admin: this.is_admin,
          is_organization_admin: this.is_organization_admin,
          is_organization_member: this.is_organization_member,
          is_regular_user: this.is_regular_user
        })
        
        console.log('DETAILED PERMISSIONS:', this.permissions)
        
        // Add logging for navigation decision
        console.log('NAVIGATION DECISION:', {
          to_super_admin: this.is_super_admin ? '/super-admin' : null,
          to_organization: (this.is_organization_admin || this.is_organization_member) ? '/organization' : null,
          to_dashboard: this.is_regular_user ? '/dashboard' : null,
          organization_status: this.organization?.status
        })

        // Navigate based on permissions
        if (this.is_super_admin) {
          window.router.push('/super-admin')
        } else if (this.is_organization_admin || this.is_organization_member) {
          window.router.push('/organization')
        } else if (this.is_regular_user) {
          window.router.push('/dashboard')
        } else {
          window.router.push('/')
        }
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },

    async refreshToken() {
      if (this.isRefreshing) {
        console.log('Token refresh already in progress...')
        return false
      }

      console.log('Starting token refresh...')
      this.isRefreshing = true

      try {
        const refreshResponse = await axiosInstance.post('/api/v1/auth/refresh')
        if (refreshResponse.data?.user) {
          const userData = refreshResponse.data.user
          this.user = {
            id: userData.id,
            email: userData.email,
            role: userData.role,
            is_verified: userData.is_verified,
            organizations: userData.organizations || [],  // Add this line
            memberships: userData.memberships || [] 
          }
          this.role = userData.role
          this.permissions = userData.permissions || {}
          console.log('Token refresh successful')
          return true
        }
        return false
      } catch (error) {
        console.error('Token refresh failed:', error)
        return false
      } finally {
        this.isRefreshing = false
      }
    },

    async initAuth() {
      console.log('Initializing auth...')
      if (this.auth_initialized) {
        console.log('Auth already initialized')
        return
      }

      try {
        const success = await this.refreshToken()
        if (success) {
          this.auth_initialized = true
          console.log('Auth initialized successfully')
        }
      } catch (error) {
        console.error('Auth initialization failed:', error)
        this.user = null
      }
    },

    async logout() {
      try {
        await axiosInstance.post('/api/v1/auth/logout')
      } catch (error) {
        console.error('Logout error:', error)
      }
      
      this.user = null
      this.role = null
      this.permissions = {}
      this.organization = null
      this.auth_initialized = false
      window.router.push('/login')
    }
  }
})
