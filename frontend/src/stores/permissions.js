import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usePermissionsService } from '@/services/api/permissions'
import { useAuthStore } from './auth'

export const usePermissionsStore = defineStore('permissions', () => {
  // State
  const userPermissions = ref([])
  const rolePermissions = ref({})
  const organizationMemberPermissions = ref({})
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hasPermission = computed(() => (permission) => {
    const authStore = useAuthStore();
    
    // Organization admins should have all permissions automatically
    if (authStore.role === 'organization' && authStore.is_organization_admin) {
      return true;
    }
    
    // Ensure userPermissions.value is an array before calling includes
    return Array.isArray(userPermissions.value) && userPermissions.value.includes(permission)
  })

  const canManageEvents = computed(() => {
    const authStore = useAuthStore();
    
    // Organization admins should have all permissions automatically
    if (authStore.role === 'organization' && authStore.is_organization_admin) {
      return true;
    }
    
    // Ensure userPermissions.value is an array before checking
    return Array.isArray(userPermissions.value) && (
      userPermissions.value.includes('event:create') || 
      userPermissions.value.includes('event:update') ||
      userPermissions.value.includes('event:delete')
    )
  })

  const canCreateEvent = computed(() => {
    const authStore = useAuthStore();
    
    // Organization admins should have all permissions automatically
    if (authStore.role === 'organization' && authStore.is_organization_admin) {
      return true;
    }
    
    // Ensure userPermissions.value is an array before calling includes
    return Array.isArray(userPermissions.value) && userPermissions.value.includes('event:create')
  })

  const canUpdateEvent = computed(() => {
    const authStore = useAuthStore();
    
    // Organization admins should have all permissions automatically
    if (authStore.role === 'organization' && authStore.is_organization_admin) {
      return true;
    }
    
    // Ensure userPermissions.value is an array before calling includes
    return Array.isArray(userPermissions.value) && userPermissions.value.includes('event:update')
  })

  const canDeleteEvent = computed(() => {
    const authStore = useAuthStore();
    
    // Organization admins should have all permissions automatically
    if (authStore.role === 'organization' && authStore.is_organization_admin) {
      return true;
    }
    
    // Ensure userPermissions.value is an array before calling includes
    return Array.isArray(userPermissions.value) && userPermissions.value.includes('event:delete')
  })

  // Actions
  const fetchUserPermissions = async () => {
    const authStore = useAuthStore()
    if (!authStore.user?.id) {
      console.log('No user ID available, skipping permission fetch')
      userPermissions.value = []
      return []
    }

    loading.value = true
    try {
      const permissionsService = usePermissionsService()
      const response = await permissionsService.getMemberPermissionsUI(authStore.user.id)
      // Ensure we have an array even if the API returns something else
      userPermissions.value = Array.isArray(response) ? response : []
      return userPermissions.value
    } catch (err) {
      error.value = err.message
      console.error('Error fetching user permissions:', err)
      // Initialize with empty array to prevent further errors
      userPermissions.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  const fetchRolePermissions = async (role) => {
    loading.value = true
    try {
      const permissionsService = usePermissionsService()
      const response = await permissionsService.getPermissionsByRole(role)
      rolePermissions.value[role] = response
      return response
    } catch (err) {
      error.value = err.message
      console.error('Error fetching role permissions:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchOrganizationMemberPermissions = async (organizationId) => {
    loading.value = true
    try {
      const permissionsService = usePermissionsService()
      const response = await permissionsService.getPermissionsByOrganization(organizationId)
      organizationMemberPermissions.value[organizationId] = response
      return response
    } catch (err) {
      error.value = err.message
      console.error('Error fetching organization member permissions:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    userPermissions,
    rolePermissions,
    organizationMemberPermissions,
    loading,
    error,
    
    // Getters
    hasPermission,
    canManageEvents,
    canCreateEvent,
    canUpdateEvent,
    canDeleteEvent,
    
    // Actions
    fetchUserPermissions,
    fetchRolePermissions,
    fetchOrganizationMemberPermissions
  }
})
