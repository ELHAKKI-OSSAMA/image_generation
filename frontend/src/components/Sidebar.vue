<template>
  <div 
    class="fixed inset-y-0 left-0 z-30 bg-primary text-white transition-all duration-300 ease-in-out"
    :class="{ 
      '-translate-x-full': !isOpen,
      'w-64': !isMobile,
      'w-20': isMobile
    }"
  >
    <!-- Toggle Button -->
    <button 
      @click="toggleSidebar"
      class="absolute right-0 top-4 translate-x-full bg-primary text-white p-2 rounded-r"
    >
      <font-awesome-icon :icon="isOpen ? 'chevron-left' : 'chevron-right'" />
    </button>

    <!-- Sidebar Header -->
    <div class="p-4">
      <h2 class="text-xl font-semibold">
        <template v-if="isAdmin">Admin Panel</template>
        <template v-else-if="isOrganization">Organization Panel</template>
        <template v-else>AI Image Suite</template>
      </h2>
      <div v-if="isOrganization" class="mt-1 text-sm text-gray-300">
        Role: {{ displayRole }}
      </div>
      <div v-if="isOrganization && organizationStatus === 'pending'" class="mt-2 text-sm text-yellow-300">
        <font-awesome-icon icon="clock" class="mr-1" />
        Pending Approval
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="mt-5 overflow-y-auto flex-1" style="height: calc(100vh - 137px);">
      <!-- Admin Menu -->
      <div v-if="isAdmin">
        <router-link 
          to="/super-admin" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin' }"
        >
          <font-awesome-icon icon="tachometer-alt" class="mr-3" />
          <span>Dashboard</span>
        </router-link>
        <router-link 
          to="/super-admin/users" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/users' }"
        >
          <font-awesome-icon icon="users" class="mr-3" />
          <span>User Management</span>
        </router-link>
        <router-link 
          to="/super-admin/models" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/models' }"
        >
          <font-awesome-icon icon="cube" class="mr-3" />
          <span>Model Management</span>
        </router-link>
        <router-link 
          to="/super-admin/analytics" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/analytics' }"
        >
          <font-awesome-icon icon="chart-line" class="mr-3" />
          <span>Analytics Dashboard</span>
        </router-link>
        <router-link 
          to="/super-admin/event-management" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/event-management' }"
        >
          <font-awesome-icon icon="calendar-alt" class="mr-3" />
          <span>Event Management</span>
        </router-link>
        <router-link 
          to="/super-admin/system-logs" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/system-logs' }"
        >
          <font-awesome-icon icon="clipboard-list" class="mr-3" />
          <span>System Logs</span>
        </router-link>
        <router-link 
          to="/super-admin/billing-subscription" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/billing-subscription' }"
        >
          <font-awesome-icon icon="credit-card" class="mr-3" />
          <span>Manage Billing </span>
        </router-link>
        <router-link 
          to="/super-admin/notifications" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/notifications' }"
        >
          <font-awesome-icon icon="bell" class="mr-3" />
          <span>Notifications</span>
        </router-link>
        <router-link 
          to="/super-admin/permissions" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/permissions' }"
        >
          <font-awesome-icon icon="shield-alt" class="mr-3" />
          <span>Permissions</span>
        </router-link>
        <router-link 
          to="/super-admin/profile" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/profile' }"
        >
          <font-awesome-icon icon="user-circle" class="mr-3" />
          <span>Profile</span>
        </router-link>
        <router-link 
          to="/super-admin/settings" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/super-admin/settings' }"
        >
          <font-awesome-icon icon="cog" class="mr-3" />
          <span>Settings</span>
        </router-link>
      </div>

      <!-- Organization Menu -->
      <div v-else-if="isOrganization && organizationStatus !== 'pending'">
        <router-link 
          to="/organization" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization' }"
        >
          <font-awesome-icon icon="building" class="mr-3" />
          <span>Organization Dashboard</span>
        </router-link>
        <router-link 
          to="/organization/generate-image" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/generate-image' }"
        >
          <font-awesome-icon icon="magic" class="mr-3" />
          <span>Generate Image</span>
        </router-link>
        <router-link 
          to="/organization/image-gallery" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/image-gallery' }"
        >
          <font-awesome-icon icon="images" class="mr-3" />
          <span>Image Gallery</span>
        </router-link>
        <router-link 
          to="/organization/events" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/events' }"
        >
          <font-awesome-icon icon="calendar-alt" class="mr-3" />
          <span>Event Management</span>
        </router-link>
        <router-link 
          to="/organization/staff" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/staff' }"
        >
          <font-awesome-icon icon="users" class="mr-3" />
          <span>Staff Management</span>
        </router-link>
        <router-link 
          to="/organization/profile" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/profile' }"
        >
          <font-awesome-icon icon="user-circle" class="mr-3" />
          <span>Profile</span>
        </router-link>
        <router-link 
          to="/organization/billing" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/billing' }"
        >
          <font-awesome-icon icon="credit-card" class="mr-3" />
          <span>Billing & Subscription</span>
        </router-link>
        <router-link 
          to="/organization/settings" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/organization/settings' }"
        >
          <font-awesome-icon icon="cog" class="mr-3" />
          <span>Organization Settings</span>
        </router-link>
      </div>

      <!-- Regular User Menu -->
      <div v-else-if="!isOrganization || organizationStatus === 'pending'">
        <router-link 
          to="/dashboard" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard' }"
        >
          <font-awesome-icon icon="home" class="mr-3" />
          <span>Dashboard</span>
        </router-link>
        <router-link 
          to="/dashboard/generate" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/generate' }"
        >
          <font-awesome-icon icon="magic" class="mr-3" />
          <span>Generate Image</span>
        </router-link>
        <router-link 
          to="/dashboard/gallery" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/gallery' }"
        >
          <font-awesome-icon icon="images" class="mr-3" />
          <span>Gallery</span>
        </router-link>
        <router-link 
          to="/dashboard/events-overview" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/events-overview' }"
        >
          <font-awesome-icon icon="calendar" class="mr-3" />
          <span>Events</span>
        </router-link>
        <router-link 
          to="/dashboard/model-library" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/model-library' }"
        >
          <font-awesome-icon icon="cubes" class="mr-3" />
          <span>Model Library</span>
        </router-link>
        <router-link 
          to="/dashboard/tutorials" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/tutorials' }"
        >
          <font-awesome-icon icon="book" class="mr-3" />
          <span>Tutorials</span>
        </router-link>
        <router-link 
          to="/dashboard/feedback-support" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/feedback-support' }"
        >
          <font-awesome-icon icon="question-circle" class="mr-3" />
          <span>Help & Support</span>
        </router-link>
        <router-link 
          to="/dashboard/profile" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/profile' }"
        >
          <font-awesome-icon icon="user-circle" class="mr-3" />
          <span>Profile</span>
        </router-link>
        <router-link 
          to="/dashboard/settings" 
          class="flex items-center px-6 py-3 hover:bg-primary-light"
          :class="{ 'bg-primary-dark': $route.path === '/dashboard/settings' }"
        >
          <font-awesome-icon icon="cog" class="mr-3" />
          <span>Settings</span>
        </router-link>
      </div>
    </nav>

    <!-- User Info & Logout -->
    <div class="absolute bottom-0 w-full p-4 border-t border-primary-light">
      <div class="flex items-center justify-between text-sm">
        <div class="flex items-center">
          <font-awesome-icon icon="user" class="mr-2" />
          <span class="truncate">{{ userName }}</span>
        </div>
        <button @click="handleLogout" class="text-white hover:text-gray-300">
          <font-awesome-icon icon="sign-out-alt" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useOrganizationStore } from '@/stores/organization'
