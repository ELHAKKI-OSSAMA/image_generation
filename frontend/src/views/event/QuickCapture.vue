<template>
  <div class="quick-capture">
    <!-- Camera Section -->
    <div class="relative aspect-video max-w-4xl mx-auto bg-gray-900 rounded-xl overflow-hidden">
      <!-- Permission Request -->
      <div v-if="!has_webcam_permission && !webcam_error" 
           class="absolute inset-0 flex items-center justify-center">
        <div class="text-center p-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <h4 class="text-base font-medium text-white mb-2">Camera Access Required</h4>
          <p class="text-sm text-gray-400 mb-4">We need access to your camera to capture photos.</p>
          <button 
            @click="request_webcam_permission"
            class="px-4 py-2 bg-primary text-white rounded-full font-medium shadow-lg hover:bg-primary-dark transition-colors duration-200"
          >
            Enable Camera
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="webcam_error" 
           class="absolute inset-0 flex items-center justify-center">
        <div class="text-center p-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h4 class="text-base font-medium text-white mb-2">Camera Access Error</h4>
          <p class="text-sm text-gray-400 mb-4">{{ webcam_error }}</p>
          <button 
            @click="retry_webcam_permission"
            class="px-4 py-2 bg-primary text-white rounded-full font-medium shadow-lg hover:bg-primary-dark transition-colors duration-200"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Live Camera View -->
      <video 
        v-else-if="!captured_image"
        ref="webcam" 
        class="absolute inset-0 w-full h-full object-cover"
        autoplay
        playsinline
        muted
      ></video>

      <!-- Captured Photo View -->
      <img 
        v-else
        :src="captured_image" 
        class="absolute inset-0 w-full h-full object-cover"
        alt="Captured photo"
      />
      
      <!-- Camera Controls -->
      <div class="absolute bottom-4 left-0 right-0 flex justify-center gap-3">
        <button
          v-if="!captured_image"
          @click="capture_image"
          class="px-6 py-3 bg-primary text-white rounded-full text-lg font-medium shadow-lg hover:bg-primary-dark transition-colors duration-200"
        >
          Take Photo
        </button>
        <button
          v-else
          @click="retake_photo"
          class="px-6 py-3 bg-white text-primary rounded-full text-lg font-medium shadow-lg hover:bg-gray-50 transition-colors duration-200"
        >
          Retake
        </button>
      </div>

      <!-- Event Branding Overlay -->
      <div class="absolute top-4 left-4 bg-black bg-opacity-50 px-3 py-1 rounded-lg">
        <p class="text-white text-sm">{{ event_name }}</p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="captured_image" class="mt-6 flex justify-center gap-4">
      <button
        @click="generate_image"
        class="px-6 py-3 bg-primary text-white rounded-xl text-lg font-medium shadow-lg hover:bg-primary-dark transition-colors duration-200 flex items-center"
      >
        <span>Generate Photo</span>
      </button>
    </div>

    <!-- Generated Image -->
    <div v-if="generated_image" class="mt-8">
      <div class="relative bg-white rounded-xl overflow-hidden max-w-2xl mx-auto shadow-lg">
        <img :src="generated_image" alt="Generated image" class="w-full">
        <div class="absolute top-4 right-4 flex gap-2">
          <button 
            @click="download_image"
            class="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors duration-200"
            title="Download Image"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          <button 
            @click="share_image"
            class="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors duration-200"
            title="Share Image"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
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
  name: 'QuickCapture',
  data() {
    return {
      has_webcam_permission: false,
      webcam_error: null,
      captured_image: null,
      generated_image: null,
      event_name: '',
      stream: null
    }
  },
  methods: {
    async request_webcam_permission() {
      try {
        await this.start_webcam()
        this.has_webcam_permission = true
      } catch (error) {
        this.handle_webcam_error(error)
      }
    },
    async retry_webcam_permission() {
      this.webcam_error = null
      await this.request_webcam_permission()
    },
    async start_webcam() {
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1920 },
            height: { ideal: 1080 },
            facingMode: 'user'
          }
        })
        
        const video = this.$refs.webcam
        if (video) {
          video.srcObject = this.stream
          await video.play()
        }
      } catch (error) {
        this.handle_webcam_error(error)
      }
    },
    handle_webcam_error(error) {
      console.error('Webcam error:', error)
      this.webcam_error = this.get_webcam_error_message(error)
      this.has_webcam_permission = false
    },
    get_webcam_error_message(error) {
      switch (error.name) {
        case 'NotFoundError':
          return 'No camera device found. Please connect a camera and try again.'
        case 'NotAllowedError':
          return 'Camera access denied. Please enable camera access in your browser settings.'
        case 'NotReadableError':
          return 'Camera is in use by another application. Please close other applications using the camera.'
        default:
          return 'An error occurred while accessing the camera. Please try again.'
      }
    },
    capture_image() {
      const video = this.$refs.webcam
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0)
      
      // Add event watermark
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
      ctx.font = '24px sans-serif'
      ctx.fillText(this.event_name, 20, canvas.height - 20)
      
      this.captured_image = canvas.toDataURL('image/jpeg')
    },
    retake_photo() {
      this.captured_image = null
      this.generated_image = null
    },
    async generate_image() {
      // Implementation will use the existing image generation logic
      // but with event-specific settings and branding
    },
    download_image() {
      const link = document.createElement('a')
      link.download = `${this.event_name}-photo.jpg`
      link.href = this.generated_image || this.captured_image
      link.click()
    },
    async share_image() {
      if (navigator.share) {
        try {
          // Convert base64 to blob
          const response = await fetch(this.generated_image || this.captured_image)
          const blob = await response.blob()
          const file = new File([blob], `${this.event_name}-photo.jpg`, { type: 'image/jpeg' })
          
          await navigator.share({
            title: `${this.event_name} Photo`,
            files: [file]
          })
        } catch (error) {
          console.error('Error sharing:', error)
        }
      }
    },
    async fetch_event_data() {
      const store = useOrganizationStore()
      const event_id = this.$route.params.id
      await store.set_current_event(event_id)
      if (store.current_event) {
        this.event_name = store.current_event.name
      }
    }
  },
  async created() {
    await this.fetch_event_data()
  },
  beforeUnmount() {
    // Clean up camera stream
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
    }
  }
}
</script>
