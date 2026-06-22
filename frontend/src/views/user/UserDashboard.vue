<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Top Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Left side -->
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-2xl font-semibold text-gray-900 pl-5">{{ pageTitle }}</h1>
            </div>
          </div>
          <FullscreenButton />
          <!-- Search -->
          <div class="flex-1 flex items-center justify-center px-2 lg:px-6">
            <div class="max-w-lg w-full lg:max-w-xs">
              <label for="search" class="sr-only">Search</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <font-awesome-icon icon="search" class="h-5 w-5 text-gray-400" />
                </div>
                <input 
                  id="search" 
                  name="search" 
                  class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm" 
                  placeholder="Search" 
                  type="search" 
                  v-model="searchQuery"
                  @input="handleSearch"
                >
              </div>
            </div>
          </div>

          <!-- Right side -->
          <div class="flex items-center">
            <!-- Notifications -->
            <button 
              class="p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary relative"
              @click="toggleNotifications"
            >
              <span class="sr-only">View notifications</span>
              <font-awesome-icon icon="bell" class="h-6 w-6" />
              <span 
                v-if="unreadNotifications > 0"
                class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"
              />
            </button>

            <!-- Notifications Dropdown -->
            <div 
              v-if="showNotifications"
              class="origin-top-right absolute right-0 mt-2 w-80 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
              style="top: 4rem;"
            >
              <div class="px-4 py-2 border-b border-gray-200">
                <h3 class="text-sm font-medium text-gray-900">Notifications</h3>
              </div>
              <div class="max-h-96 overflow-y-auto">
                <div v-if="notifications.length === 0" class="px-4 py-3 text-sm text-gray-500">
                  No new notifications
                </div>
                <a
                  v-for="notification in notifications"
                  :key="notification.id"
                  href="#"
                  class="block px-4 py-3 hover:bg-gray-50"
                  :class="{ 'bg-gray-50': !notification.read }"
                >
                  <div class="flex items-center">
                    <div class="flex-shrink-0">
                      <font-awesome-icon 
                        :icon="notification.icon" 
                        class="h-6 w-6 text-primary"
                      />
                    </div>
                    <div class="ml-3">
                      <p class="text-sm font-medium text-gray-900">
                        {{ notification.title }}
                      </p>
                      <p class="text-sm text-gray-500">
                        {{ notification.message }}
                      </p>
                      <p class="mt-1 text-xs text-gray-400">
                        {{ notification.time }}
                      </p>
                    </div>
                  </div>
                </a>
              </div>
            </div>

            <!-- Profile Dropdown -->
            <div class="ml-3 relative" style="z-index: 99999 !important;">
              <button 
                class="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                @click="toggleProfile"
              >
                <span class="sr-only">Open user menu</span>
                <!-- Try multiple approaches for avatar display -->
                <div 
                  v-if="profileStore.profile && profileStore.profile.avatar_url"
                  class="h-8 w-8 rounded-full bg-gray-200 overflow-hidden"
                >
                  <!-- First try with direct URL -->
                  <img
                    v-if="!avatarError"
                    :src="getAvatarUrl(profileStore.profile.avatar_url)"
                    alt="User avatar"
                    class="h-full w-full object-cover"
                    @error="avatarError = true"
                  />
                  <!-- Fallback to Font Awesome icon if image fails -->
                  <font-awesome-icon
                    v-if="avatarError"
                    icon="user-circle"
                    class="h-8 w-8 text-gray-400"
                  />
                </div>
                <font-awesome-icon 
                  v-else 
                  icon="user-circle" 
                  class="h-8 w-8 text-gray-400" 
                />
              </button>

              <!-- Profile Dropdown Menu -->
              <div 
                v-if="showProfile"
                class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
              >
                <router-link 
                  :to="{ name: 'user-profile' }" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Your Profile
                </router-link>
                <router-link 
                  :to="{ name: 'user-settings' }" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Settings
                </router-link>
                <a 
                  href="#" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="handleLogout"
                >
                  Sign out
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">

      <main class="flex-1 p-6">
        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center h-full">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {{ error }}
        </div>

        <!-- Default Dashboard Content -->
        <div v-else-if="$route.path === '/dashboard'" class="grid gap-6 mb-8 md:grid-cols-2 xl:grid-cols-3">
          <!-- Quick Generate Card -->
          <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div class="flex items-center">
              <div class="p-3 rounded-full bg-primary bg-opacity-10">
                <font-awesome-icon icon="magic" class="text-primary text-xl" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-semibold">Quick Generate</h3>
                <p class="text-gray-600">Create new AI-generated images</p>
              </div>
            </div>
            <router-link 
              to="/dashboard/generate"
              class="mt-4 inline-block px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
            >
              Start Generating
            </router-link>
          </div>

          <!-- Gallery Card -->
          <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div class="flex items-center">
              <div class="p-3 rounded-full bg-primary bg-opacity-10">
                <font-awesome-icon icon="images" class="text-primary text-xl" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-semibold">Your Gallery</h3>
                <p class="text-gray-600">View your generated images</p>
              </div>
            </div>
            <router-link 
              to="/dashboard/gallery"
              class="mt-4 inline-block px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
            >
              View Gallery
            </router-link>
          </div>

          <!-- Profile Card -->
          <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div class="flex items-center">
              <div class="p-3 rounded-full bg-primary bg-opacity-10">
                <font-awesome-icon icon="user-circle" class="text-primary text-xl" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-semibold">Profile Settings</h3>
                <p class="text-gray-600">Manage your account</p>
              </div>
            </div>
            <router-link 
              to="/dashboard/profile"
              class="mt-4 inline-block px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
            >
              View Profile
            </router-link>
          </div>
        </div>

        <!-- Router View for Sub-routes -->
        <router-view v-else></router-view>
      </main>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { ref, onMounted } from 'vue'
