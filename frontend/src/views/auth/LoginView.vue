<template>
  <div class="min-h-screen bg-gradient-to-br from-primary to-primary-light flex items-center justify-center px-4">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-xl">
      <div class="text-center">
        <div class="mx-auto h-12 w-12 text-primary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" />
          </svg>
        </div>
        <h2 class="mt-4 text-center text-3xl font-extrabold text-gray-900">Sign in to your account</h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Enter your credentials to access your account
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email address</label>
            <input 
              id="email"
              v-model="formData.email" 
              type="email" 
              required 
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm" 
              placeholder="Email address"
            >
          </div>
          <div class="relative">
            <label for="password" class="sr-only">Password</label>
            <input 
              id="password"
              v-model="formData.password" 
              :type="showPassword ? 'text' : 'password'" 
              required 
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm" 
              placeholder="Password"
            >
            <button 
              type="button"
              @click="togglePassword"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-600 hover:text-gray-800 focus:outline-none" style="z-index: 99999;"
            >
              <svg 
                v-if="showPassword"
                xmlns="http://www.w3.org/2000/svg" 
                class="h-5 w-5" 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
              </svg>
              <svg 
                v-else
                xmlns="http://www.w3.org/2000/svg" 
                class="h-5 w-5" 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" />
                <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Error display -->
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <div class="text-sm text-red-700">
                {{ error }}
              </div>
            </div>
          </div>
        </div>

        <div>
          <button 
            type="submit" 
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            :disabled="loading"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="h-5 w-5 text-white group-hover:text-gray-100" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
            </span>
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>

        <div class="flex items-center justify-between mt-6">
          <div class="text-sm">
            <a href="#" class="font-medium text-primary-dark hover:text-primary transition-colors duration-200" @click.prevent="forgotPassword">
              Forgot your password?
            </a>
          </div>
          <div class="text-sm">
            <router-link to="/register" class="font-medium text-primary-dark hover:text-primary transition-colors duration-200">
              Create new account
            </router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '../../plugins/axios'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const formData = reactive({
      email: '',
      password: ''
    })
    const error = ref('')
    const loading = ref(false)
    const showPassword = ref(false)

    const handleLogin = async () => {
      error.value = ''
      loading.value = true
      
      try {
        await authStore.login(formData.email, formData.password, true)
      } catch (e) {
        error.value = e.message || 'Failed to login'
      } finally {
        loading.value = false
      }
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const forgotPassword = async () => {
      if (!formData.email) {
        error.value = 'Please enter your email address'
        return
      }

      loading.value = true
      try {
        await axiosInstance.post('/api/v1/auth/forgot-password', {
          email: formData.email
        })
        error.value = ''
        alert('Password reset instructions have been sent to your email')
      } catch (e) {
        console.error('Password reset error:', e)
        error.value = e.response?.data?.detail || 'Failed to process password reset request'
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      error,
      loading,
      showPassword,
      handleLogin,
      togglePassword,
      forgotPassword
    }
  }
}
</script>

<style scoped>
.from-primary {
  --tw-gradient-from: #1867C0;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgb(24 103 192 / 0));
}
.to-primary-light {
  --tw-gradient-to: #3986D8;
}
.text-primary {
  color: #1867C0;
}
.text-primary-dark {
  color: #0D4A8F;
}
.bg-primary {
  background-color: #1867C0;
}
.hover\:bg-primary-dark:hover {
  background-color: #0D4A8F;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #1867C0;
}
.focus\:border-primary:focus {
  border-color: #1867C0;
}
.text-white {
  color: #FFFFFF;
}
.group-hover\:text-gray-100:hover {
  color: #F3F4F6;
}
</style>