import { useOrganizationService } from '@/services/api/organization'

export default {
  name: 'Sidebar',
  props: ['isOpen'],
  setup(props, { emit }) {
    // const isOpen = ref(true)
    const authStore = useAuthStore()
    const organizationStore = useOrganizationStore()
    const router = useRouter()
    
    // Add a ref to store the organization name
    const currentOrgName = ref('')

    // Add debugging logs
    console.log('SIDEBAR ROLE CHECK:', {
      role: authStore.role,
      is_admin: authStore.is_admin,
      is_super_admin: authStore.is_super_admin,
      is_organization_admin: authStore.is_organization_admin,
      is_organization_member: authStore.is_organization_member,
      is_regular_user: authStore.is_regular_user
    })
    
    // Fetch organization data directly using the service
    const fetchOrgName = async () => {
      if (authStore.role === 'organization' || authStore.role === 'member') {
        try {
          // Use the organization service directly
          const orgService = useOrganizationService()
          const orgs = await orgService.getOwnedOrganizations()
          
          if (orgs && orgs.length > 0) {
            currentOrgName.value = orgs[0].name
            console.log('Organization name set to:', currentOrgName.value)
          }
        } catch (error) {
          console.error('Error fetching organization name:', error)
        }
      }
    }
    
    // Call the fetch function when mounted
    onMounted(fetchOrgName)
    
    // Also watch for changes in the organization store
    watch(() => organizationStore.organizations, (newOrgs) => {
      if (newOrgs && newOrgs.length > 0 && newOrgs[0].name) {
        currentOrgName.value = newOrgs[0].name
        console.log('Organization name updated from watch:', currentOrgName.value)
      }
    }, { deep: true })

    const isAdmin = computed(() => authStore.role === 'super_admin')
    const isOrganization = computed(() => {
      // Include both organization admins and members
      const result = authStore.role === 'organization' || authStore.role === 'member'
      console.log('isOrganization computed:', result, 'role:', authStore.role)
      return result
    })
    
    // Get a formatted display role
    const displayRole = computed(() => {
      if (authStore.role === 'organization') {
        return 'Organization Admin'
      } else if (authStore.role === 'member') {
        return 'Organization Member'
      } else if (authStore.role === 'super_admin') {
        return 'Super Admin'
      } else {
        return 'User'
      }
    })
    
    const organizationStatus = computed(() => authStore.organization?.status)
    
    // Get organization name from organization store
    const organizationName = computed(() => {
      if (organizationStore.organizations && organizationStore.organizations.length > 0) {
        return organizationStore.organizations[0].name
      } else if (organizationStore.organization) {
        return organizationStore.organization.name
      } else if (organizationStore.settings && organizationStore.settings.profile) {
        return organizationStore.settings.profile.name
      }
      return ''
    })
    
    const userName = computed(() => authStore.user?.email || 'User')

    const toggleSidebar = () => {
      emit('toggle')
    }

    const handleLogout = async () => {
      try {
        await authStore.logout()
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    return {
      isOpen: computed(() => props.isOpen),
      isAdmin,
      isOrganization,
      organizationStatus,
      organizationName,
      currentOrgName,
      displayRole,
      userName,
      toggleSidebar,
      handleLogout
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar styling */
nav::-webkit-scrollbar {
  width: 6px;
}

nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
