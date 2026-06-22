<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold">Image Gallery</h2>
      <div class="flex space-x-4">
        <div class="relative">
          <input type="text" placeholder="Search images..." 
                 class="pl-10 pr-4 py-2 border rounded-lg focus:ring-primary focus:border-primary"
                 v-model="searchQuery">
          <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
        </div>
        <select class="border rounded-lg px-4 py-2 focus:ring-primary focus:border-primary"
                v-model="filter">
          <option value="all">All Images</option>
          <option value="recent">Recent</option>
          <option value="favorites">Favorites</option>
        </select>
      </div>
    </div>

    <!-- Conditional Virtual Scrolling Image Grid -->
    <div v-if="filteredImages.length > 6" class="h-[calc(100vh-12rem)] relative">
      <DynamicScroller
        :items="filteredImages"
        :min-item-size="300"
        class="scroller absolute inset-0"
      >
        <template #default="{ item: image, index, active }">
          <DynamicScrollerItem
            :item="image"
            :active="active"
            :size-dependencies="[image.url]"
            :data-index="index"
            class="group relative bg-white rounded-lg shadow overflow-hidden transition-shadow duration-200 hover:shadow-lg"
          >
            <div class="relative h-[300px] bg-gray-100">
              <!-- Enhanced image loading with blur placeholder -->
              <div class="absolute inset-0">
                <img 
                  :src="image.url" 
                  :alt="image.prompt"
                  loading="lazy"
                  decoding="async"
                  :class="[
                    'object-cover w-full h-full transition-transform duration-200',
                    'group-hover:scale-105',
                    imageLoadStatus[index] ? 'opacity-100' : 'opacity-0'
                  ]"
                  @load="handleImageLoad(index)"
                  @error="handleImageError(index)"
                >
                <!-- Loading placeholder -->
                <div 
                  v-if="!imageLoadStatus[index]"
                  class="absolute inset-0 bg-gray-200 animate-pulse"
                ></div>
              </div>
            </div>
            
            <!-- Overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <div class="absolute bottom-0 left-0 right-0 p-4">
                <p class="text-white text-sm line-clamp-2 mb-2">{{ image.prompt }}</p>
                <div class="flex justify-between items-center">
                  <div class="flex space-x-2">
                    <button class="text-white hover:text-primary-light">
                      <i class="fas fa-download"></i>
                    </button>
                    <button class="text-white hover:text-primary-light">
                      <i class="fas fa-share"></i>
                    </button>
                    <button class="text-white hover:text-primary-light" @click="toggleFavorite(image)">
                      <i :class="image.favorite ? 'fas fa-heart text-red-100' : 'far fa-heart'"></i>
                    </button>
                  </div>
                  <span class="text-white text-sm">{{ image.date }}</span>
                </div>
              </div>
            </div>
          </DynamicScrollerItem>
        </template>
      </DynamicScroller>
    </div>

    <!-- Simple grid for few images -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      <div 
        v-for="(image, index) in filteredImages" 
        :key="image.id"
        class="group relative bg-white rounded-lg shadow overflow-hidden transition-shadow duration-200 hover:shadow-lg"
      >
        <div class="relative h-[300px] bg-gray-100">
          <!-- Enhanced image loading with blur placeholder -->
          <div class="absolute inset-0">
            <img 
              :src="image.url" 
              :alt="image.prompt"
              loading="lazy"
              decoding="async"
              :class="[
                'object-cover w-full h-full transition-transform duration-200',
                'group-hover:scale-105',
                imageLoadStatus[index] ? 'opacity-100' : 'opacity-0'
              ]"
              @load="handleImageLoad(index)"
              @error="handleImageError(index)"
            >
            <!-- Loading placeholder -->
            <div 
              v-if="!imageLoadStatus[index]"
              class="absolute inset-0 bg-gray-200 animate-pulse"
            ></div>
          </div>
        </div>
        
        <!-- Overlay -->
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div class="absolute bottom-0 left-0 right-0 p-4">
            <p class="text-white text-sm line-clamp-2 mb-2">{{ image.prompt }}</p>
            <div class="flex justify-between items-center">
              <div class="flex space-x-2">
                <button class="text-white hover:text-primary-light">
                  <i class="fas fa-download"></i>
                </button>
                <button class="text-white hover:text-primary-light">
                  <i class="fas fa-share"></i>
                </button>
                <button class="text-white hover:text-primary-light" @click="toggleFavorite(image)">
                  <i :class="image.favorite ? 'fas fa-heart text-red-100' : 'far fa-heart'"></i>
                </button>
              </div>
              <span class="text-white text-sm">{{ image.date }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Load More -->
    <div class="flex justify-center mt-6" v-if="hasMore">
      <button 
        class="text-white bg-primary hover:bg-primary-dark px-4 py-2 rounded transition-colors duration-200 disabled:opacity-50 flex items-center space-x-2" 
        @click="loadMore" 
        :disabled="loading"
      >
        <span>Load More</span>
        <i v-if="loading" class="fas fa-spinner fa-spin"></i>
      </button>
    </div>
    <div v-else class="text-center text-gray-500 mt-6">
      All images have been loaded
    </div>

    <!-- Share Modal -->
    <div v-if="showShareModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">Share Image</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Share Link</label>
            <div class="mt-1 flex rounded-md shadow-sm">
              <input type="text" :value="selectedImage?.shareUrl" readonly
                     class="flex-1 input-primary rounded-r-none">
              <button class="px-4 py-2 bg-primary text-white rounded-r-md hover:bg-primary-dark" @click="copyShareLink">
                Copy
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Social Media</label>
            <div class="flex space-x-4">
              <button class="p-2 rounded-full bg-blue-500 text-white hover:bg-blue-600" @click="shareToSocial('twitter')">
                <i class="fab fa-twitter"></i>
              </button>
              <button class="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700" @click="shareToSocial('facebook')">
                <i class="fab fa-facebook"></i>
              </button>
              <button class="p-2 rounded-full bg-pink-500 text-white hover:bg-pink-600" @click="shareToSocial('instagram')">
                <i class="fab fa-instagram"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button class="text-gray-600 hover:text-gray-900" @click="showShareModal = false">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { handleError } from '@/utils/errorHandler'
import { computed, ref } from 'vue'
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import image1 from '../../assets/1.jpg'
import image2 from '../../assets/2.webp'
import image3 from '../../assets/3.jpg'

export default {
  name: 'ImageGallery',
  components: {
    DynamicScroller,
    DynamicScrollerItem
  },
  data() {
    return {
      images: [
        {
          id: 1,
          url: image1,
          prompt: 'A serene landscape with mountains and a lake at sunset',
          date: '2024-02-25',
          favorite: true,
          shareUrl: 'https://example.com/share/1'
        },
        {
          id: 2,
          url: image2,
          prompt: 'Abstract digital art with vibrant colors',
          date: '2024-02-24',
          favorite: false,
          shareUrl: 'https://example.com/share/2'
        },
        {
          id: 3,
          url: image3,
          prompt: 'Abstract digital art with vibrant colors',
          date: '2024-02-24',
          favorite: false,
          shareUrl: 'https://example.com/share/2'
        }
      ],
      nextPage: 2,
      hasMore: true,
      showShareModal: false,
      selectedImage: null,
      loading: false,
      searchQuery: '',
      filter: 'all',
      imageLoadStatus: {},
      imageErrors: {}
    }
  },
  computed: {
    filteredImages() {
      let filtered = [...this.images]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(image => 
          image.prompt.toLowerCase().includes(query)
        )
      }
      
      if (this.filter === 'favorites') {
        filtered = filtered.filter(image => image.favorite)
      }
      
      return filtered
    }
  },
  methods: {
    handleImageLoad(index) {
      this.imageLoadStatus[index] = true
    },
    handleImageError(index) {
      this.imageErrors[index] = true
      this.imageLoadStatus[index] = true
      handleError(new Error('Failed to load image'), 'Image Load')
    },
    async toggleFavorite(image) {
      const index = this.images.findIndex(img => img.id === image.id)
      if (index === -1) return
      
      const originalState = this.images[index].favorite
      
      try {
        // Optimistic update
        this.images[index].favorite = !originalState
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
      } catch (error) {
        // Rollback on error
        this.images[index].favorite = originalState
        handleError(error, 'Toggle Favorite', {
          message: 'Failed to update favorite status. Please try again.'
        })
      }
    },
    async loadMore() {
      if (this.loading || !this.hasMore) return;
      
      try {
        this.loading = true;
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate new images
        const newImages = [
          {
            id: this.images.length + 1,
            url: image1,
            prompt: 'New landscape image ' + this.nextPage,
            date: '2024-02-23',
            favorite: false,
            shareUrl: 'https://example.com/share/' + (this.images.length + 1)
          },
          {
            id: this.images.length + 2,
            url: image2,
            prompt: 'New abstract art ' + this.nextPage,
            date: '2024-02-23',
            favorite: false,
            shareUrl: 'https://example.com/share/' + (this.images.length + 2)
          },
          {
            id: this.images.length + 3,
            url: image3,
            prompt: 'New digital art ' + this.nextPage,
            date: '2024-02-23',
            favorite: false,
            shareUrl: 'https://example.com/share/' + (this.images.length + 3)
          }
        ];
        
        // Add new images to the list
        this.images.push(...newImages);
        
        // Update pagination
        this.nextPage++;
        this.hasMore = this.nextPage < 5; // Limit to 4 pages total
        
      } catch (error) {
        handleError(error, 'Load More', {
          message: 'Failed to load more images. Please try again.'
        });
      } finally {
        this.loading = false;
      }
    },
    async fetchImages() {
      try {
        this.loading = true;
        // Implement Firebase Storage fetch
        await new Promise(resolve => setTimeout(resolve, 1000));
        // Simulated error for testing
        if (!this.images || this.images.length === 0) {
          throw new Error('No images found');
        }
      } catch (error) {
        handleError(error, 'Fetch Images', {
          message: 'Failed to load your images. Please check your connection and try again.'
        });
      } finally {
        this.loading = false;
      }
    },

    async copyShareLink() {
      try {
        if (!this.selectedImage?.shareUrl) {
          throw new Error('Share URL not found');
        }
        await navigator.clipboard.writeText(this.selectedImage.shareUrl);
        // Show success toast
        this.$toast.success('Link copied to clipboard!');
      } catch (error) {
        handleError(error, 'Copy Link', {
          message: 'Failed to copy link. Please try again.'
        });
      }
    },

    async shareImage(image) {
      try {
        this.selectedImage = image;
        if (!this.selectedImage?.shareUrl) {
          throw new Error('Share URL not found');
        }
        this.showShareModal = true;
      } catch (error) {
        handleError(error, 'Share Image', {
          message: 'Failed to prepare image for sharing. Please try again.'
        });
      }
    },

    async shareToSocial(platform) {
      try {
        if (!this.selectedImage?.shareUrl) {
          throw new Error('Share URL not found');
        }

        const shareData = {
          title: 'Check out my AI-generated image!',
          text: this.selectedImage.prompt,
          url: this.selectedImage.shareUrl
        };

        if (navigator.share && platform === 'native') {
          await navigator.share(shareData);
        } else {
          // Implement platform-specific sharing
          const platformUrls = {
            twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareData.text)}&url=${encodeURIComponent(shareData.url)}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareData.url)}`,
            instagram: null // Instagram doesn't support direct sharing via URL
          };

          const shareUrl = platformUrls[platform];
          if (!shareUrl) {
            throw new Error(`Sharing to ${platform} is not supported`);
          }

          window.open(shareUrl, '_blank');
        }
      } catch (error) {
        // Don't show error for user cancellation
        if (error.name === 'AbortError') return;
        
        handleError(error, 'Social Share', {
          message: `Failed to share to ${platform}. Please try again.`
        });
      }
    }
  },
  mounted() {
    this.fetchImages();
  }
}
</script>

<style>
/* Scroller styles */
.scroller {
  height: 100%;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.vue-recycle-scroller {
}

.vue-recycle-scroller__item-wrapper {
  display: grid !important;
  grid-template-columns: repeat(3, 1fr) !important;
  gap: 1.5rem !important;
  padding: 1.5rem !important;
  width: 100% !important;
}

.vue-recycle-scroller__item-view {
  width: 100% !important;
  transform: none !important;
  margin-bottom: 0 !important;
  height: auto !important;
}

@media (max-width: 1024px) {
  .vue-recycle-scroller__item-wrapper {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 640px) {
  .vue-recycle-scroller__item-wrapper {
    grid-template-columns: repeat(1, 1fr) !important;
  }
}

/* Rest of the styles remain unchanged */
.grid {
  overflow: visible;
}

/* Smooth image loading transition */
img {
  transition: transform 0.2s ease-in-out;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
</style>
