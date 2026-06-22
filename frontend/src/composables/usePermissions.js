import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Composable for handling permission checks in components
 * @returns {Object} Permission check methods
 */
export function usePermissions() {
    const authStore = useAuthStore()

    /**
     * Check if user has a specific permission
     * @param {string} permission - Permission to check
     * @returns {boolean}
     */
    const hasPermission = computed(() => (permission) => {
        const userPermissions = authStore.permissions
        return userPermissions?.all || userPermissions?.[permission] === true
    })

    /**
     * Check if user has any of the given permissions
     * @param {Array<string>} permissions - List of permissions to check
     * @returns {boolean}
     */
    const hasAnyPermission = computed(() => (permissions) => {
        if (!Array.isArray(permissions)) return false
        return permissions.some(permission => hasPermission.value(permission))
    })

    /**
     * Check if user has all of the given permissions
     * @param {Array<string>} permissions - List of permissions to check
     * @returns {boolean}
     */
    const hasAllPermissions = computed(() => (permissions) => {
        if (!Array.isArray(permissions)) return false
        return permissions.every(permission => hasPermission.value(permission))
    })

    /**
     * Check if user has admin access
     * @returns {boolean}
     */
    const isAdmin = computed(() => {
        return hasPermission.value('manage_users') && hasPermission.value('manage_organizations')
    })

    /**
     * Check if user has super admin access
     * @returns {boolean}
     */
    const isSuperAdmin = computed(() => {
        return hasPermission.value('all')
    })

    /**
     * Check if user has organization admin access
     * @returns {boolean}
     */
    const isOrganizationAdmin = computed(() => {
        return hasPermission.value('manage_org_members') && hasPermission.value('manage_org_settings')
    })

    return {
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
        isAdmin,
        isSuperAdmin,
        isOrganizationAdmin
    }
}
