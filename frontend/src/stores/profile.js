import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'

export const useProfileStore = defineStore('profile', {
  state: () => ({
    profile: null,
    loading: false,
    error: null
  }),

  getters: {
    hasProfile: (state) => !!state.profile,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },

  actions: {
    async fetchProfile() {
      this.loading = true
      this.error = null
      try {
        const response = await axiosInstance.get('/api/v1/profile')
        this.profile = response.data
        console.log("these are the profile info ", this.profile)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch profile'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateProfile(profileData) {
      this.loading = true
      this.error = null
      try {
        const response = await axiosInstance.put('/api/v1/profile', profileData)
        this.profile = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update profile'
        throw error
      } finally {
        this.loading = false
      }
    },

    async uploadAvatar(formData) {
      try {
        // Remove manual Content-Type header - Axios adds it automatically
        const response = await axiosInstance.put('/api/v1/profile/avatar', formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })
        this.profile = response.data
      } catch (error) {
        console.error('Upload error:', error)
        this.error = error.response?.data?.detail || 'Failed to update avatar'
        throw error
      }
    },

    async toggleTwoFactor() {
      this.loading = true
      this.error = null
      try {
        const response = await axiosInstance.post('/api/v1/profile/two-factor')
        this.profile = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to toggle two-factor authentication'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
