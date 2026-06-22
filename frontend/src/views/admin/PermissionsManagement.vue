<template>
  <div class="admin-page">
    <header class="page-header">
      <h1>Permissions Management</h1>
      <p class="text-gray-600">Create and manage system permissions</p>
    </header>
    
    <main class="page-content">
      <!-- Create Permission Form -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Create New Permission</h2>
        
        <form @submit.prevent="createPermission" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Permission Name</label>
              <input
                id="name"
                v-model="newPermission.name"
                type="text"
                class="form-control"
                required
                placeholder="e.g. Manage Image Gallery"
              />
            </div>
            
            <div class="form-group">
              <label for="role" class="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <select
                id="role"
                v-model="newPermission.role"
                class="form-control"
                required
              >
                <option value="organization">Organization</option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              id="description"
              v-model="newPermission.description"
              class="form-control"
              rows="2"
              placeholder="Describe what this permission allows"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="type" class="block text-sm font-medium text-gray-700 mb-1">Permission Type</label>
            <select
              id="type"
              v-model="newPermission.type"
              class="form-control"
              required
            >
              <option value="">Select a permission type</option>
              
              <!-- Organization management -->
              <optgroup label="Organization Management">
                <option value="MANAGE_ORGANIZATION">Manage Organization</option>
                <option value="VIEW_ORGANIZATION">View Organization</option>
                <option value="MANAGE_MEMBERS">Manage Members</option>
                <option value="VIEW_MEMBERS">View Members</option>
              </optgroup>
              
              <!-- Event management -->
              <optgroup label="Event Management">
                <option value="MANAGE_EVENTS">Manage Events</option>
                <option value="VIEW_EVENTS">View Events</option>
                <option value="PARTICIPATE_EVENTS">Participate in Events</option>
              </optgroup>
              
              <!-- User management -->
              <optgroup label="User Management">
                <option value="MANAGE_USERS">Manage Users</option>
              </optgroup>
              
              <!-- Content management -->
              <optgroup label="Content Management">
                <option value="MANAGE_CONTENT">Manage Content</option>
                <option value="VIEW_CONTENT">View Content</option>
                <option value="CREATE_CONTENT">Create Content</option>
                <option value="EDIT_CONTENT">Edit Content</option>
                <option value="DELETE_CONTENT">Delete Content</option>
              </optgroup>
              
              <!-- Finance management -->
              <optgroup label="Finance Management">
                <option value="MANAGE_FINANCES">Manage Finances</option>
                <option value="VIEW_FINANCES">View Finances</option>
                <option value="PROCESS_PAYMENTS">Process Payments</option>
                <option value="ISSUE_REFUNDS">Issue Refunds</option>
              </optgroup>
              
              <!-- Integration management -->
              <optgroup label="Integration Management">
                <option value="MANAGE_INTEGRATIONS">Manage Integrations</option>
                <option value="VIEW_INTEGRATIONS">View Integrations</option>
              </optgroup>
              
              <!-- Security management -->
              <optgroup label="Security Management">
                <option value="MANAGE_SECURITY">Manage Security</option>
                <option value="VIEW_SECURITY_LOGS">View Security Logs</option>
              </optgroup>
              
              <!-- Analytics and reporting -->
              <optgroup label="Analytics & Reporting">
                <option value="MANAGE_ANALYTICS">Manage Analytics</option>
                <option value="VIEW_ANALYTICS">View Analytics</option>
                <option value="EXPORT_REPORTS">Export Reports</option>
              </optgroup>
              
              <!-- Settings management -->
              <optgroup label="Settings Management">
                <option value="MANAGE_SETTINGS">Manage Settings</option>
                <option value="VIEW_SETTINGS">View Settings</option>
              </optgroup>
            </select>
          </div>
          
          <div class="flex justify-end">
            <button
              type="submit"
              class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark"
              :disabled="loading"
            >
              <span v-if="loading">Creating...</span>
              <span v-else>Create Permission</span>
            </button>
          </div>
        </form>
      </div>
      
      <!-- Permissions List -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Existing Permissions</h2>
            
            <div class="flex items-center space-x-2">
              <label for="filter-type" class="text-sm font-medium text-gray-700">Filter by Type:</label>
              <select
                id="filter-type"
                v-model="filterType"
                class="form-control-sm"
                @change="filterPermissions"
              >
                <option value="">All Types</option>
              
              <!-- Organization management -->
              <optgroup label="Organization Management">
                <option value="MANAGE_ORGANIZATION">Manage Organization</option>
                <option value="VIEW_ORGANIZATION">View Organization</option>
                <option value="MANAGE_MEMBERS">Manage Members</option>
                <option value="VIEW_MEMBERS">View Members</option>
              </optgroup>
              
              <!-- Event management -->
              <optgroup label="Event Management">
                <option value="MANAGE_EVENTS">Manage Events</option>
                <option value="VIEW_EVENTS">View Events</option>
                <option value="PARTICIPATE_EVENTS">Participate in Events</option>
              </optgroup>
              
              <!-- User management -->
              <optgroup label="User Management">
                <option value="MANAGE_USERS">Manage Users</option>
              </optgroup>
              
              <!-- Content management -->
              <optgroup label="Content Management">
                <option value="MANAGE_CONTENT">Manage Content</option>
                <option value="VIEW_CONTENT">View Content</option>
                <option value="CREATE_CONTENT">Create Content</option>
                <option value="EDIT_CONTENT">Edit Content</option>
                <option value="DELETE_CONTENT">Delete Content</option>
              </optgroup>
              
              <!-- Finance management -->
              <optgroup label="Finance Management">
                <option value="MANAGE_FINANCES">Manage Finances</option>
                <option value="VIEW_FINANCES">View Finances</option>
                <option value="PROCESS_PAYMENTS">Process Payments</option>
                <option value="ISSUE_REFUNDS">Issue Refunds</option>
              </optgroup>
              
              <!-- Integration management -->
              <optgroup label="Integration Management">
                <option value="MANAGE_INTEGRATIONS">Manage Integrations</option>
                <option value="VIEW_INTEGRATIONS">View Integrations</option>
              </optgroup>
              
              <!-- Security management -->
              <optgroup label="Security Management">
                <option value="MANAGE_SECURITY">Manage Security</option>
                <option value="VIEW_SECURITY_LOGS">View Security Logs</option>
              </optgroup>
              
              <!-- Analytics and reporting -->
              <optgroup label="Analytics & Reporting">
                <option value="MANAGE_ANALYTICS">Manage Analytics</option>
                <option value="VIEW_ANALYTICS">View Analytics</option>
                <option value="EXPORT_REPORTS">Export Reports</option>
              </optgroup>
              
              <!-- Settings management -->
              <optgroup label="Settings Management">
                <option value="MANAGE_SETTINGS">Manage Settings</option>
                <option value="VIEW_SETTINGS">View Settings</option>
              </optgroup>
              </select>
            </div>
          </div>
        </div>
        
        <div class="p-6">
          <div v-if="loading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
          
          <div v-else-if="error" class="p-6 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-700">{{ error }}</p>
            <button @click="fetchPermissions" class="mt-2 text-sm text-red-700 underline">Retry</button>
          </div>
          
          <div v-else-if="filteredPermissions.length === 0" class="text-center py-8 text-gray-500">
            <p v-if="filterType">No permissions found with the selected type.</p>
            <p v-else>No permissions found. Create your first permission above.</p>
          </div>
          
          <div v-else>
            <div class="overflow-x-auto rounded-lg shadow">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th scope="col" class="hidden md:table-cell px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                    <th scope="col" class="hidden sm:table-cell px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th scope="col" class="hidden sm:table-cell px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="permission in paginatedPermissions" :key="permission.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ permission.id }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ permission.name }}</td>
                    <td class="hidden md:table-cell px-6 py-4 text-sm text-gray-500">
                      <div class="max-w-xs truncate">{{ permission.description || 'N/A' }}</div>
                    </td>
                    <td class="hidden sm:table-cell px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{{ permission.role }}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                        :class="getTypeClass(permission.type)"
                      >
                        {{ permission.type }}
                      </span>
                    </td>
                    <td class="hidden sm:table-cell px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(permission.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Pagination Controls -->
            <div class="mt-4 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
              <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                <div>
                  <p class="text-sm text-gray-700">
                    Showing
                    <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
                    to
                    <span class="font-medium">{{ Math.min(currentPage * itemsPerPage, filteredPermissions.length) }}</span>
                    of
                    <span class="font-medium">{{ filteredPermissions.length }}</span>
                    results
                  </p>
                </div>
                <div>
                  <select v-model="itemsPerPage" class="mr-4 rounded border-gray-300 py-1 text-sm" @change="currentPage = 1">
                    <option :value="5">5 per page</option>
                    <option :value="10">10 per page</option>
                    <option :value="25">25 per page</option>
                    <option :value="50">50 per page</option>
                  </select>
                  <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                    <button
                      @click="currentPage = Math.max(1, currentPage - 1)"
                      :disabled="currentPage === 1"
                      class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                      :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
                    >
                      <span class="sr-only">Previous</span>
                      <font-awesome-icon icon="chevron-left" class="h-5 w-5" aria-hidden="true" />
                    </button>
                    
                    <!-- Page numbers -->
                    <template v-if="totalPages <= 7">
                      <button
                        v-for="page in totalPages"
                        :key="page"
                        @click="currentPage = page"
                        :class="[
                          currentPage === page ? 'bg-primary text-white' : 'text-gray-900 hover:bg-gray-50',
                          'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-20 focus:outline-offset-0'
                        ]"
                      >
                        {{ page }}
                      </button>
                    </template>
                    
                    <!-- Truncated page numbers for many pages -->
                    <template v-else>
                      <!-- First page -->
                      <button
                        @click="currentPage = 1"
                        :class="[
                          currentPage === 1 ? 'bg-primary text-white' : 'text-gray-900 hover:bg-gray-50',
                          'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-20 focus:outline-offset-0'
                        ]"
                      >
                        1
                      </button>
                      
                      <!-- Ellipsis if needed -->
                      <span v-if="currentPage > 3" class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-700 ring-1 ring-inset ring-gray-300 focus:outline-offset-0">
                        ...
                      </span>
                      
                      <!-- Pages around current page -->
                      <button
                        v-for="page in getPageRange()"
                        :key="page"
                        @click="currentPage = page"
                        :class="[
                          currentPage === page ? 'bg-primary text-white' : 'text-gray-900 hover:bg-gray-50',
                          'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-20 focus:outline-offset-0'
                        ]"
                      >
                        {{ page }}
                      </button>
                      
                      <!-- Ellipsis if needed -->
                      <span v-if="currentPage < totalPages - 2" class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-700 ring-1 ring-inset ring-gray-300 focus:outline-offset-0">
                        ...
                      </span>
                      
                      <!-- Last page -->
                      <button
                        v-if="totalPages > 1"
                        @click="currentPage = totalPages"
                        :class="[
                          currentPage === totalPages ? 'bg-primary text-white' : 'text-gray-900 hover:bg-gray-50',
                          'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-20 focus:outline-offset-0'
                        ]"
                      >
                        {{ totalPages }}
                      </button>
                    </template>
                    
                    <button
                      @click="currentPage = Math.min(totalPages, currentPage + 1)"
                      :disabled="currentPage === totalPages || totalPages === 0"
                      class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                      :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages || totalPages === 0 }"
                    >
                      <span class="sr-only">Next</span>
                      <font-awesome-icon icon="chevron-right" class="h-5 w-5" aria-hidden="true" />
                    </button>
                  </nav>
                </div>
              </div>
              
              <!-- Mobile pagination controls -->
              <div class="flex flex-1 justify-between sm:hidden">
                <button
                  @click="currentPage = Math.max(1, currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
                >
                  Previous
                </button>
                <div class="mx-2 flex items-center">
                  <span class="text-sm text-gray-700">{{ currentPage }} / {{ totalPages || 1 }}</span>
                </div>
                <button
                  @click="currentPage = Math.min(totalPages, currentPage + 1)"
                  :disabled="currentPage === totalPages || totalPages === 0"
                  class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages || totalPages === 0 }"
                >
                  Next
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
import { ref, onMounted, computed, watch } from 'vue'
import { usePermissionsService } from '@/services/api/permissions'
import { useToast } from 'vue-toast-notification'

