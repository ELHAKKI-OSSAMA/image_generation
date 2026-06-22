<template>
	<div class="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
		<div class="sm:mx-auto sm:w-full sm:max-w-md">
			<div class="text-center">
				<font-awesome-icon 
					icon="clock" 
					class="mx-auto h-12 w-12 text-primary animate-pulse"
				/>
				<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
					Account Pending Approval
				</h2>
				<p class="mt-2 text-center text-sm text-gray-600">
					Thank you for registering your organization!
				</p>
			</div>
		</div>

		<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
			<div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
				<div class="text-center">
					<p class="text-sm text-gray-500 mb-4">
						Your organization account is currently pending approval from our administrators.
						We will review your application and notify you via email once your account is approved.
						You'll be automatically redirected once your account is approved.
					</p>
					<div class="space-y-4">
						<div class="border-t border-gray-200 pt-4">
							<h3 class="text-lg font-medium text-gray-900">What happens next?</h3>
							<ul class="mt-4 text-sm text-gray-500 text-left list-disc list-inside space-y-2">
								<li>Our team will review your organization details</li>
								<li>You'll receive an email notification about the approval status</li>
								<li>Once approved, you can log in and start managing your events</li>
								<li>This page will automatically redirect you when approved</li>
							</ul>
							<div class="mt-6 border-t border-gray-200 pt-4">
								<button
									@click="router.push('/')"
									class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
								>
									<font-awesome-icon icon="arrow-left" class="mr-2" />
									Back to Home
								</button>
							</div>
						</div>
						<div class="border-t border-gray-200 pt-4">
							<h3 class="text-lg font-medium text-gray-900">Need help?</h3>
							<p class="mt-2 text-sm text-gray-500">
								If you have any questions or concerns, please contact our support team at
								<a href="mailto:support@aiart.com" class="text-primary hover:text-primary-dark">
									support@aiart.com
								</a>
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'PendingApproval',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    let statusCheckInterval = null

    // Watch for organization status changes
    watch(() => authStore.organization?.status, (newStatus) => {
      if (newStatus === 'approved') {
        router.push('/organization')
      }
    })

    onMounted(() => {
      // Set up periodic checks every 30 seconds
      statusCheckInterval = setInterval(() => {
        if (authStore.organization?.status === 'approved') {
          router.push('/organization')
        }
      }, 30000)
    })

    onUnmounted(() => {
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval)
      }
    })

    return {
      router
    }
  }
}
</script>
