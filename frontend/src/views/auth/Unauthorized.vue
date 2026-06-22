<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="max-w-md w-full px-6 py-8 bg-white shadow-md rounded-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">
          Access Denied
        </h2>
        <p class="text-gray-600 mb-6">
          You don't have permission to access this page. Please contact your administrator if you believe this is a mistake.
        </p>
        <div class="flex justify-center space-x-4">
          <button
            @click="goBack"
            class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Go Back
          </button>
          <button
            @click="goHome"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Go to Home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Unauthorized',
  
  methods: {
    goBack() {
      this.$router.back()
    },
    
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>