export default {
  name: 'PermissionsManagement',
  setup() {
    const permissionsService = usePermissionsService()
    const toast = useToast()
    const permissions = ref([])
    const filteredPermissions = ref([])
    const loading = ref(false)
    const error = ref(null)
    const filterType = ref('')
    
    // Pagination
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const paginatedPermissions = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredPermissions.value.slice(start, end)
    })
    const totalPages = computed(() => {
      return Math.ceil(filteredPermissions.value.length / itemsPerPage.value)
    })
    
    const newPermission = ref({
      name: '',
      description: '',
      role: 'organization',
      type: 'MANAGE_ORGANIZATION'
    })
    
    // Initialize with default values
    
    const fetchPermissions = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await permissionsService.getPermissions()
        permissions.value = Array.isArray(response) ? response : []
        filteredPermissions.value = [...permissions.value]
      } catch (err) {
        console.error('Error fetching permissions:', err)
        error.value = 'Failed to load permissions. Please try again.'
      } finally {
        loading.value = false
      }
    }
    
    const createPermission = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await permissionsService.createPermission(newPermission.value)
        
        // Add the new permission to the list
        permissions.value.push(response)
        filterPermissions()
        
        // Reset the form
        newPermission.value = {
          name: '',
          description: '',
          role: 'organization',
          type: 'MANAGE_ORGANIZATION'
        }
        
        // Show success message with toast
        toast.success('Permission created successfully!', {
          position: 'top-right',
          duration: 3000
        })
        
        // Reset to first page to show the new permission
        currentPage.value = 1
      } catch (err) {
        console.error('Error creating permission:', err)
        error.value = 'Failed to create permission. Please try again.'
        
        // Show error message with toast
        toast.error('Failed to create permission. Please try again.', {
          position: 'top-right',
          duration: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    const filterPermissions = () => {
      if (!filterType.value) {
        filteredPermissions.value = [...permissions.value]
      } else {
        filteredPermissions.value = permissions.value.filter(p => p.type === filterType.value)
      }
    }
    
    const getTypeClass = (type) => {
      const classes = {
        'MANAGE_ORGANIZATION': 'bg-blue-100 text-blue-800',
        'MANAGE_EVENTS': 'bg-green-100 text-green-800',
        'MANAGE_USERS': 'bg-purple-100 text-purple-800',
        'MANAGE_CONTENT': 'bg-yellow-100 text-yellow-800',
        'MANAGE_FINANCES': 'bg-red-100 text-red-800',
        'MANAGE_INTEGRATIONS': 'bg-indigo-100 text-indigo-800',
        'MANAGE_SECURITY': 'bg-gray-100 text-gray-800',
        'ACCESS_CONTENT': 'bg-pink-100 text-pink-800'
      }
      
      return classes[type] || 'bg-gray-100 text-gray-800'
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    // Initialize the component on mount
    onMounted(() => {
      fetchPermissions()
    })
    
    // Method to get page range for pagination
    const getPageRange = () => {
      // Show pages around current page
      const range = []
      const start = Math.max(2, currentPage - 1)
      const end = Math.min(totalPages - 1, currentPage + 1)
      
      for (let i = start; i <= end; i++) {
        range.push(i)
      }
      
      return range
    }
    
    // Reset pagination when filter changes
    watch(filterType, () => {
      currentPage.value = 1
    })
    
    return {
      permissions,
      filteredPermissions,
      paginatedPermissions,
      loading,
      error,
      filterType,
      newPermission,
      fetchPermissions,
      createPermission,
      filterPermissions,
      getTypeClass,
      formatDate,
      // Pagination
      currentPage,
      itemsPerPage,
      totalPages,
      getPageRange
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-control-sm {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}
</style>
