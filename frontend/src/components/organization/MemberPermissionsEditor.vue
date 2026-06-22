<template>
  <div class="permissions-editor">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Manage Permissions</h3>
    
    <!-- Permissions Groups -->
    <div class="space-y-6">
      <!-- Organization Management -->
      <div class="permission-group">
        <h4 class="text-md font-medium text-gray-800 mb-2">Organization Management</h4>
        <div class="bg-gray-50 rounded-md p-4 space-y-2">
          <div v-for="permission in filteredOrganizationPermissions" :key="permission.key" 
               class="flex items-center">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
            <label :for="permission.key" class="ml-3 text-sm text-gray-900">
              {{ permission.label }}
              <span class="text-xs text-gray-500 block">{{ permission.description }}</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Event Management -->
      <div class="permission-group">
        <h4 class="text-md font-medium text-gray-800 mb-2">Event Management</h4>
        <div class="bg-gray-50 rounded-md p-4 space-y-2">
          <div v-for="permission in filteredEventPermissions" :key="permission.key" 
               class="flex items-center">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
            <label :for="permission.key" class="ml-3 text-sm text-gray-900">
              {{ permission.label }}
              <span class="text-xs text-gray-500 block">{{ permission.description }}</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- User Management -->
      <div class="permission-group">
        <h4 class="text-md font-medium text-gray-800 mb-2">User Management</h4>
        <div class="bg-gray-50 rounded-md p-4 space-y-2">
          <div v-for="permission in filteredUserPermissions" :key="permission.key" 
               class="flex items-center">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
            <label :for="permission.key" class="ml-3 text-sm text-gray-900">
              {{ permission.label }}
              <span class="text-xs text-gray-500 block">{{ permission.description }}</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Content Management (Only shown if permissions are available) -->
      <div v-if="contentPermissions.length > 0" class="permission-group">
        <h4 class="text-md font-medium text-gray-800 mb-2">Content Management</h4>
        <div class="bg-gray-50 rounded-md p-4 space-y-2">
          <div v-for="permission in contentPermissions" :key="permission.key" 
               class="flex items-center">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
            <label :for="permission.key" class="ml-3 text-sm text-gray-900">
              {{ permission.label }}
              <span class="text-xs text-gray-500 block">{{ permission.description }}</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Finance Management (Only shown if permissions are available) -->
      <div v-if="financePermissions.length > 0" class="permission-group">
        <h4 class="text-md font-medium text-gray-800 mb-2">Finance Management</h4>
        <div class="bg-gray-50 rounded-md p-4 space-y-2">
          <div v-for="permission in financePermissions" :key="permission.key" 
               class="flex items-center">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
            <label :for="permission.key" class="ml-3 text-sm text-gray-900">
              {{ permission.label }}
              <span class="text-xs text-gray-500 block">{{ permission.description }}</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Other Permissions (Only shown if permissions are available) -->
      <div v-if="otherPermissions.length > 0" class="permission-group">
        <h4 class="text-md font-medium text-gray-800 mb-2">Other Permissions</h4>
        <div class="bg-gray-50 rounded-md p-4 space-y-2">
          <div v-for="permission in otherPermissions" :key="permission.key" 
               class="flex items-center">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
            <label :for="permission.key" class="ml-3 text-sm text-gray-900">
              {{ permission.label }}
              <span class="text-xs text-gray-500 block">{{ permission.description }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Custom Permissions -->
    <div class="mt-6">
      <div class="flex justify-between items-center mb-2">
        <h4 class="text-md font-medium text-gray-800">Custom Permissions</h4>
        <button 
          @click="showAddPermissionForm = true"
          class="px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition"
        >
          <span class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Permission
          </span>
        </button>
      </div>
      
      <div v-if="isAdminRole" class="text-sm text-blue-600 mb-3 bg-blue-50 p-2 rounded">
        <i class="fas fa-info-circle mr-1"></i> Admin users have all permissions by default, but you can still customize their permissions if needed.
      </div>
      
      <!-- Add Permission Form -->
      <div v-if="showAddPermissionForm" class="bg-gray-50 rounded-md p-4 mb-4 border border-gray-200">
        <h5 class="font-medium text-gray-800 mb-3">Create New Permission</h5>
        <div class="space-y-3">
          <div>
            <label for="new-permission-key" class="block text-sm font-medium text-gray-700 mb-1">Permission Key</label>
            <input
              id="new-permission-key"
              v-model="newPermission.key"
              type="text"
              placeholder="e.g., access_reports"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              :class="{'border-red-300': keyError}"
            />
            <p v-if="keyError" class="mt-1 text-xs text-red-500">{{ keyError }}</p>
            <p class="mt-1 text-xs text-gray-500">Use snake_case format without spaces</p>
          </div>
          
          <div>
            <label for="new-permission-category" class="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              id="new-permission-category"
              v-model="newPermission.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="organization">Organization Management</option>
              <option value="event">Event Management</option>
              <option value="user">User Management</option>
              <option value="content">Content Management</option>
              <option value="finance">Finance Management</option>
              <option value="integration">Integration Management</option>
              <option value="security">Security Management</option>
              <option value="analytics">Analytics Management</option>
              <option value="settings">Settings Management</option>
              <option value="custom">Other</option>
            </select>
          </div>
          
          <div>
            <label for="new-permission-label" class="block text-sm font-medium text-gray-700 mb-1">Label</label>
            <input
              id="new-permission-label"
              v-model="newPermission.label"
              type="text"
              placeholder="e.g., Access Reports"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          
          <div>
            <label for="new-permission-description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              id="new-permission-description"
              v-model="newPermission.description"
              rows="2"
              placeholder="Describe what this permission allows"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            ></textarea>
          </div>
          
          <div class="flex justify-end space-x-2 pt-2">
            <button 
              @click="cancelAddPermission"
              class="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button 
              @click="addNewPermission"
              class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
              :disabled="!isNewPermissionValid"
            >
              Add Permission
            </button>
          </div>
        </div>
      </div>
      
      <!-- Custom Permissions List -->
      <div v-if="customPermissions.length > 0" class="bg-gray-50 rounded-md p-4">
        <div v-for="permission in customPermissions" :key="permission.key" class="flex items-start py-2 border-b border-gray-200 last:border-0">
          <div class="flex items-center h-5 mt-0.5">
            <input
              :id="permission.key"
              v-model="memberPermissions[permission.key]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="emitUpdate"
            />
          </div>
          <div class="ml-3 flex-grow">
            <label :for="permission.key" class="text-sm font-medium text-gray-900">
              {{ permission.label }}
              <span class="ml-2 text-xs px-2 py-0.5 bg-gray-200 text-gray-700 rounded-full">{{ getCategoryLabel(permission.category) }}</span>
            </label>
            <p class="text-xs text-gray-500">{{ permission.description }}</p>
          </div>
          <div class="flex space-x-1">
            <button 
              @click="editPermission(permission)"
              class="p-1 text-gray-500 hover:text-blue-600"
              title="Edit permission"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button 
              @click="deletePermission(permission.key)"
              class="p-1 text-gray-500 hover:text-red-600"
              title="Delete permission"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <div v-else-if="!showAddPermissionForm" class="bg-gray-50 rounded-md p-4 text-center text-gray-500 text-sm">
        No custom permissions created yet. Click "Add Permission" to create one.
      </div>
    </div>
    
    <!-- Edit Permission Modal -->
    <div v-if="editingPermission" class="fixed inset-0 flex items-center justify-center z-50">
      <div class="fixed inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm" @click="cancelEditPermission"></div>
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-auto p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Edit Permission</h3>
        
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Permission Key</label>
            <input
              type="text"
              disabled
              :value="editedPermission.key"
              class="w-full px-3 py-2 border border-gray-300 bg-gray-100 rounded-md text-sm"
            />
            <p class="mt-1 text-xs text-gray-500">Permission keys cannot be changed after creation</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              v-model="editedPermission.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="organization">Organization Management</option>
              <option value="event">Event Management</option>
              <option value="user">User Management</option>
              <option value="custom">Other</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Label</label>
            <input
              v-model="editedPermission.label"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="editedPermission.description"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            ></textarea>
          </div>
        </div>
        
        <div class="flex justify-end space-x-2 mt-6">
          <button 
            @click="cancelEditPermission"
            class="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button 
            @click="saveEditedPermission"
            class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
    
    <!-- Role Templates -->
    <div class="mt-6">
      <h4 class="text-md font-medium text-gray-800 mb-2">Apply Permission Template</h4>
      <div class="flex space-x-2">
        <button 
          v-for="template in roleTemplates" 
          :key="template.role"
          @click="applyTemplate(template.permissions)"
          class="px-3 py-1 text-sm rounded-md border border-gray-300 hover:bg-gray-50"
        >
          {{ template.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MemberPermissionsEditor',
  props: {
    permissions: {
      type: Object,
      default: () => ({})
    },
    customPermissions: {
      type: Array,
      default: () => ([])
    },
    availablePermissions: {
      type: Array,
      default: () => ([])
    }
  },
  data() {
    return {
      memberPermissions: {},
      organizationPermissions: [
        {
          key: 'manage_org_settings',
          label: 'Manage Organization Settings',
          description: 'Can update organization profile, settings, and configuration'
        },
        {
          key: 'manage_org_members',
          label: 'Manage Organization Members',
          description: 'Can invite, remove, and update roles of organization members'
        },
        {
          key: 'view_org_analytics',
          label: 'View Organization Analytics',
          description: 'Can view organization statistics and reports'
        }
      ],
      eventPermissions: [
        {
          key: 'manage_events',
          label: 'Manage Events',
          description: 'Can create, edit, and delete events'
        },
        {
          key: 'view_events',
          label: 'View Events',
          description: 'Can view all organization events'
        },
        {
          key: 'participate_events',
          label: 'Participate in Events',
          description: 'Can register and participate in events'
        }
      ],
      userPermissions: [
        {
          key: 'manage_participants',
          label: 'Manage Participants',
          description: 'Can manage event participants and registrations'
        },
        {
          key: 'view_participant_data',
          label: 'View Participant Data',
          description: 'Can view participant information and statistics'
        }
      ],
      roleTemplates: [
        {
          role: 'admin',
          label: 'Admin',
          permissions: {
            manage_organization: true,
            view_organization: true,
            manage_org_settings: true,
            manage_org_members: true,
            view_org_analytics: true,
            manage_events: true,
            create_events: true,
            edit_events: true,
            delete_events: true,
            view_events: true,
            manage_users: true,
            view_users: true,
            manage_content: true,
            create_content: true,
            edit_content: true,
            delete_content: true,
            view_content: true,
            manage_finances: true,
            view_finances: true,
            process_payments: true,
            manage_security: true,
            view_security_logs: true
          }
        },
        {
          role: 'manager',
          label: 'Manager',
          permissions: {
            manage_organization: false,
            view_organization: true,
            manage_org_settings: false,
            manage_org_members: true,
            view_org_analytics: true,
            manage_events: true,
            create_events: true,
            edit_events: true,
            delete_events: true,
            view_events: true,
            manage_users: true,
            view_users: true,
            manage_content: true,
            create_content: true,
            edit_content: true,
            delete_content: true,
            view_content: true,
            manage_finances: false,
            view_finances: true,
            process_payments: false,
            manage_security: false,
            view_security_logs: true
          }
        },
        {
          role: 'staff',
          label: 'Staff',
          permissions: {
            manage_organization: false,
            view_organization: true,
            manage_org_settings: false,
            manage_org_members: false,
            view_org_analytics: true,
            manage_events: false,
            create_events: true,
            edit_events: true,
            delete_events: false,
            view_events: true,
            manage_users: false,
            view_users: true,
            manage_content: false,
            create_content: true,
            edit_content: true,
            delete_content: false,
            view_content: true,
            manage_finances: false,
            view_finances: false,
            process_payments: false,
            manage_security: false,
            view_security_logs: false
          }
        },
        {
          role: 'member',
          label: 'Member',
          permissions: {
            manage_organization: false,
            view_organization: true,
            manage_org_settings: false,
            manage_org_members: false,
            view_org_analytics: false,
            manage_events: false,
            create_events: false,
            edit_events: false,
            delete_events: false,
            view_events: true,
            manage_users: false,
            view_users: false,
            manage_content: false,
            create_content: false,
            edit_content: false,
            delete_content: false,
            view_content: true,
            manage_finances: false,
            view_finances: false,
            process_payments: false,
            manage_security: false,
            view_security_logs: false
          }
        }
      ],
      customPermissions: this.customPermissions,
      showAddPermissionForm: false,
      newPermission: {
        key: '',
        category: 'custom',
        label: '',
        description: ''
      },
      keyError: '',
      editingPermission: false,
      editedPermission: {}
    }
  },
  computed: {
    isNewPermissionValid() {
      return this.newPermission.key && this.newPermission.label && this.newPermission.description
    },
    isAdminRole() {
      return this.memberPermissions.manage_org_settings && this.memberPermissions.manage_org_members && this.memberPermissions.view_org_analytics
    },
    // Organize available permissions by category
    categorizedPermissions() {
      if (!this.availablePermissions || this.availablePermissions.length === 0) {
        // If no available permissions provided, use the default hardcoded ones
        return {
          organization: this.organizationPermissions,
          event: this.eventPermissions,
          user: this.userPermissions
        }
      }
      
      // Group permissions by category
      const categorized = {
        organization: [],
        event: [],
        user: [],
        content: [],
        finance: [],
        integration: [],
        security: [],
        analytics: [],
        settings: [],
        other: []
      }
      
      this.availablePermissions.forEach(permission => {
        // Map backend permission fields to our component's expected format
        const permissionId = permission.id?.toString() || ''
        const permissionName = permission.name || ''
        
        // Create a key from the name if not provided
        const key = permissionName.toLowerCase().replace(/\s+/g, '_')
        
        // Use the type field for categorization
        const type = permission.type || permission.role || 'other'
        const category = this.mapPermissionTypeToCategory(type)
        
        const formattedPermission = {
          id: permissionId,
          key: key,
          label: permissionName,
          description: permission.description || `Permission to ${key.replace(/_/g, ' ')}`,
          type: type,
          category: category
        }
        
        if (categorized[category]) {
          categorized[category].push(formattedPermission)
        } else {
          categorized.other.push(formattedPermission)
        }
      })
      
      return categorized
    },
    // Get organization management permissions
    filteredOrganizationPermissions() {
      return this.categorizedPermissions.organization || this.organizationPermissions
    },
    // Get event management permissions
    filteredEventPermissions() {
      return this.categorizedPermissions.event || this.eventPermissions
    },
    // Get user management permissions
    filteredUserPermissions() {
      return this.categorizedPermissions.user || this.userPermissions
    },
    // Get content management permissions
    contentPermissions() {
      return this.categorizedPermissions.content || []
    },
    // Get finance management permissions
    financePermissions() {
      return this.categorizedPermissions.finance || []
    },
    // Get other permissions
    otherPermissions() {
      return this.categorizedPermissions.other || []
    }
  },
  created() {
    // Initialize permissions from props
    this.memberPermissions = { ...this.permissions }
    
    // Ensure all permissions exist in the object
    const allPermissions = [
      ...this.organizationPermissions,
      ...this.eventPermissions,
      ...this.userPermissions
    ]
    
    allPermissions.forEach(permission => {
      if (!(permission.key in this.memberPermissions)) {
        this.memberPermissions[permission.key] = false
      }
    })

    // Initialize custom permissions from props
    this.customPermissions = [...this.customPermissions]
  },
  methods: {
    mapPermissionTypeToCategory(type) {
      // Convert permission type to a category
      const typeLower = type.toLowerCase()
      
      if (typeLower.includes('org')) return 'organization'
      if (typeLower.includes('event')) return 'event'
      if (typeLower.includes('user') || typeLower.includes('member')) return 'user'
      if (typeLower.includes('content')) return 'content'
      if (typeLower.includes('financ') || typeLower.includes('payment')) return 'finance'
      if (typeLower.includes('integrat')) return 'integration'
      if (typeLower.includes('secur')) return 'security'
      if (typeLower.includes('analytic') || typeLower.includes('report')) return 'analytics'
      if (typeLower.includes('setting')) return 'settings'
      
      return 'other'
    },
    
    emitUpdate() {
      this.$emit('update:permissions', { ...this.memberPermissions })
    },
    applyTemplate(templatePermissions) {
      this.memberPermissions = { ...templatePermissions }
      this.emitUpdate()
    },
    addNewPermission() {
      if (!this.isNewPermissionValid) return
      
      // Validate permission key format (snake_case)
      if (!/^[a-z][a-z0-9_]*$/.test(this.newPermission.key)) {
        this.keyError = 'Permission key must be in snake_case format (lowercase with underscores)'
        return
      }
      
      // Check if key already exists
      if (this.memberPermissions.hasOwnProperty(this.newPermission.key) || 
          this.customPermissions.some(p => p.key === this.newPermission.key)) {
        this.keyError = 'Permission key already exists'
        return
      }
      
      // Format the new permission to match backend structure
      const newPermission = {
        id: `custom_${Date.now()}`, // Generate a temporary ID for custom permissions
        key: this.newPermission.key,
        name: this.newPermission.label,
        description: this.newPermission.description,
        type: this.newPermission.category,
        role: 'organization',
        custom: true // Mark as custom permission
      }
      
      this.customPermissions.push(newPermission)
      this.memberPermissions[newPermission.key] = true // Enable the permission by default
      this.emitUpdate()
      this.emitCustomPermissionsUpdate()
      this.cancelAddPermission()
    },
    cancelAddPermission() {
      this.showAddPermissionForm = false
      this.newPermission = {
        key: '',
        category: 'custom',
        label: '',
        description: ''
      }
      this.keyError = ''
    },
    editPermission(permission) {
      this.editingPermission = true
      this.editedPermission = { ...permission }
    },
    cancelEditPermission() {
      this.editingPermission = false
      this.editedPermission = {}
    },
    saveEditedPermission() {
      const index = this.customPermissions.findIndex(permission => permission.key === this.editedPermission.key)
      if (index !== -1) {
        this.customPermissions.splice(index, 1, this.editedPermission)
        this.emitCustomPermissionsUpdate()
      }
      this.cancelEditPermission()
    },
    deletePermission(key) {
      const index = this.customPermissions.findIndex(permission => permission.key === key)
      if (index !== -1) {
        this.customPermissions.splice(index, 1)
      }
      delete this.memberPermissions[key]
      this.emitUpdate()
      this.emitCustomPermissionsUpdate()
    },
    getCategoryLabel(category) {
      switch (category) {
        case 'organization':
          return 'Org'
        case 'event':
          return 'Event'
        case 'user':
          return 'User'
        default:
          return 'Custom'
      }
    },
    emitCustomPermissionsUpdate() {
      this.$emit('update:customPermissions', [...this.customPermissions])
    }
  },
  watch: {
    permissions: {
      handler(newPermissions) {
        this.memberPermissions = { ...newPermissions }
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.permissions-editor {
  max-width: 100%;
}
</style>
