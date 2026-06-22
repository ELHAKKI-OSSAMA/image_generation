import { useAuthStore } from '@/stores/auth'

/**
 * Check if user has required permissions
 * @param {string|Array} permissions - Required permission(s)
 * @param {boolean} requireAll - If true, all permissions are required
 * @returns {Function} Navigation guard
 */
export function requirePermissions(permissions, requireAll = false) {
    return (to, from, next) => {
        const authStore = useAuthStore()
        
        if (!authStore.is_authenticated) {
            // Save intended destination
            to.meta.returnTo = to.fullPath
            return next({ name: 'login' })
        }

        // Convert single permission to array
        const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions]

        // Check permissions
        const hasPermission = requireAll
            ? requiredPermissions.every(p => authStore.permissions?.[p])
            : requiredPermissions.some(p => authStore.permissions?.[p])

        if (!hasPermission) {
            return next({ name: 'unauthorized' })
        }

        return next()
    }
}

/**
 * Guard for authenticated users
 */
export function requireAuth(to, from, next) {
    const authStore = useAuthStore()
    
    if (!authStore.is_authenticated) {
        // Save intended destination
        to.meta.returnTo = to.fullPath
        return next({ name: 'login' })
    }

    return next()
}

/**
 * Guard for admin access
 */
export function requireAdmin(to, from, next) {
    const authStore = useAuthStore()
    
    if (!authStore.is_authenticated) {
        to.meta.returnTo = to.fullPath
        return next({ name: 'login' })
    }

    if (!authStore.is_admin && !authStore.is_super_admin) {
        return next({ name: 'unauthorized' })
    }

    return next()
}

/**
 * Guard for super admin access
 */
export function requireSuperAdmin(to, from, next) {
    const authStore = useAuthStore()
    
    if (!authStore.is_authenticated) {
        to.meta.returnTo = to.fullPath
        return next({ name: 'login' })
    }

    if (!authStore.is_super_admin) {
        return next({ name: 'unauthorized' })
    }

    return next()
}

/**
 * Guard for organization admin access
 */
export function requireOrganizationAdmin(to, from, next) {
    const authStore = useAuthStore()
    
    // Add detailed logging for debugging
    console.log('ORGANIZATION ACCESS CHECK:', {
        path: to.fullPath,
        is_authenticated: authStore.is_authenticated,
        role: authStore.role,
        is_organization_admin: authStore.is_organization_admin,
        is_organization_member: authStore.is_organization_member,
        permissions: authStore.permissions
    })
    
    if (!authStore.is_authenticated) {
        console.log('User not authenticated, redirecting to login')
        to.meta.returnTo = to.fullPath
        return next({ name: 'login' })
    }

    if (!authStore.is_organization_admin) {
        console.log('User is not organization admin, redirecting to unauthorized')
        console.log('User permissions:', authStore.permissions)
        console.log('Organization member check:', authStore.is_organization_member)
        return next({ name: 'unauthorized' })
    }

    console.log('Organization admin access granted')
    return next()
}

/**
 * Guard for organization access (both admin and members)
 */
export function requireOrganizationAccess(to, from, next) {
    const authStore = useAuthStore()
    
    console.log('ORGANIZATION ACCESS CHECK (NEW GUARD):', {
        path: to.fullPath,
        is_authenticated: authStore.is_authenticated,
        role: authStore.role,
        is_organization_admin: authStore.is_organization_admin,
        is_organization_member: authStore.is_organization_member
    })
    
    if (!authStore.is_authenticated) {
        console.log('User not authenticated, redirecting to login')
        to.meta.returnTo = to.fullPath
        return next({ name: 'login' })
    }

    // Allow both organization admins and members
    if (!authStore.is_organization_admin && !authStore.is_organization_member) {
        console.log('User is neither organization admin nor member, redirecting to unauthorized')
        return next({ name: 'unauthorized' })
    }

    console.log('Organization access granted')
    return next()
}

/**
 * Guard for organization view access (allows members to view but not modify)
 */
export function requireOrganizationViewAccess(to, from, next) {
    const authStore = useAuthStore()
    
    console.log('ORGANIZATION VIEW ACCESS CHECK:', {
        path: to.fullPath,
        is_authenticated: authStore.is_authenticated,
        role: authStore.role,
        is_organization_admin: authStore.is_organization_admin,
        is_organization_member: authStore.is_organization_member
    })
    
    if (!authStore.is_authenticated) {
        console.log('User not authenticated, redirecting to login')
        to.meta.returnTo = to.fullPath
        return next({ name: 'login' })
    }

    // Allow organization admins with specific permissions or any organization member
    if (authStore.is_organization_admin || authStore.is_organization_member) {
        console.log('Organization view access granted')
        return next()
    }

    console.log('User is neither organization admin nor member, redirecting to unauthorized')
    return next({ name: 'unauthorized' })
}
