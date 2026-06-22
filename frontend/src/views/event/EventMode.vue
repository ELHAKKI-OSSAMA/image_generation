<template>
  <div class="event-mode">
    <!-- Event Header -->
    <div class="bg-primary p-4 text-white">
      <div class="container mx-auto">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-semibold">{{ event_data.name }}</h1>
            <p class="text-sm opacity-80">{{ event_data.organization_name }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm">{{ formatted_date }}</p>
            <p class="text-sm opacity-80">{{ attendees_count }} Attendees</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="container mx-auto">
        <div class="flex space-x-4 p-2">
          <router-link 
            to="capture" 
            class="px-4 py-2 rounded-lg hover:bg-gray-100"
            :class="{ 'bg-primary text-white': $route.path.includes('capture') }"
          >
            Quick Capture
          </router-link>
          <router-link 
            to="gallery" 
            class="px-4 py-2 rounded-lg hover:bg-gray-100"
            :class="{ 'bg-primary text-white': $route.path.includes('gallery') }"
          >
            Event Gallery
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Event Content -->
    <div class="container mx-auto p-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import { useOrganizationStore } from '@/stores/organization'

export default {
  name: 'EventMode',
  data() {
    return {
      event_data: {
        name: '',
        organization_name: '',
        date: null,
        attendees_count: 0
      }
    }
  },
  computed: {
    formatted_date() {
      if (!this.event_data.date) return ''
      return new Date(this.event_data.date).toLocaleDateString()
    },
    attendees_count() {
      return this.event_data.attendees_count
    }
  },
  methods: {
    async fetch_event_data() {
      const store = useOrganizationStore()
      const event_id = this.$route.params.id
      await store.set_current_event(event_id)
      // Update local data from store
      if (store.current_event) {
        this.event_data = {
          name: store.current_event.name,
          organization_name: store.organization?.name || '',
          date: store.current_event.date,
          attendees_count: store.current_event.attendees_count
        }
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
