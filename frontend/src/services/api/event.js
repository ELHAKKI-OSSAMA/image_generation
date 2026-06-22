import { useApi } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'

export const useEventService = () => {
  const api = useApi()
  const authStore = useAuthStore()

  const getEventsByOrganization = async (id) => {
    try {
      const response = await api.get(`/api/v1/event/organization/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching events by organization:', error)
      throw error
    }
  }

  const getEvents = async () => {
    try {
      const response = await api.get('/api/v1/event/')
      return response.data
    } catch (error) {
      console.error('Error fetching events:', error)
      throw error
    }
  }

  const createEvent = async (eventData) => {
    try {
      const response = await api.post('/api/v1/event/', eventData)
      return response.data
    } catch (error) {
      console.error('Error creating event:', error)
      throw error
    }
  }

  const updateEvent = async (id, eventData) => {
    try {
      const response = await api.put(`/api/v1/event/${id}`, eventData)
      return response.data
    } catch (error) {
      console.error('Error updating event:', error)
      throw error
    }
  }

  const deleteEvent = async (id) => {
    try {
      const response = await api.delete(`/api/v1/event/${id}`)
      return response.data
    } catch (error) {
      console.error('Error deleting event:', error)
      throw error
    }
  }

  const getEventCount = async (organizationId) => {
    try {
      const response = await api.get(`/api/v1/event/organization/${organizationId}/count`);
      return response.data;
    } catch (error) {
      console.error('Error fetching event count:', error);
      throw error;
    }
  };

  // Fetches events for the current authenticated user's organization
  const getOrganizationEvents = async () => {
    try {
      if (!authStore.organization_id) {
        throw new Error('No organization access');
      }
      const response = await api.get(`/api/v1/event/organization/${authStore.organization_id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching events for current organization:', error);
      throw error;
    }
  };

  return {
    getEventsByOrganization,
    getOrganizationEvents,
    getEvents,
    createEvent,
    updateEvent,
    deleteEvent,
    getEventCount
  };
};
