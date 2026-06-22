import { useApi } from '@/composables/useApi'

export const usePermissionsService = () => {
  const api = useApi()

  const getOrganizationMemberInfo = async (id) => {
    try {
      const response = await api.get(`/api/v1/permissions/organization-member-info/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching organization member info:', error)
      throw error
    }
  }

  const getMemberPermissions = async (id) => {
    try {
      const response = await api.get(`/api/v1/permissions/organization-member/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching member permissions:', error)
      throw error
    }
  }

  const getMembersByOrganization = async (organizationId) => {
    try {
      const response = await api.get(`/api/v1/permissions/organization-members-info/${organizationId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching members by organization:', error)
      throw error
    }
  }

  const getPermissionsByOrganization = async (organizationId) => {
    try {
      const response = await api.get(`/api/v1/permissions/organization-members/${organizationId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching permissions by organization:', error)
      throw error
    }
  }

  const getPermissionsById = async (id) => {
    try {
      const response = await api.get(`/api/v1/permissions/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching permissions by id:', error)
      throw error
    }
  }

  const getPermissionsByRole = async (role) => {
    try {
      const response = await api.get(`/api/v1/permissions/role/${role}`)
      return response.data
    } catch (error) {
      console.error('Error fetching permissions by role:', error)
      throw error
    }
  }

  const getPermissions = async () => {
    try {
      const response = await api.get('/api/v1/permissions/')
      return response.data
    } catch (error) {
      console.error('Error fetching permissions:', error)
      throw error
    }
  }

  const getMemberPermissionsUI = async (id) => {
    try {
      const response = await api.get(`/api/v1/organization/member/permissions`)
      // Ensure we return an array even if the API returns something else
      return Array.isArray(response.data) ? response.data : []
    } catch (error) {
      console.error('Error fetching member permissions UI:', error)
      // Return empty array on error to prevent further errors
      return []
    }
  }

  const createPermission = async (permissionData) => {
    try {
      const response = await api.post('/api/v1/permissions/', permissionData)
      return response.data
    } catch (error) {
      console.error('Error creating permission:', error)
      throw error
    }
  }

  return {
    getOrganizationMemberInfo,
    getMemberPermissions,
    getMembersByOrganization,
    getPermissionsByOrganization,
    getPermissionsById,
    getPermissionsByRole,
    getPermissions,
    getMemberPermissionsUI,
    createPermission
  }
}
