<template>
  <div class="min-h-screen bg-gray-100">
    <Sidebar v-if="showSidebar" :is-open="sidebarOpen" @toggle="handleSidebarToggle" />
    <main 
      class="min-h-screen transition-all duration-300 ease-in-out"
      :class="{ 'pl-64': showSidebar && sidebarOpen }"
    >
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { computed, ref, onMounted } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'App',
  components: {
    Sidebar
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()
    const sidebarOpen = ref(true)

    // Initialize auth on app mount only if not already initialized
    onMounted(async () => {
      if (!authStore.auth_initialized) {
        await authStore.initAuth()
      }
    })

    const showSidebar = computed(() => {
      // Hide sidebar for pending organizations, auth pages, and standalone pages
      return authStore.user && 
             !['/', '/login', '/register', '/pending-approval'].includes(route.path) &&
             !(authStore.is_organization && authStore.organization?.status === 'pending') &&
             !route.meta.standalone
    })

    const handleSidebarToggle = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    return {
      showSidebar,
      sidebarOpen,
      handleSidebarToggle
    }
  }
}
</script>

<style>
@import '@/assets/base.css';
@import '@/assets/main.css';

:root {
  --primary: #2A0944;
  --primary-light: #3B0B63;
  --primary-dark: #1A0429;
}

/* Global button styles */
.v-btn {
  text-transform: none !important;
  letter-spacing: normal !important;
  font-weight: 500 !important;
}

.v-btn--elevated {
  box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
}

.v-btn--elevated:hover {
  box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
}

/* Primary button specific styles */
.v-btn.v-btn--variant-elevated.v-theme--light.v-btn--density-default.v-btn--size-default.v-btn--color-primary {
  background: linear-gradient(135deg, #1867C0, #1E88E5) !important;
  transition: all 0.3s ease;
}

.v-btn.v-btn--variant-elevated.v-theme--light.v-btn--density-default.v-btn--size-default.v-btn--color-primary:hover {
  background: linear-gradient(135deg, #1565C0, #1976D2) !important;
  transform: translateY(-1px);
}

/* Form control styles */
.v-field--variant-outlined .v-field__outline {
  --v-field-border-width: 1.5px !important;
}

.v-field--variant-outlined:hover .v-field__outline {
  --v-field-border-width: 2px !important;
}

.v-field--focused .v-field__outline {
  --v-field-border-width: 2px !important;
}
</style>
