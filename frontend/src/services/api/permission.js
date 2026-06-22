import axiosInstance from '@/plugins/axios'

/**
 * Service for managing permissions
 */
export const usePermissionService = () => {
  /**
   * Get all available permissions
   * @returns {Promise<Array>} List of permissions
   */
  const getPermissions = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/permissions/')
      return response.data
    } catch (error) {
      console.error('Error fetching permissions:', error)
      throw error
    }
  }

  /**
   * Get permissions for a specific role
   * @param {string} role - Role name
   * @returns {Promise<Array>} List of permissions for the role
   */
  const getPermissionsByRole = async (role) => {
    try {
      const response = await axiosInstance.get(`/api/v1/permissions/role/${role}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching permissions for role ${role}:`, error)
      throw error
    }
  }

  /**
   * Get permissions for a specific member
   * @param {string|number} memberId - Member ID
   * @returns {Promise<Object>} Member permissions
   */
  const getMemberPermissions = async (memberId) => {
    try {
      const response = await axiosInstance.get(`/api/v1/permissions/ui/${memberId}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching permissions for member ${memberId}:`, error)
      throw error
    }
  }

  /**
   * Get permissions for all members in an organization
   * @param {string|number} organizationId - Organization ID
   * @returns {Promise<Array>} List of member permissions
   */
  const getOrganizationMemberPermissions = async (organizationId) => {
    try {
      const response = await axiosInstance.get(`/api/v1/permissions/organization-members/${organizationId}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching permissions for organization ${organizationId}:`, error)
      throw error
    }
  }

  /**
   * Update permissions for a member
   * @param {string|number} organizationId - Organization ID
   * @param {string|number} memberId - Member ID
   * @param {Object} permissionsData - Permissions data to update
   * @returns {Promise<Object>} Updated member permissions
   */
  const updateMemberPermissions = async (organizationId, memberId, permissionsData) => {
    try {
      const response = await axiosInstance.post('/api/v1/permissions/', {
        organization_id: organizationId,
        member_id: memberId,
        permissions: permissionsData.permissions,
        custom_permissions: permissionsData.custom_permissions || []
      })
      return response.data
    } catch (error) {
      console.error(`Error updating permissions for member ${memberId}:`, error)
      throw error
    }
  }

  return {
    getPermissions,
    getPermissionsByRole,
    getMemberPermissions,
    getOrganizationMemberPermissions,
    updateMemberPermissions
  }
}
