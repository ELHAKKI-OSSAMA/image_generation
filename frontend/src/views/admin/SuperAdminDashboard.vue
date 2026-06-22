<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Top Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Left side -->
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-2xl font-semibold text-gray-900 pl-6">
                {{ pageTitle }}
              </h1>
            </div>
          </div>

          <!-- Search -->
          <div class="flex-1 flex items-center justify-center px-2 lg:px-6">
            <div class="max-w-lg w-full lg:max-w-xs">
              <label for="search" class="sr-only">Search</label>
              <div class="relative">
                <div
                  class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                >
                  <font-awesome-icon
                    icon="search"
                    class="h-5 w-5 text-gray-400"
                  />
                </div>
                <input
                  id="search"
                  name="search"
                  class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm"
                  placeholder="Search"
                  type="search"
                  v-model="searchQuery"
                  @input="handleSearch"
                />
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
              style="top: 4rem; z-index: 99999"
            >
              <div class="px-4 py-2 border-b border-gray-200">
                <h3 class="text-sm font-medium text-gray-900">Notifications</h3>
              </div>
              <div class="max-h-96 overflow-y-auto">
                <div
                  v-if="notifications.length === 0"
                  class="px-4 py-3 text-sm text-gray-500"
                >
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
            <div class="ml-3 relative" style="z-index: 99999 !important">
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
                  :to="{ name: 'admin-profile' }"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Your Profile
                </router-link>
                <router-link
                  :to="{ name: 'admin-settings' }"
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
    <main class="flex-1 p-6">
      <router-view v-if="$route.path !== '/super-admin'" />
      <div v-else>
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <!-- Total Users -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <h3 class="text-gray-500 text-sm font-medium">Total Users</h3>
              <font-awesome-icon icon="users" class="h-8 w-8 text-primary" />
            </div>
            <p class="text-3xl font-semibold mt-2">1,234</p>
            <p class="text-green-600 text-sm mt-2">
              <font-awesome-icon icon="arrow-up" class="mr-1" />
              12% from last month
            </p>
          </div>

          <!-- Active Models -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <h3 class="text-gray-500 text-sm font-medium">Active Models</h3>
              <font-awesome-icon icon="cube" class="h-8 w-8 text-primary" />
            </div>
            <p class="text-3xl font-semibold mt-2">15</p>
            <p class="text-green-600 text-sm mt-2">
              <font-awesome-icon icon="arrow-up" class="mr-1" />
              3 new this week
            </p>
          </div>

          <!-- Total Generations -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <h3 class="text-gray-500 text-sm font-medium">
                Total Generations
              </h3>
              <font-awesome-icon icon="images" class="h-8 w-8 text-primary" />
            </div>
            <p class="text-3xl font-semibold mt-2">45,678</p>
            <p class="text-green-600 text-sm mt-2">
              <font-awesome-icon icon="arrow-up" class="mr-1" />
              25% from last month
            </p>
          </div>

          <!-- System Health -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <h3 class="text-gray-500 text-sm font-medium">System Health</h3>
              <font-awesome-icon icon="heart" class="h-8 w-8 text-primary" />
            </div>
            <p class="text-3xl font-semibold mt-2">98%</p>
            <p class="text-green-600 text-sm mt-2">
              <font-awesome-icon icon="check" class="mr-1" />
              All systems operational
            </p>
          </div>
        </div>

        <!-- Recent Activity and Quick Actions -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Recent Activity -->
          <div class="bg-white rounded-lg shadow">
            <div class="p-6 border-b border-gray-200">
              <h3 class="text-lg font-medium">Recent Activity</h3>
            </div>
            <div class="p-6">
              <div class="space-y-4">
                <div
                  v-for="(activity, index) in recentActivity"
                  :key="index"
                  class="flex items-start"
                >
                  <div class="flex-shrink-0">
                    <font-awesome-icon
                      :icon="activity.icon"
                      class="h-6 w-6 text-primary"
                    />
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-900">
                      {{ activity.title }}
                    </p>
                    <p class="text-sm text-gray-500">
                      {{ activity.description }}
                    </p>
                    <p class="text-xs text-gray-400 mt-1">
                      {{ activity.time }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow">
            <div class="p-6 border-b border-gray-200">
              <h3 class="text-lg font-medium">Quick Actions</h3>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-2 gap-4">
                <button
                  v-for="action in quickActions"
                  :key="action.title"
                  class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  @click="action.onClick"
                >
                  <font-awesome-icon
                    :icon="action.icon"
                    class="h-8 w-8 text-primary mb-2"
                  />
                  <span class="text-sm font-medium text-gray-900">{{
                    action.title
                  }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import axios from "axios";
import { useProfileStore } from "@/stores/profile";

export default {
  name: "AdminDashboard",
  setup() {
    const authStore = useAuthStore();
    const profileStore = useProfileStore();
    const searchQuery = ref("");
    const showNotifications = ref(false);
    const showProfile = ref(false);
    const unreadNotifications = ref(0);
    const notifications = ref([]);
    const avatarError = ref(false);

    // Fetch pending organizations and update notifications
    const fetchPendingApprovals = async () => {
      try {
        const response = await axios.get(
          "/api/v1/admin/organizations?status=pending"
        );
        const pendingOrgs = Array.isArray(response.data) ? response.data : [];

        // Update notifications with pending organizations
        notifications.value = pendingOrgs.map((org) => ({
          id: org.id,
          title: "Organization Pending Approval",
          message: `${org.name} is waiting for approval`,
          time: new Date(org.created_at).toLocaleString(),
          icon: "building",
          read: false,
        }));

        // Update unread count
        unreadNotifications.value = notifications.value.length;
      } catch (error) {
        console.error("Error fetching pending approvals:", error);
      }
    };

    const recentActivity = ref([
      {
        id: 1,
        title: "New User Registration",
        description: "John Doe has registered as a new user",
        time: "5 minutes ago",
        icon: "user-plus",
      },
      {
        id: 2,
        title: "System Update",
        description: "New version 2.0 is available",
        time: "1 hour ago",
        icon: "info-circle",
      },
    ]);

    const quickActions = ref([
      {
        id: 1,
        title: "Create New Model",
        icon: "cube",
        onClick: () => {
          console.log("Create New Model");
        },
      },
      {
        id: 2,
        title: "View All Users",
        icon: "users",
        onClick: () => {
          console.log("View All Users");
        },
      },
    ]);

    const handleSearch = () => {
      // Implement search functionality
      console.log("Searching:", searchQuery.value);
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
        this.$router.push("/login");
      } catch (error) {
        console.error("Logout error:", error);
      }
    };
    
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
    
    const handleImageError = (event) => {
      console.error('Failed to load avatar image');
      // Replace with fallback icon
      event.target.style.display = 'none';
    };

    // Fetch pending approvals on mount
    onMounted(async () => {
      await profileStore.fetchProfile();
      console.log('Profile data:', profileStore.profile);
      console.log('Avatar URL:', profileStore.profile?.avatar_url);
      await fetchPendingApprovals();
    });

    return {
      searchQuery,
      showNotifications,
      showProfile,
      unreadNotifications,
      notifications,
      recentActivity,
      quickActions,
      handleSearch,
      toggleNotifications,
      toggleProfile,
      fetchPendingApprovals,
      handleLogout,
      getAvatarUrl,
      handleImageError,
      avatarError,
      pageTitle: "Super Admin Dashboard",
      profileStore,
    };
  },
};
</script>
