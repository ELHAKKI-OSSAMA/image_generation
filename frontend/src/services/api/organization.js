import { useApi } from '@/composables/useApi'

export const useOrganizationService = () => {
  const api = useApi()

  const getOrganizations = async (params = {}) => {
    try {
      const response = await api.get('/api/v1/organizations', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching organizations:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const getOrganization = async (id) => {
    try {
      const response = await api.get(`/api/v1/organizations/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching organization:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const getUserOrganizations = async (userId) => {
    try {
      const response = await api.get(`/api/v1/organizations/user/${userId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching user organizations:', error)
      throw error
    }
  }

  const createOrganization = async (data) => {
    try {
      const response = await api.post('/api/v1/organizations', data)
      return response.data
    } catch (error) {
      console.error('Error creating organization:', error)
      throw error
    }
  }

  const updateOrganization = async (id, data) => {
    try {
      const response = await api.put(`/api/v1/organizations/${id}`, data)
      return response.data
    } catch (error) {
      console.error('Error updating organization:', error)
      throw error
    }
  }

  const deleteOrganization = async (id) => {
    try {
      await api.delete(`/api/v1/organizations/${id}`)
      return true
    } catch (error) {
      console.error('Error deleting organization:', error)
      throw error
    }
  }

  const addMember = async (organizationId, userId, role = 'member') => {
    try {
      const response = await api.post(`/api/v1/organizations/${organizationId}/members`, {
        user_id: userId,
        role
      })
      return response.data
    } catch (error) {
      console.error('Error adding member:', error)
      throw error
    }
  }

  const removeMember = async (organizationId, userId) => {
    try {
      await api.delete(`/api/v1/organizations/${organizationId}/members/${userId}`)
      return true
    } catch (error) {
      console.error('Error removing member:', error)
      throw error
    }
  }

  const getMembers = async (organizationId, params = {}) => {
    try {
      console.log(`API Call: Fetching members for organization ${organizationId}`)
      // Use the endpoint format that matches the backend API
      const url = `/api/v1/organizations/${organizationId}/members`
      console.log('Full Request URL:', api.defaults.baseURL + url)
      
      // Log headers for debugging
      const config = { params }
      console.log('Request headers:', api.defaults.headers)
      
      const response = await api.get(url, config)
      console.log('API Response for members:', response.data)
      return response.data
    } catch (error) {
      console.error('Error fetching members:', error)
      console.error('Error details:', error.response?.data || error.message)
      console.error('Error status:', error.response?.status)
      throw error
    }
  }

  const updateMemberRole = async (organizationId, userId, role) => {
    try {
      const response = await api.put(`/api/v1/organizations/${organizationId}/members/${userId}`, {
        role
      })
      return response.data
    } catch (error) {
      console.error('Error updating member role:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const updateMemberStatus = async (organizationId, userId, status) => {
    try {
      const response = await api.put(`/api/v1/organizations/${organizationId}/members/${userId}`, {
        status
      })
      return response.data
    } catch (error) {
      console.error('Error updating member status:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }
  
  const updateMemberPermissions = async (organizationId, userId, permissionsData) => {
    try {
      console.log(`API Call: Updating permissions for member ${userId} in organization ${organizationId}`)
      const url = `/api/v1/organizations/${organizationId}/members/${userId}/permissions`
      console.log('Full Request URL:', api.defaults.baseURL + url)
      console.log('Request Data:', permissionsData)
      
      const response = await api.put(url, permissionsData)
      console.log('API Response:', response.data)
      return response.data
    } catch (error) {
      console.error('Error updating member permissions:', error)
      console.error('Error details:', error.response?.data || error.message)
      console.error('Error status:', error.response?.status)
      throw error
    }
  }

  const inviteStaffMember = async (organizationId, inviteData) => {
    try {
      console.log(`API Call: Inviting staff member to organization ${organizationId}`)
      const url = `/api/v1/organizations/${organizationId}/members/invite`
      console.log('Full Request URL:', api.defaults.baseURL + url)
      console.log('Request Data:', inviteData)
      
      const response = await api.post(url, inviteData)
      console.log('API Response:', response.data)
      return response.data
    } catch (error) {
      console.error('Error inviting staff member:', error)
      console.error('Error details:', error.response?.data || error.message)
      console.error('Error status:', error.response?.status)
      throw error
    }
  }

  const getOwnedOrganizations = async () => {
    try {
      console.log('Fetching owned organizations')
      // Use the correct endpoint for owned organizations
      const response = await api.get('/api/v1/organizations/owned')
      console.log('Owned organizations response:', response.data)
      return response.data
    } catch (error) {
      console.error('Error fetching owned organizations:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  // Event API methods
  const getEvents = async (organizationId) => {
    try {
      const response = await api.get(`/api/v1/event/organization/${organizationId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching events:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const getEvent = async (organizationId, eventId) => {
    try {
      const response = await api.get(`/api/v1/event/${eventId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching event details:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const createEvent = async (organizationId, eventData) => {
    try {
      const data = {
        ...eventData,
        organization_id: organizationId
      }
      const response = await api.post('/api/v1/event', data)
      return response.data
    } catch (error) {
      console.error('Error creating event:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const updateEvent = async (organizationId, eventId, eventData) => {
    try {
      const response = await api.put(`/api/v1/event/${eventId}`, eventData)
      return response.data
    } catch (error) {
      console.error('Error updating event:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const deleteEvent = async (eventId) => {
    try {
      await api.delete(`/api/v1/event/${eventId}`)
      return true
    } catch (error) {
      console.error('Error deleting event:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  const getEventParticipants = async (eventId) => {
    try {
      const response = await api.get(`/api/v1/event/${eventId}/participants`)
      return response.data
    } catch (error) {
      console.error('Error fetching event participants:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    }
  }

  return {
    getOrganizations,
    getOrganization,
    getUserOrganizations,
    createOrganization,
    updateOrganization,
    deleteOrganization,
    addMember,
    removeMember,
    getMembers,
    updateMemberRole,
    updateMemberStatus,
    updateMemberPermissions,
    inviteStaffMember,
    getOwnedOrganizations,
    getEvents,
    getEvent,
    createEvent,
    updateEvent,
    deleteEvent,
    getEventParticipants
  }
}
