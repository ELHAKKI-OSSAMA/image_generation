<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold">User Management</h2>
      <div class="space-x-4">
        <button class="btn-primary" @click="showAddUserModal = true">
          <font-awesome-icon icon="plus" class="mr-2" /> Add User
        </button>
        <button class="btn-primary" @click="showInviteModal = true">
          <font-awesome-icon icon="user-plus" class="mr-2" /> Invite User
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      {{ error }}
    </div>

    <!-- User List -->
    <div v-if="!loading" class="bg-white shadow rounded-lg overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organizations</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="users.length === 0">
            <td colspan="5" class="px-6 py-4 text-center text-gray-500">
              No users found
            </td>
          </tr>
          <tr v-for="user in users" :key="user.id" v-else>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <font-awesome-icon icon="user-circle" class="text-gray-500" />
                </div>
                <div class="ml-4">
                  <div class="text-sm text-gray-900">{{ user.email }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'">
                {{ user.role }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div v-if="user.organizations?.length > 0 || user.memberships?.length > 0">
                <!-- Owned Organizations -->
                <div v-for="org in user.organizations" :key="org.id" class="text-sm text-gray-900">
                  {{ org.name }}
                  <span class="text-xs text-gray-500">
                    (Owner)
                    <span :class="org.status === 'pending' ? 'text-yellow-600' : 'text-green-600'">
                      [{{ org.status }}]
                    </span>
                  </span>
                </div>
                <!-- Member Organizations -->
                <div v-for="membership in user.memberships" :key="membership.id" class="text-sm text-gray-900">
                  {{ membership.organization?.name }}
                  <span class="text-xs text-gray-500">
                    ({{ membership.role }})
                    <span :class="membership.organization?.status === 'pending' ? 'text-yellow-600' : 'text-green-600'">
                      [{{ membership.organization?.status }}]
                    </span>
                  </span>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500">No organizations</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <button 
                @click="editUser(user)"
                class="text-indigo-600 hover:text-indigo-900 mr-3"
              >
                Edit
              </button>
              <button 
                @click="confirmDelete(user)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Organizations Management Section -->
    <div v-if="!loading" class="bg-white shadow rounded-lg overflow-hidden mt-6 p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-900">Organization Management</h2>
        <div class="flex space-x-4">
          <button 
            @click="organizationFilter = 'pending'"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-md',
              organizationFilter === 'pending' 
                ? 'bg-yellow-100 text-yellow-800' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            Pending
          </button>
          <button 
            @click="organizationFilter = 'active'"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-md',
              organizationFilter === 'active' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            Active
          </button>
          <button 
            @click="organizationFilter = 'suspended'"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-md',
              organizationFilter === 'suspended' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            Suspended
          </button>
        </div>
      </div>

      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Owner</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="org in filteredOrganizations" :key="org.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ org.name }}</div>
              <div class="text-xs text-gray-500">{{ org.description }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ org.owner?.email }}</div>
              <div class="text-xs text-gray-500">{{ org.owner?.first_name }} {{ org.owner?.last_name }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full" 
                :class="{
                  'bg-yellow-100 text-yellow-800': org.status === 'pending',
                  'bg-green-100 text-green-800': org.status === 'active',
                  'bg-red-100 text-red-800': org.status === 'suspended'
                }">
                {{ org.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(org.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
              <!-- Show Approve button only for pending organizations -->
              <button 
                v-if="org.status === 'pending'"
                @click="confirmAction(org, 'approve')"
                class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Approve
              </button>
              
              <!-- Show Decline button only for pending organizations -->
              <button 
                v-if="org.status === 'pending'"
                @click="confirmAction(org, 'decline')"
                class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Decline
              </button>
              
              <!-- Show Suspend/Restore button for active organizations -->
              <button 
                v-if="org.status === 'active'"
                @click="confirmAction(org, 'suspend')"
                class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Suspend
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96">
        <h3 class="text-lg font-semibold mb-4">Confirm Action</h3>
        <p class="text-gray-600">{{ confirmationMessage }}</p>
        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showConfirmModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
          >
            Cancel
          </button>
          <button 
            @click="executeAction"
            :class="[
              'px-4 py-2 text-sm font-medium text-white rounded-md',
              {
                'bg-green-600 hover:bg-green-700': pendingAction.action === 'approve',
                'bg-red-600 hover:bg-red-700': pendingAction.action === 'decline',
                'bg-yellow-600 hover:bg-yellow-700': pendingAction.action === 'suspend'
              }
            ]"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96">
        <h3 class="text-lg font-semibold mb-4">Edit User</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input 
              type="email" 
              v-model="editingUser.email" 
              disabled
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Role</label>
            <select 
              v-model="editingUser.role"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showEditModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
          >
            Cancel
          </button>
          <button 
            @click="saveUser"
            class="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary-dark rounded-md"
          >
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96">
        <h3 class="text-lg font-semibold mb-4">Confirm Delete</h3>
        <p class="text-gray-600">Are you sure you want to delete this user? This action cannot be undone.</p>
        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showDeleteModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
          >
            Cancel
          </button>
          <button 
            @click="deleteUser"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Invite User Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96">
        <h3 class="text-lg font-semibold mb-4">Invite New User</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input 
              type="email" 
              v-model="inviteEmail" 
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Role</label>
            <select 
              v-model="inviteRole"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showInviteModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
          >
            Cancel
          </button>
          <button 
            @click="inviteUser"
            class="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary-dark rounded-md"
          >
            Send Invitation
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import axios from '@/plugins/axios'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'UserManagement',
  setup() {
    const $toast = useToast()
    const users = ref([])
    const loading = ref(false)
    const error = ref(null)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const showAddUserModal = ref(false)
    const showInviteModal = ref(false)
    const editingUser = ref(null)
    const userToDelete = ref(null)
    const inviteEmail = ref('')
    const inviteRole = ref('user')
    const authStore = useAuthStore()
    const organizationFilter = ref('pending')
    const filteredOrganizations = ref([])
    const showConfirmModal = ref(false)
    const pendingAction = ref(null)
    const confirmationMessage = ref('')

    const fetchUsers = async () => {
      try {
        loading.value = true
        error.value = null
        
        const response = await axios.get('/api/v1/admin/users')
        users.value = response.data
        console.log("user data: ", response.data)
        
        // Fetch all organizations in one call
        try {
          const orgResponse = await axios.get('/api/v1/admin/organizations')
          const allOrganizations = orgResponse.data
          
          // Map organizations to users
          for (const user of users.value) {
            user.organizations = allOrganizations.filter(org => 
              org.owner_id === user.id || 
              org.members?.some(member => member.user_id === user.id)
            )
          }
        } catch (error) {
          console.error('Error fetching organizations:', error)
          users.value.forEach(user => user.organizations = [])
        }
      } catch (error) {
        console.error('Error fetching users:', error)
        const errorMessage = error.response?.data?.detail || 'Failed to load users'
        error.value = errorMessage
        $toast.error(errorMessage)
        users.value = []
      } finally {
        loading.value = false
      }
    }

    const fetchOrganizations = async () => {
      try {
        const response = await axios.get('/api/v1/admin/organizations')
        filteredOrganizations.value = response.data
      } catch (error) {
        console.error('Error fetching organizations:', error)
        $toast.error('Failed to fetch organizations')
        filteredOrganizations.value = []
      }
    }

    watch(organizationFilter, async (newFilter) => {
      try {
        const response = await axios.get(`/api/v1/admin/organizations?status=${newFilter}`)
        filteredOrganizations.value = response.data
      } catch (error) {
        console.error('Error fetching organizations:', error)
        filteredOrganizations.value = []
      }
    })

    const editUser = (user) => {
      editingUser.value = { ...user }
      showEditModal.value = true
    }

    const saveUser = async () => {
      try {
        await axios.put(`/api/v1/admin/users/${editingUser.value.id}`, {
          role: editingUser.value.role,
          status: editingUser.value.status,
          is_verified: editingUser.value.is_verified
        })
        
        await fetchUsers()
        showEditModal.value = false
        $toast.success('User updated successfully')
      } catch (error) {
        console.error('Error updating user:', error)
        $toast.error('Failed to update user')
      }
    }

    const confirmDelete = (user) => {
      userToDelete.value = user
      showDeleteModal.value = true
    }

    const deleteUser = async () => {
      try {
        await axios.delete(`/api/v1/admin/users/${userToDelete.value.id}`)
        await fetchUsers()
        showDeleteModal.value = false
        $toast.success('User deleted successfully')
      } catch (error) {
        console.error('Error deleting user:', error)
        $toast.error('Failed to delete user')
      }
      userToDelete.value = null
    }

    const confirmAction = (org, action) => {
      pendingAction.value = { action, organizationId: org.id }
      confirmationMessage.value = `Are you sure you want to ${action} the organization "${org.name}"?`
      showConfirmModal.value = true
    }

    const executeAction = async () => {
      if (!pendingAction.value) return

      const { action, organizationId } = pendingAction.value
      try {
        let endpoint = ''
        switch (action) {
          case 'approve':
            endpoint = `/api/v1/admin/approve-org/${organizationId}`
            break
          case 'decline':
            endpoint = `/api/v1/admin/decline-org/${organizationId}`
            break
          case 'suspend':
            endpoint = `/api/v1/admin/suspend-org/${organizationId}`
            break
        }

        await axios.post(endpoint)
        await fetchOrganizations()
        showConfirmModal.value = false
        pendingAction.value = null
        $toast.success(`Organization ${action}ed successfully`)
      } catch (error) {
        console.error(`Error ${action}ing organization:`, error)
        $toast.error(`Failed to ${action} organization`)
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString()
    }

    onMounted(async () => {
      await fetchUsers()
      await fetchOrganizations()
    })

    return {
      users,
      loading,
      error,
      showEditModal,
      showDeleteModal,
      showAddUserModal,
      showInviteModal,
      editingUser,
      userToDelete,
      inviteEmail,
      inviteRole,
      organizationFilter,
      filteredOrganizations,
      showConfirmModal,
      pendingAction,
      confirmationMessage,
      fetchUsers,
      fetchOrganizations,
      editUser,
      saveUser,
      confirmDelete,
      deleteUser,
      confirmAction,
      executeAction,
      formatDate
    }
  }
}
</script>
