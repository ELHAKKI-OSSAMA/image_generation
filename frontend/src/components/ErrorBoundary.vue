<!-- Error Boundary component to catch and handle component errors -->
<template>
  <div>
    <!-- Show error state if there's an error -->
    <div v-if="error" class="error-boundary bg-red-50 p-4 rounded-lg shadow-sm">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <font-awesome-icon 
            icon="exclamation-circle" 
            class="text-red-400"
            size="lg"
          />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ errorMessage }}
          </h3>
          <div class="mt-2">
            <button
              @click="resetError"
              class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <font-awesome-icon icon="sync" class="mr-2" />
              Try Again
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Render default content when no error -->
    <slot v-else />
  </div>
</template>

<script>
import { ref, onErrorCaptured } from 'vue'
import { handleError } from '@/utils/errorHandler'

export default {
  name: 'ErrorBoundary',
  
  props: {
    // Custom error message to display
    customMessage: {
      type: String,
      default: 'Something went wrong'
    },
    // Component identifier for error tracking
    componentName: {
      type: String,
      default: 'Unknown Component'
    }
  },

  setup(props, { emit }) {
    const error = ref(null)
    const errorMessage = ref(props.customMessage)

    // Handle captured errors
    onErrorCaptured((err, instance, info) => {
      error.value = err
      // Use our global error handler
      handleError(err, `Component Error: ${props.componentName}`, {
        message: props.customMessage
      })
      // Emit error event for parent components
      emit('error', { error: err, info })
      // Prevent error from propagating further
      return false
    })

    // Reset error state
    const resetError = () => {
      error.value = null
      errorMessage.value = props.customMessage
      emit('reset')
    }

    return {
      error,
      errorMessage,
      resetError
    }
  }
}
</script>

<style scoped>
.error-boundary {
  transition: all 0.3s ease;
}
</style>
