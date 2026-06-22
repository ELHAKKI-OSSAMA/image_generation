<template>
  <button 
    v-if="!isFullscreen"
    @click="openFullscreen" 
    class="fullscreen-button group flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-medium relative overflow-hidden"
    :class="{ 'pulse-animation': animate }"
    :title="title || 'Open in a new window'"
    @mouseenter="animate = true"
    @mouseleave="animate = false"
  >
    <span class="absolute inset-0 w-full h-full bg-gradient-to-r from-blue-400/20 to-indigo-500/20 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></span>
    <svg class="w-5 h-5 relative z-10 transform group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
    </svg>
    <span class="relative z-10">{{ text || 'Open Fullscreen' }}</span>
  </button>
</template>

<script>
export default {
  name: 'FullscreenButton',
  props: {
    route: {
      type: String,
      default: '/fullscreen-image-generation'
    },
    text: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      animate: false
    }
  },
  computed :{
    isFullscreen () {
      return window.location.pathname.includes('fullscreen')
    }
  },
  methods: {
    openFullscreen() {
      // Using window.open to open the route in a new tab
      // No query parameters are passed to ensure we rely on cookies for auth
      window.open(this.route, '_blank');
    }
  }
}
</script>

<style scoped>
.fullscreen-button {
  position: relative;
  overflow: hidden;
}

.fullscreen-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 70%);
  opacity: 0;
  transition: opacity 0.5s;
}

.fullscreen-button:active::after {
  opacity: 0.3;
  transition: 0s;
}

.pulse-animation {
  animation: pulse 1.5s ease-in-out;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(66, 153, 225, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(66, 153, 225, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(66, 153, 225, 0);
  }
}
</style>
