<template>
  <div class="event-detail">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
    </div>

    <template v-else>
      <!-- Event Header -->
      <div class="bg-white rounded-xl shadow-md overflow-hidden mb-6">
        <div class="p-6">
          <div class="flex justify-between items-start">
            <div>
              <h1 class="text-2xl font-semibold text-gray-900">{{ event?.name }}</h1>
              <p class="mt-1 text-sm text-gray-500">{{ formatted_date }}</p>
            </div>
            <div class="flex gap-2">
              <button 
                v-if="event?.status === 'active'"
                @click="start_event"
                class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors duration-200"
              >
                Start Event
              </button>
              <button 
                v-else-if="event?.status === 'live'"
                @click="end_event"
                class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-200"
              >
                End Event
              </button>
              <button 
                @click="edit_mode = true"
                class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Event Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div class="bg-gray-50 p-4 rounded-lg">
              <div class="text-sm text-gray-500">Total Photos</div>
              <div class="mt-1 text-2xl font-semibold">{{ event_stats?.total_photos || 0 }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <div class="text-sm text-gray-500">Total Attendees</div>
              <div class="mt-1 text-2xl font-semibold">{{ event_stats?.total_attendees || 0 }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <div class="text-sm text-gray-500">Total Likes</div>
              <div class="mt-1 text-2xl font-semibold">{{ event_stats?.total_likes || 0 }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Event Settings -->
      <div class="bg-white rounded-xl shadow-md overflow-hidden mb-6">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Event Settings</h2>
          
          <form v-if="edit_mode" @submit.prevent="save_event" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
              <input 
                v-model="form.name"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                required
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input 
                v-model="form.date"
                type="datetime-local"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                required
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea 
                v-model="form.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
              <select 
                v-model="form.type"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
                <option value="invitation">Invitation Only</option>
              </select>
            </div>

            <div class="flex justify-end gap-2">
              <button 
                type="button"
                @click="cancel_edit"
                class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                Cancel
              </button>
              <button 
                type="submit"
                class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors duration-200"
              >
                Save Changes
              </button>
            </div>
          </form>

          <div v-else class="space-y-4">
            <div>
              <div class="text-sm font-medium text-gray-500">Event Type</div>
              <div class="mt-1">{{ event?.type || 'Not specified' }}</div>
            </div>
            
            <div>
              <div class="text-sm font-medium text-gray-500">Description</div>
              <div class="mt-1">{{ event?.description || 'No description provided' }}</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-500">Access Code</div>
              <div class="mt-1 flex items-center gap-2">
                <code class="px-2 py-1 bg-gray-100 rounded">{{ event?.access_code || 'Not generated' }}</code>
                <button 
                  @click="generate_access_code"
                  class="text-primary hover:text-primary-dark transition-colors duration-200"
                >
                  Generate New
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-xl shadow-md overflow-hidden mb-6">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button 
              @click="$router.push(`/event/${event?.id}/capture`)"
              class="p-4 text-center border border-gray-200 rounded-lg hover:border-primary hover:text-primary transition-all duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Quick Capture</span>
            </button>
            
            <button 
              @click="$router.push(`/event/${event?.id}/gallery`)"
              class="p-4 text-center border border-gray-200 rounded-lg hover:border-primary hover:text-primary transition-all duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>View Gallery</span>
            </button>
            
            <button 
              @click="download_photos"
              class="p-4 text-center border border-gray-200 rounded-lg hover:border-primary hover:text-primary transition-all duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Download All</span>
            </button>
            
            <button 
              @click="share_event"
              class="p-4 text-center border border-gray-200 rounded-lg hover:border-primary hover:text-primary transition-all duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
              <span>Share Event</span>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { useOrganizationStore } from '@/stores/organization'

export default {
  name: 'EventDetail',
  data() {
    return {
      loading: true,
      edit_mode: false,
      form: {
        name: '',
        date: '',
        description: '',
        type: 'public'
      }
    }
  },
  computed: {
    event() {
      const store = useOrganizationStore()
      return store.current_event
    },
    event_stats() {
      const store = useOrganizationStore()
      return store.event_stats
    },
    formatted_date() {
      if (!this.event?.date) return ''
      return new Date(this.event.date).toLocaleString()
    }
  },
  methods: {
    async fetch_event_data() {
      this.loading = true
      try {
        const store = useOrganizationStore()
        const event_id = this.$route.params.id
        await store.set_current_event(event_id)
        
        // Initialize form with current event data
        if (store.current_event) {
          this.form = {
            name: store.current_event.name,
            date: store.current_event.date,
            description: store.current_event.description || '',
            type: store.current_event.type || 'public'
          }
        }
      } catch (error) {
        console.error('Error fetching event:', error)
        // TODO: Show error notification
      } finally {
        this.loading = false
      }
    },
    async save_event() {
      try {
        const store = useOrganizationStore()
        await store.update_event(this.event.id, this.form)
        this.edit_mode = false
        // TODO: Show success notification
      } catch (error) {
        console.error('Error updating event:', error)
        // TODO: Show error notification
      }
    },
    cancel_edit() {
      this.edit_mode = false
      // Reset form to current event data
      if (this.event) {
        this.form = {
          name: this.event.name,
          date: this.event.date,
          description: this.event.description || '',
          type: this.event.type || 'public'
        }
      }
    },
    async start_event() {
      try {
        const store = useOrganizationStore()
        await store.update_event(this.event.id, { status: 'live' })
        // TODO: Show success notification
      } catch (error) {
        console.error('Error starting event:', error)
        // TODO: Show error notification
      }
    },
    async end_event() {
      try {
        const store = useOrganizationStore()
        await store.update_event(this.event.id, { status: 'completed' })
        // TODO: Show success notification
      } catch (error) {
        console.error('Error ending event:', error)
        // TODO: Show error notification
      }
    },
    async generate_access_code() {
      try {
        const store = useOrganizationStore()
        const access_code = Math.random().toString(36).substring(2, 8).toUpperCase()
        await store.update_event(this.event.id, { access_code })
        // TODO: Show success notification
      } catch (error) {
        console.error('Error generating access code:', error)
        // TODO: Show error notification
      }
    },
    async download_photos() {
      // TODO: Implement batch photo download
      console.log('Download photos')
    },
    share_event() {
      const url = `${window.location.origin}/event/${this.event.id}`
      if (navigator.share) {
        navigator.share({
          title: this.event.name,
          text: `Join our event: ${this.event.name}`,
          url
        }).catch(console.error)
      } else {
        navigator.clipboard.writeText(url)
        // TODO: Show success notification
      }
    }
  },
  async created() {
    await this.fetch_event_data()
  },
  watch: {
    '$route.params.id': {
      handler: 'fetch_event_data',
      immediate: true
    }
  }
}
</script>
