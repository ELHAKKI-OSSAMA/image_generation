<template>
  <div>
    <div class="container mx-auto px-4 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Staff Management</h1>
        <button
          @click="show_invite_modal = true"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition"
          :disabled="!hasAdminPermissions"
          :class="{ 'opacity-50 cursor-not-allowed': !hasAdminPermissions }"
          v-tooltip="!hasAdminPermissions ? 'You do not have permission to invite staff members' : ''"
        >
          <i class="fas fa-plus mr-2"></i> Invite Staff
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
    </div>
    
    <!-- No Organization Selected -->
    <div v-else-if="!has_organization" class="flex flex-col justify-center items-center min-h-[400px] bg-white rounded-2xl shadow-xl p-8">
      <div class="text-center mb-4">
        <i class="fas fa-building text-4xl text-gray-300 mb-4"></i>
        <h3 class="text-xl font-semibold text-gray-700">No Organization Selected</h3>
        <p class="text-gray-500 mt-2">Please select an organization to manage staff members.</p>
      </div>
    </div>

    <!-- Staff List -->
    <div v-else class="bg-white rounded-2xl shadow-xl overflow-hidden">
      <!-- Search and Filter -->
      <div class="p-4 border-b border-gray-200">
        <div class="flex flex-wrap gap-4">
          <div class="flex-grow max-w-md relative">
            <input
              v-model="search_query"
              type="text"
              placeholder="Search staff..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <select
            v-model="role_filter"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          >
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="staff">Staff</option>
            <option value="member">Member</option>
          </select>
          
          <select
            v-model="status_filter"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="pending">Pending</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <!-- Staff Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Staff Member</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Active</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="member in filtered_staff" :key="member.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="h-10 w-10 flex-shrink-0">
                    <img
                      :src="getAvatarUrl(member)"
                      class="h-10 w-10 rounded-full object-cover"
                      :alt="member.first_name + ' ' + member.last_name"
                      @error="handleImageError($event, member)"
                    />
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ member.first_name || '' }} {{ member.last_name || '' }}
                    </div>
                    <div class="text-sm text-gray-500">{{ member.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="member.role" class="text-sm font-medium">
                  {{ member.role.charAt(0).toUpperCase() + member.role.slice(1) }}
                </span>
                <select
                  v-model="member.role"
                  @change="update_member_role(member)"
                  class="text-sm border-0 bg-transparent focus:ring-0 ml-2"
                  :disabled="!can_edit_role(member)"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="member">Member</option>
                  <option value="staff">Staff</option>
                </select>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': member.status === 'active',
                    'bg-yellow-100 text-yellow-800': member.status === 'pending',
                    'bg-red-100 text-red-800': member.status === 'inactive'
                  }"
                >
                  {{ member.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex flex-col">
                  <span class="font-medium">{{ member.organization?.name || 'N/A' }}</span>
                  <span class="text-xs text-gray-400">{{ member.organization?.status || '' }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ format_date(member.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ format_date(member.last_active) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    @click="edit_member(member)"
                    class="text-blue-600 hover:text-blue-900 focus:outline-none"
                    :disabled="!hasAdminPermissions"
                    :class="{ 'opacity-50 cursor-not-allowed': !hasAdminPermissions }"
                    v-tooltip="!hasAdminPermissions ? 'You do not have permission to edit staff members' : ''"
                  >
                    Edit
                  </button>
                  <button
                    @click="openPermissionsModal(member)"
                    class="text-purple-600 hover:text-purple-900 focus:outline-none"
                    :disabled="!hasAdminPermissions"
                    :class="{ 'opacity-50 cursor-not-allowed': !hasAdminPermissions }"
                    v-tooltip="!hasAdminPermissions ? 'You do not have permission to edit permissions' : ''"
                  >
                    Permissions
                  </button>
                  <button
                    v-if="member.status === 'active'"
                    @click="show_confirmation('deactivate_member', 'Are you sure you want to deactivate this staff member?', member)"
                    class="text-yellow-600 hover:text-yellow-900 focus:outline-none"
                    :disabled="!hasAdminPermissions"
                    :class="{ 'opacity-50 cursor-not-allowed': !hasAdminPermissions }"
                    v-tooltip="!hasAdminPermissions ? 'You do not have permission to deactivate staff members' : ''"
                    title="Deactivate"
                  >
                    <i class="fas fa-user-slash"></i>
                  </button>
                  <button
                    v-else
                    @click="activate_member(member)"
                    class="text-green-600 hover:text-green-900 focus:outline-none"
                    :disabled="!hasAdminPermissions"
                    :class="{ 'opacity-50 cursor-not-allowed': !hasAdminPermissions }"
                    v-tooltip="!hasAdminPermissions ? 'You do not have permission to activate staff members' : ''"
                    title="Activate"
                  >
                    <i class="fas fa-user-check"></i>
                  </button>
                  <button
                    @click="show_confirmation('remove_member', 'Are you sure you want to remove this staff member?', member)"
                    class="text-red-600 hover:text-red-900 focus:outline-none"
                    :disabled="!hasAdminPermissions"
                    :class="{ 'opacity-50 cursor-not-allowed': !hasAdminPermissions }"
                    v-tooltip="!hasAdminPermissions ? 'You do not have permission to remove staff members' : ''"
                    title="Remove"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Invite Staff Modal -->
    <transition name="modal">
      <div v-if="show_invite_modal" class="fixed inset-0 flex items-center justify-center z-50">
        <div class="fixed inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 transform transition-all scale-95">
          <div class="p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Invite Staff Member</h2>
            <form @submit.prevent="send_invite" class="space-y-4">
              <div>
                <label for="invite-email" class="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  id="invite-email"
                  v-model="invite_form.email"
                  class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                />
                <p v-if="form_errors.invite.email" class="mt-1 text-xs text-red-600">{{ form_errors.invite.email }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Role</label>
                <select
                  v-model="invite_form.role"
                  required
                  class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="staff">Staff</option>
                  <option value="member">Member</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Message (Optional)</label>
                <textarea
                  v-model="invite_form.message"
                  rows="3"
                  class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
              <div class="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  @click="show_invite_modal = false"
                  class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
                >Cancel</button>
                <button
                  type="submit"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >Send Invite</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>

    <!-- Edit Member Modal -->
    <transition name="modal">
      <div v-if="selected_member" class="fixed inset-0 flex items-center justify-center z-50">
        <div class="fixed inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 transform transition-all scale-95">
          <div class="p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Edit Staff Member</h2>
            <form @submit.prevent="save_member" class="space-y-4">
              <div>
                <label for="edit-name" class="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  id="edit-name"
                  v-model="edit_form.name"
                  class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p v-if="form_errors.edit.name" class="mt-1 text-xs text-red-600">{{ form_errors.edit.name }}</p>
              </div>
              <div>
                <label for="edit-email" class="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  id="edit-email"
                  v-model="edit_form.email"
                  class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p v-if="form_errors.edit.email" class="mt-1 text-xs text-red-600">{{ form_errors.edit.email }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Role</label>
                <select
                  v-model="edit_form.role"
                  :disabled="!can_edit_role(selected_member)"
                  class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="staff">Staff</option>
                  <option value="member">Member</option>
                </select>
              </div>
              <div class="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  @click="selected_member = null"
                  class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
                >Cancel</button>
                <button
                  type="submit"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>

    <!-- Permissions Modal -->
    <transition name="modal">
      <div v-if="permissions_modal_open" class="fixed inset-0 flex items-center justify-center z-50 p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm" @click="closePermissionsModal"></div>
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-auto my-8 transform transition-all scale-95">
          <div class="flex flex-col max-h-[90vh]">
            <!-- Header with sticky position -->
            <div class="sticky top-0 bg-white z-10 p-6 pb-2 rounded-t-2xl border-b border-gray-100">
              <div class="flex justify-between items-center">
                <h2 class="text-xl font-semibold text-gray-900">Member Permissions</h2>
                <button @click="closePermissionsModal" class="text-gray-500 hover:text-gray-700 focus:outline-none">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <!-- Scrollable content area -->
            <div class="overflow-y-auto p-6 pt-2">
              <div v-if="selected_member_for_permissions" class="mb-4 p-4 bg-gray-50 rounded-lg">
                <div class="flex flex-wrap items-center">
                  <img
                    :src="getAvatarUrl(selected_member_for_permissions)"
                    class="h-10 w-10 rounded-full mr-3"
                    :alt="selected_member_for_permissions.first_name + ' ' + selected_member_for_permissions.last_name"
                  />
                  <div class="flex-grow min-w-0 mr-2">
                    <p class="font-medium truncate">{{ selected_member_for_permissions.first_name }} {{ selected_member_for_permissions.last_name }}</p>
                    <p class="text-sm text-gray-500 truncate">{{ selected_member_for_permissions.email }}</p>
                  </div>
                  <span class="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm mt-2 sm:mt-0">
                    {{ selected_member_for_permissions.role }}
                  </span>
                </div>
              </div>
              <member-permissions-editor
                :permissions="current_permissions"
                :custom-permissions="custom_permissions"
                :available-permissions="available_permissions"
                @update:permissions="updatePermissions"
                @update:customPermissions="updateCustomPermissions"
              />
              <div v-if="loading_permissions" class="flex justify-center items-center py-4">
                <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
                <span class="ml-2 text-sm text-gray-600">Loading permissions...</span>
              </div>
            </div>
            
            <!-- Footer with sticky position -->
            <div class="sticky bottom-0 bg-white z-10 p-6 pt-4 rounded-b-2xl border-t border-gray-100">
              <div class="flex justify-end gap-3">
                <button
                  type="button"
                  @click="closePermissionsModal"
                  class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
                >Cancel</button>
                <button
                  @click="savePermissions"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >Save Permissions</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Confirmation Dialog -->
    <transition name="modal">
      <div v-if="show_confirm_dialog" class="fixed inset-0 flex items-center justify-center z-50">
        <div class="fixed inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 transform transition-all scale-95">
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Confirm Action</h3>
            <p class="text-gray-700">{{ confirm_message }}</p>
            <div class="flex justify-end gap-3 mt-6">
              <button
                @click="cancel_dialog_action"
                class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >Cancel</button>
              <button
                @click="confirm_dialog_action"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >Confirm</button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { useOrganizationStore } from '@/stores/organization'
import { useAuthStore } from '@/stores/auth'
import { useOrganizationService } from '@/services/api/organization'
import { usePermissionService } from '@/services/api/permission'
import MemberPermissionsEditor from '@/components/organization/MemberPermissionsEditor.vue'

export default {
  name: 'StaffManagement',
  components: {
    MemberPermissionsEditor
  },
  directives: {
    tooltip: {
      mounted(el, binding) {
        if (binding.value) {
          el.setAttribute('data-tooltip', binding.value)
          el.classList.add('tooltip-trigger')
          
          // Add tooltip styles if not already present
          if (!document.getElementById('tooltip-styles')) {
            const style = document.createElement('style')
            style.id = 'tooltip-styles'
            style.innerHTML = `
              .tooltip-trigger {
                position: relative;
              }
              .tooltip-trigger:hover:after {
                content: attr(data-tooltip);
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 100;
                margin-bottom: 5px;
              }
            `
            document.head.appendChild(style)
          }
        }
      },
      updated(el, binding) {
        if (binding.value) {
          el.setAttribute('data-tooltip', binding.value)
        } else {
          el.removeAttribute('data-tooltip')
        }
      }
    }
  },
  data() {
    return {
      loading: true,
      search_query: '',
      role_filter: '',
      status_filter: '',
      show_invite_modal: false,
      show_confirm_dialog: false,
      confirm_action: null,
      confirm_data: null,
      confirm_message: '',
      permissions_modal_open: false,
      selected_member_for_permissions: null,
      current_permissions: {},
      custom_permissions: [],
      available_permissions: [],
      loading_permissions: false,
      selected_member: null,
      staff: [],
      has_organization: true,
      invite_form: {
        email: '',
        role: 'staff',
        message: ''
      },
      edit_form: {
        name: '',
        email: '',
        role: ''
      },
      form_errors: {
        invite: {
          email: ''
        },
        edit: {
          name: '',
          email: ''
        }
      }
    }
  },
  computed: {
    filtered_staff() {
      if (!this.staff || !Array.isArray(this.staff)) {
        return [];
      }
      
      return this.staff.filter(member => {
        const matches_search = !this.search_query || 
          (member.name && member.name.toLowerCase().includes(this.search_query.toLowerCase())) ||
          (member.email && member.email.toLowerCase().includes(this.search_query.toLowerCase()))
        
        const matches_role = !this.role_filter || member.role === this.role_filter
        const matches_status = !this.status_filter || member.status === this.status_filter
        
        return matches_search && matches_role && matches_status
      })
    },
    hasAdminPermissions() {
      const authStore = useAuthStore()
      return authStore.is_organization_admin
    }
  },
  methods: {
    getAvatarUrl(member) {
      if (member.avatar_url) {
        if (member.avatar_url.startsWith('/')) {
          return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${member.avatar_url}`
        }
        return member.avatar_url
      }
      const fullName = `${member.first_name || ''}+${member.last_name || ''}`
      return `https://ui-avatars.com/api/?name=${fullName}&background=random`
    },
    async fetch_staff() {
      this.loading = true
      try {
        const store = useOrganizationStore()
        const authStore = useAuthStore()
        if (authStore.organization?.id) {
          this.has_organization = true
          this.staff = await store.fetch_staff(authStore.organization.id)
          return
        }
        if (authStore.is_organization_admin && authStore.user?.id) {
          this.has_organization = true
          try {
            const organizationService = useOrganizationService()
            const ownedOrgs = await organizationService.getOwnedOrganizations()
            if (ownedOrgs && ownedOrgs.length > 0) {
              const orgId = ownedOrgs[0].id
              this.staff = await store.fetch_staff(orgId)
              return
            } else {
              this.staff = []
              return
            }
          } catch {
            this.staff = []
            this.$toast.error('Failed to fetch staff members')
            return
          }
        }
        // Add condition for organization members
        if (authStore.is_organization_member && authStore.user?.id) {
          console.log('Fetching organizations for member:', authStore.user.id)
          this.has_organization = true
          try {
            const organizationService = useOrganizationService()
            const userOrgs = await organizationService.getUserOrganizations(authStore.user.id)
            console.log('Member organizations response:', userOrgs)
            
            // The response format is different than expected - it's an object with user ID as key
            // and an array of organizations as value
            if (userOrgs && authStore.user?.id && userOrgs[authStore.user.id] && userOrgs[authStore.user.id].length > 0) {
              const orgId = userOrgs[authStore.user.id][0].id
              console.log('Using organization ID for member:', orgId)
              this.staff = await store.fetch_staff(orgId)
              console.log('Staff data for member:', this.staff)
              return
            } else {
              console.log('No organizations found for member')
              this.staff = []
              return
            }
          } catch (error) {
            console.error('Error fetching member organizations:', error)
            this.staff = []
            this.$toast.error('Failed to fetch staff members')
            return
          }
        }
        this.has_organization = false
        this.staff = []
        this.$toast.warning('Please select an organization to manage staff')
      } catch (error) {
        console.error('Error fetching staff:', error)
        this.staff = []
        this.$toast.error('Failed to fetch staff members')
      } finally {
        this.loading = false
      }
    },
    format_date(date) {
      if (!date) return 'Never'
      return new Date(date).toLocaleDateString()
    },
    can_edit_role(member) {
      const auth_store = useAuthStore()
      return auth_store.role === 'admin' && member.id !== auth_store.user?.id
    },
    async update_member_role(member) {
      try {
        const store = useOrganizationStore()
        await store.update_staff(member.id, { role: member.role })
        this.$toast.success('Staff role updated successfully')
      } catch {
        this.$toast.error('Failed to update staff role')
      }
    },
    edit_member(member) {
      this.selected_member = member
      this.edit_form = { name: member.name, email: member.email, role: member.role }
    },
    async save_member() {
      this.form_errors.edit = { name: '', email: '' }
      let has_errors = false
      if (!this.edit_form.name.trim()) {
        this.form_errors.edit.name = 'Name is required'
        has_errors = true
      }
      if (!this.edit_form.email.trim()) {
        this.form_errors.edit.email = 'Email is required'
        has_errors = true
      } else if (!/^\S+@\S+\.\S+$/.test(this.edit_form.email)) {
        this.form_errors.edit.email = 'Invalid email format'
        has_errors = true
      }
      if (has_errors) return
      try {
        const store = useOrganizationStore()
        await store.update_staff(this.selected_member.id, this.edit_form)
        const idx = this.staff.findIndex(m => m.id === this.selected_member.id)
        if (idx !== -1) this.staff[idx] = { ...this.staff[idx], ...this.edit_form }
        this.selected_member = null
        this.$toast.success('Staff member updated successfully')
      } catch {
        this.$toast.error('Failed to update staff member')
      }
    },
    async send_invite() {
      this.form_errors.invite = { email: '' }
      let has_errors = false
      if (!this.invite_form.email.trim()) {
        this.form_errors.invite.email = 'Email is required'
        has_errors = true
      } else if (!/^\S+@\S+\.\S+$/.test(this.invite_form.email)) {
        this.form_errors.invite.email = 'Invalid email format'
        has_errors = true
      }
      if (has_errors) return
      try {
        const store = useOrganizationStore()
        await store.invite_staff(this.invite_form)
        this.show_invite_modal = false
        this.invite_form = { email: '', role: 'staff', message: '' }
        this.$toast.success('Invitation sent successfully')
      } catch {
        this.$toast.error('Failed to send invitation')
      }
    },
    show_confirmation(action, message, data) {
      this.confirm_action = action
      this.confirm_message = message
      this.confirm_data = data
      this.show_confirm_dialog = true
    },
    async confirm_dialog_action() {
      if (this.confirm_action && typeof this[this.confirm_action] === 'function') {
        await this[this.confirm_action](this.confirm_data)
      }
      this.show_confirm_dialog = false
      this.confirm_action = null
      this.confirm_data = null
    },
    cancel_dialog_action() {
      this.show_confirm_dialog = false
      this.confirm_action = null
      this.confirm_data = null
    },
    async activate_member(member) {
      try {
        const store = useOrganizationStore()
        await store.update_staff_status(member.id, 'active')
        member.status = 'active'
        this.$toast.success('Staff member activated successfully')
      } catch {
        this.$toast.error('Failed to activate staff member')
      }
    },
    async deactivate_member(member) {
      try {
        const store = useOrganizationStore()
        await store.update_staff_status(member.id, 'inactive')
        member.status = 'inactive'
        this.$toast.success('Staff member deactivated successfully')
      } catch {
        this.$toast.error('Failed to deactivate staff member')
      }
    },
    async remove_member(member) {
      try {
        const store = useOrganizationStore()
        await store.remove_staff(member.id)
        this.staff = this.staff.filter(m => m.id !== member.id)
        this.$toast.success('Staff member removed successfully')
      } catch {
        this.$toast.error('Failed to remove staff member')
      }
    },
    async openPermissionsModal(member) {
      this.selected_member_for_permissions = { ...member }
      
      try {
        // Fetch member permissions from the backend
        const permissionService = usePermissionService()
        const memberPermissions = await permissionService.getMemberPermissions(member.id)
        
        this.current_permissions = memberPermissions || {}
        this.custom_permissions = member.custom_permissions || []
        this.permissions_modal_open = true
      } catch (error) {
        console.error('Error fetching member permissions:', error)
        this.$toast.error('Failed to load member permissions')
        
        // Fallback to permissions from the member object
        this.current_permissions = member.permissions || {}
        this.custom_permissions = member.custom_permissions || []
        this.permissions_modal_open = true
      }
    },
    closePermissionsModal() {
      this.permissions_modal_open = false
      this.selected_member_for_permissions = null
      this.current_permissions = {}
      this.custom_permissions = []
    },
    updatePermissions(permissions) {
      this.current_permissions = permissions
    },
    updateCustomPermissions(permissions) {
      this.custom_permissions = permissions
    },
    async savePermissions() {
      if (!this.selected_member_for_permissions) return
      
      const memberId = this.selected_member_for_permissions.id
      const idx = this.staff.findIndex(m => m.id === memberId)
      
      if (idx === -1) {
        this.$toast.error('Member not found')
        this.closePermissionsModal()
        return
      }
      
      try {
        // Update local state first
        this.staff[idx].permissions = { ...this.current_permissions }
        this.staff[idx].custom_permissions = [...this.custom_permissions]
        
        // Save to backend
        await this.savePermissionsToBackend(memberId, {
          permissions: this.current_permissions,
          custom_permissions: this.custom_permissions
        })
        
        this.$toast.success('Permissions updated successfully')
        this.closePermissionsModal()
      } catch (error) {
        console.error('Error saving permissions:', error)
        this.$toast.error('Failed to update permissions')
      }
    },
    async savePermissionsToBackend(memberId, permissionsData) {
      try {
        const permissionService = usePermissionService()
        const authStore = useAuthStore()
        const organizationId = authStore.organization?.id
        
        if (!organizationId) {
          console.error('No organization ID found')
          return
        }
        
        // Use the permission service to update member permissions
        await permissionService.updateMemberPermissions(organizationId, memberId, permissionsData)
        return true
      } catch (error) {
        console.error('Failed to save permissions to backend:', error)
        throw error
      }
    }
  },
  async created() {
    const authStore = useAuthStore()
    if (authStore.is_organization_admin && authStore.organization?.id) {
      this.has_organization = true
    }
    await this.fetch_staff()
    await this.fetch_available_permissions()
  },
  
  async fetch_available_permissions() {
    try {
      this.loading_permissions = true
      const permissionService = usePermissionService()
      const permissions = await permissionService.getPermissions()
      this.available_permissions = permissions
      console.log('Available permissions:', this.available_permissions)
    } catch (error) {
      console.error('Error fetching permissions:', error)
      this.$toast.error('Failed to load available permissions')
    } finally {
      this.loading_permissions = false
    }
  }
}
</script>

<style>
/* Optional: modal transition */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.modal-enter, .modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
