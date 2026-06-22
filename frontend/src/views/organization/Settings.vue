<template>
  <div class="organization-settings">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Organization Settings</h1>
      <p class="mt-1 text-sm text-gray-500">Manage your organization's preferences and configurations.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- Organization Profile -->
      <div class="bg-white rounded-xl shadow-md overflow-hidden">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Organization Profile</h2>
          
          <form @submit.prevent="save_profile" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
                <input 
                  v-model="profile.name"
                  type="text"
                  required
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                <select 
                  v-model="profile.industry"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option value="technology">Technology</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="education">Education</option>
                  <option value="hospitality">Hospitality</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Contact Email</label>
                <input 
                  v-model="profile.contact_email"
                  type="email"
                  required
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input 
                  v-model="profile.phone"
                  type="tel"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea 
                v-model="profile.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
              <textarea 
                v-model="profile.address"
                rows="2"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              ></textarea>
            </div>

            <div class="flex justify-end">
              <button 
                type="submit"
                class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors duration-200"
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
      <!-- Danger Zone -->
      <div class="bg-white rounded-xl shadow-md overflow-hidden">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-red-600 mb-4">Danger Zone</h2>
          
          <div class="space-y-4">
            <div class="flex items-center justify-between py-4 border-t border-gray-200">
              <div>
                <h3 class="text-sm font-medium text-gray-900">Delete Organization</h3>
                <p class="mt-1 text-sm text-gray-500">
                  Once you delete your organization, there is no going back. Please be certain.
                </p>
              </div>
              <button 
                @click="confirm_delete"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Delete Organization
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="show_delete_modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-lg max-w-lg w-full mx-4" @click.stop>
        <div class="p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Delete Organization</h2>
          
          <p class="text-sm text-gray-500 mb-4">
            This action cannot be undone. This will permanently delete your organization, all its events, and remove all associated data.
          </p>

          <form @submit.prevent="delete_organization" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Please type <span class="font-semibold">{{ organization_name }}</span> to confirm
              </label>
              <input 
                v-model="delete_confirmation"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              >
            </div>

            <div class="flex justify-end gap-2">
              <button 
                type="button"
                @click="show_delete_modal = false"
                class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                Cancel
              </button>
              <button 
                type="submit"
                :disabled="delete_confirmation !== organization_name"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                I understand the consequences, delete this organization
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useOrganizationStore } from '@/stores/organization'

export default {
  name: 'OrganizationSettings',
  data() {
    return {
      loading: true,
      profile: {
        name: '',
        industry: '',
        contact_email: '',
        phone: '',
        description: '',
        address: ''
      },
      event_settings: {
        default_type: 'public',
        default_duration: 2,
        require_approval: false,
        auto_gallery: true,
        allow_downloads: true
      },
      show_delete_modal: false,
      delete_confirmation: '',
      organization_name: ''
    }
  },
  methods: {
    async fetch_settings() {
      this.loading = true
      try {
        const store = useOrganizationStore()
        // API call implementation here
        // const settings = await store.fetch_organization_settings()
        
        // Temporary mock data
        const settings = {
          profile: {
            name: 'Test Organization',
            industry: 'technology',
            contact_email: 'contact@test.com',
            phone: '',
            description: '',
            address: ''
          },
          event_settings: {
            default_type: 'public',
            default_duration: 2,
            require_approval: false,
            auto_gallery: true,
            allow_downloads: true
          },
        }
        
        this.profile = settings.profile
        this.event_settings = settings.event_settings
        this.organization_name = settings.profile.name
      } catch (error) {
        console.error('Error fetching settings:', error)
        // TODO: Show error notification
      } finally {
        this.loading = false
      }
    },
    async save_profile() {
      try {
        const store = useOrganizationStore()
        // API call implementation here
        // await store.update_organization_profile(this.profile)
        // TODO: Show success notification
      } catch (error) {
        console.error('Error saving profile:', error)
        // TODO: Show error notification
      }
    },
    async save_event_settings() {
      try {
        const store = useOrganizationStore()
        // API call implementation here
        // await store.update_event_settings(this.event_settings)
        // TODO: Show success notification
      } catch (error) {
        console.error('Error saving event settings:', error)
        // TODO: Show error notification
      }
    },
    confirm_delete() {
      this.show_delete_modal = true
      this.delete_confirmation = ''
    },
    async delete_organization() {
      if (this.delete_confirmation !== this.organization_name) return
      
      try {
        const store = useOrganizationStore()
        // API call implementation here
        // await store.delete_organization()
        
        // Redirect to home page
        this.$router.push('/')
      } catch (error) {
        console.error('Error deleting organization:', error)
        // TODO: Show error notification
      }
    }
  },
  async created() {
    await this.fetch_settings()
  }
}
</script>