import FullscreenButton from '../../components/FullscreenButton.vue'

export default {
  name: 'UserDashboard',
  components: {
    FullscreenButton
  },
  setup() {
    const profileStore = useProfileStore();
    const authStore = useAuthStore();
    const avatarError = ref(false);
    
    const loading = ref(false);
    const error = ref(null);
    const pageTitles = {
      '/dashboard': 'Dashboard',
      '/dashboard/generate': 'Generate Image',
      '/dashboard/gallery': 'Gallery',
      '/dashboard/profile': 'Profile Settings'
    };
    const searchQuery = ref('');
    const notifications = ref([]);
    const showNotifications = ref(false);
    const showProfile = ref(false);
    const unreadNotifications = ref(0);
    
    // Get avatar URL helper function
    const getAvatarUrl = (url) => {
      if (!url) return '';
      // If it's already a full URL, return it as is
      if (url.startsWith('http')) return url;
      // Try different base URLs
      // First try with the configured API base URL if available
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      if (apiBaseUrl) return `${apiBaseUrl}${url}`;
      // Otherwise try with localhost:8000
      return `${import.meta.env.VITE_API_URL}${url}`;
    };
    
    // Fetch profile on mount
    onMounted(async () => {
      try {
        await profileStore.fetchProfile();
        console.log('Profile data:', profileStore.profile);
        console.log('Avatar URL:', profileStore.profile?.avatar_url);
      } catch (err) {
        console.error('Error fetching profile:', err);
      }
    });
    
    // Methods
    const handleSearch = () => {
      console.log('Search:', searchQuery.value);
    };
    
    const toggleNotifications = () => {
      showNotifications.value = !showNotifications.value;
      showProfile.value = false;
    };
    
    const toggleProfile = () => {
      showProfile.value = !showProfile.value;
      showNotifications.value = false;
    };
    
    const handleLogout = async () => {
      try {
        await authStore.logout();
        window.location.href = '/login';
      } catch (error) {
        console.error('Logout error:', error);
      }
    };
    
    // Verify user access on mount
    onMounted(() => {
      if (!authStore.user) {
        window.location.href = '/login';
      }
    });
    
    return {
      profileStore,
      authStore,
      avatarError,
      loading,
      error,
      pageTitles,
      searchQuery,
      notifications,
      showNotifications,
      showProfile,
      unreadNotifications,
      getAvatarUrl,
      handleSearch,
      toggleNotifications,
      toggleProfile,
      handleLogout
    };
  },
  data() {
    return {}
  },
  computed: {
    pageTitle() {
      return this.pageTitles[this.$route.path] || 'Dashboard'
    }
  },
  // created hook moved to setup function
}
</script>
