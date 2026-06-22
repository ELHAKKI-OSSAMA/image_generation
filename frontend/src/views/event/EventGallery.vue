<template>
  <div class="event-gallery">
    <!-- Gallery Controls -->
    <div class="mb-6 flex flex-wrap gap-4 items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="relative">
          <input 
            type="text" 
            v-model="search_query"
            placeholder="Search photos..."
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select 
          v-model="sort_by"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
        >
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="likes">Most Liked</option>
        </select>
      </div>
      
      <div class="flex items-center gap-2">
        <button 
          @click="view_mode = 'grid'"
          class="p-2 rounded-lg"
          :class="view_mode === 'grid' ? 'bg-primary text-white' : 'text-gray-600 hover:bg-gray-100'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
        </button>
        <button 
          @click="view_mode = 'list'"
          class="p-2 rounded-lg"
          :class="view_mode === 'list' ? 'bg-primary text-white' : 'text-gray-600 hover:bg-gray-100'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!photos.length" class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900">No Photos Yet</h3>
      <p class="mt-1 text-sm text-gray-500">Start capturing photos to see them appear here.</p>
      <button 
        @click="$router.push('capture')"
        class="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors duration-200"
      >
        Take Photos
      </button>
    </div>

    <!-- Grid View -->
    <div v-else-if="view_mode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="photo in filtered_photos" 
        :key="photo.id"
        class="relative group bg-white rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-200"
      >
        <!-- Photo -->
        <img 
          :src="photo.url" 
          :alt="photo.caption || 'Event photo'"
          class="w-full aspect-square object-cover"
          @click="open_photo_detail(photo)"
        >
        
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity duration-200">
          <div class="absolute bottom-0 left-0 right-0 p-4 text-white transform translate-y-full group-hover:translate-y-0 transition-transform duration-200">
            <div class="flex justify-between items-center">
              <span class="text-sm">{{ format_date(photo.created_at) }}</span>
              <div class="flex items-center gap-3">
                <button 
                  @click.stop="toggle_like(photo)"
                  class="hover:text-red-500 transition-colors duration-200"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" :class="{ 'fill-current text-red-500': photo.liked }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
                <button 
                  @click.stop="download_photo(photo)"
                  class="hover:text-blue-500 transition-colors duration-200"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="space-y-4">
      <div 
        v-for="photo in filtered_photos" 
        :key="photo.id"
        class="flex items-center gap-4 p-4 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200"
      >
        <img 
          :src="photo.url" 
          :alt="photo.caption || 'Event photo'"
          class="w-24 h-24 object-cover rounded-lg cursor-pointer"
          @click="open_photo_detail(photo)"
        >
        <div class="flex-grow">
          <p class="text-sm text-gray-500">{{ format_date(photo.created_at) }}</p>
          <p v-if="photo.caption" class="mt-1 text-gray-700">{{ photo.caption }}</p>
        </div>
        <div class="flex items-center gap-3">
          <button 
            @click="toggle_like(photo)"
            class="p-2 rounded-full hover:bg-gray-100 transition-colors duration-200"
            :class="{ 'text-red-500': photo.liked }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" :class="{ 'fill-current': photo.liked }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          <button 
            @click="download_photo(photo)"
            class="p-2 rounded-full hover:bg-gray-100 transition-colors duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Photo Detail Modal -->
    <div 
      v-if="selected_photo"
      class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
      @click="close_photo_detail"
    >
      <div 
        class="relative max-w-4xl w-full mx-4 bg-white rounded-xl overflow-hidden"
        @click.stop
      >
        <img 
          :src="selected_photo.url" 
          :alt="selected_photo.caption || 'Event photo'"
          class="w-full"
        >
        <div class="absolute top-4 right-4">
          <button 
            @click="close_photo_detail"
            class="p-2 bg-black bg-opacity-50 rounded-full text-white hover:bg-opacity-75 transition-opacity duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useOrganizationStore } from '@/stores/organization'

export default {
  name: 'EventGallery',
  data() {
    return {
      loading: true,
      photos: [],
      search_query: '',
      sort_by: 'newest',
      view_mode: 'grid',
      selected_photo: null
    }
  },
  computed: {
    filtered_photos() {
      let filtered = [...this.photos]
      
      // Apply search filter
      if (this.search_query) {
        const query = this.search_query.toLowerCase()
        filtered = filtered.filter(photo => 
          photo.caption?.toLowerCase().includes(query)
        )
      }
      
      // Apply sorting
      filtered.sort((a, b) => {
        switch (this.sort_by) {
          case 'oldest':
            return new Date(a.created_at) - new Date(b.created_at)
          case 'likes':
            return (b.likes || 0) - (a.likes || 0)
          default: // newest
            return new Date(b.created_at) - new Date(a.created_at)
        }
      })
      
      return filtered
    }
  },
  methods: {
    async fetch_photos() {
      this.loading = true
      try {
        const store = useOrganizationStore()
        const event_id = this.$route.params.id
        this.photos = await store.fetch_event_photos(event_id)
      } catch (error) {
        console.error('Error fetching photos:', error)
        // TODO: Show error notification
      } finally {
        this.loading = false
      }
    },
    format_date(date) {
      return new Date(date).toLocaleDateString()
    },
    async toggle_like(photo) {
      try {
        const store = useOrganizationStore()
        await store.toggle_photo_like(photo.id)
        photo.liked = !photo.liked
        photo.likes = (photo.likes || 0) + (photo.liked ? 1 : -1)
      } catch (error) {
        console.error('Error toggling like:', error)
        // TODO: Show error notification
      }
    },
    download_photo(photo) {
      const link = document.createElement('a')
      link.href = photo.url
      link.download = `event-photo-${photo.id}.jpg`
      link.click()
    },
    open_photo_detail(photo) {
      this.selected_photo = photo
      document.body.style.overflow = 'hidden'
    },
    close_photo_detail() {
      this.selected_photo = null
      document.body.style.overflow = ''
    }
  },
  async created() {
    await this.fetch_photos()
  },
  beforeUnmount() {
    document.body.style.overflow = ''
  }
}
</script>
