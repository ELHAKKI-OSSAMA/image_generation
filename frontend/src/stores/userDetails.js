import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'
import { useAuthStore } from './auth'

export const useUserDetailsStore = defineStore('userDetails', {
  state: () => ({
    details: null,
    loading: false,
    error: null
  }),

  getters: {
    userRole: (state) => state.details?.role,
    userPermissions: (state) => state.details?.permissions || {},
    userStatus: (state) => state.details?.status,
    isLoading: (state) => state.loading
  },

  actions: {
    async fetchUserDetails() {
      this.loading = true
      this.error = null
      try {
        const authStore = useAuthStore()
        const response = await axiosInstance.get('/api/v1/user-details', {
          headers: {
            Authorization: `Bearer ${authStore.access_token}`
          }
        })
        this.details = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch user details'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateUserDetails(data) {
      this.loading = true
      this.error = null
      try {
        const authStore = useAuthStore()
        const response = await axiosInstance.put('/api/v1/user-details', data, {
          headers: {
            Authorization: `Bearer ${authStore.access_token}`
          }
        })
        this.details = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update user details'
        throw error
      } finally {
        this.loading = false
      }
    },

    async resetUserDetails() {
      this.loading = true
      this.error = null
      try {
        const authStore = useAuthStore()
        await axiosInstance.delete('/api/v1/user-details', {
          headers: {
            Authorization: `Bearer ${authStore.access_token}`
          }
        })
        // Fetch updated details after reset
        await this.fetchUserDetails()
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to reset user details'
        throw error
      } finally {
        this.loading = false
      }
    },

    clearDetails() {
      this.details = null
      this.error = null
    }
  }
})
