import { useApi } from '@/composables/useApi'

export const useOrganizationSettingsService = () => {
  const api = useApi()

  const getSettings = async (orgId) => {
    const response = await api.get(`/organization_settings/${orgId}`)
    return response.data
  }

  const updateSettings = async (orgId, data) => {
    const response = await api.put(`/organization_settings/${orgId}`, data)
    return response.data
  }

  const uploadAvatar = async (orgId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`/organization_settings/${orgId}/avatar`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }

  return {
    getSettings,
    updateSettings,
    uploadAvatar
  }
}
