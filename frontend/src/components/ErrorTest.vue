<template>
  <div class="container mx-auto p-6">
    <h2 class="text-2xl font-bold mb-6">Error Handling Test Suite</h2>
    
    <!-- Webcam Error Tests -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">Webcam Error Tests</h3>
      <div class="space-y-2">
        <button @click="testWebcamPermissionDenied" class="btn-test">
          Test Webcam Permission Denied
        </button>
        <button @click="testWebcamNotFound" class="btn-test">
          Test Webcam Not Found
        </button>
      </div>
    </div>

    <!-- Image Capture Tests -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">Image Capture Tests</h3>
      <div class="space-y-2">
        <button @click="testInvalidCapture" class="btn-test">
          Test Invalid Image Capture
        </button>
        <button @click="testCanvasError" class="btn-test">
          Test Canvas Context Error
        </button>
      </div>
    </div>

    <!-- Model Selection Tests -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">Model Selection Tests</h3>
      <div class="space-y-2">
        <button @click="testInvalidModel" class="btn-test">
          Test Invalid Model Selection
        </button>
      </div>
    </div>

    <!-- Image Generation Tests -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">Image Generation Tests</h3>
      <div class="space-y-2">
        <button @click="testGenerationWithoutModel" class="btn-test">
          Test Generation Without Model
        </button>
        <button @click="testGenerationWithoutImage" class="btn-test">
          Test Generation Without Image
        </button>
      </div>
    </div>

    <!-- Download/Share Tests -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">Download/Share Tests</h3>
      <div class="space-y-2">
        <button @click="testInvalidImageDownload" class="btn-test">
          Test Invalid Image Download
        </button>
        <button @click="testUnsupportedShare" class="btn-test">
          Test Unsupported Share
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { handleError } from '@/utils/errorHandler'

export default {
  name: 'ErrorTest',
  methods: {
    // Webcam Tests
    async testWebcamPermissionDenied() {
      try {
        const error = new Error('Permission denied')
        error.name = 'NotAllowedError'
        throw error
      } catch (error) {
        handleError(error, 'Webcam Access', {
          message: 'Camera access was denied. Please grant permission to use your camera.'
        })
      }
    },

    async testWebcamNotFound() {
      try {
        const error = new Error('Device not found')
        error.name = 'NotFoundError'
        throw error
      } catch (error) {
        handleError(error, 'Webcam Access', {
          message: 'No camera device was found. Please connect a camera and try again.'
        })
      }
    },

    // Image Capture Tests
    testInvalidCapture() {
      try {
        throw new Error('Camera not ready. Please wait a moment.')
      } catch (error) {
        handleError(error, 'Image Capture', {
          message: error.message
        })
      }
    },

    testCanvasError() {
      try {
        throw new Error('Could not initialize image capture')
      } catch (error) {
        handleError(error, 'Image Capture', {
          message: error.message
        })
      }
    },

    // Model Selection Tests
    testInvalidModel() {
      try {
        throw new Error('Invalid model selected')
      } catch (error) {
        handleError(error, 'Model Selection', {
          message: 'Failed to select the model. Please try again.'
        })
      }
    },

    // Generation Tests
    testGenerationWithoutModel() {
      try {
        throw new Error('Please select a model first')
      } catch (error) {
        handleError(error, 'Image Generation', {
          message: error.message
        })
      }
    },

    testGenerationWithoutImage() {
      try {
        throw new Error('Please capture an image first')
      } catch (error) {
        handleError(error, 'Image Generation', {
          message: error.message
        })
      }
    },

    // Download/Share Tests
    testInvalidImageDownload() {
      try {
        throw new Error('Invalid image format')
      } catch (error) {
        handleError(error, 'Image Download', {
          message: error.message
        })
      }
    },

    testUnsupportedShare() {
      try {
        throw new Error('Sharing is not supported on your device')
      } catch (error) {
        handleError(error, 'Image Share', {
          message: error.message
        })
      }
    }
  }
}
</script>

<style scoped>
.btn-test {
  padding: 0.5rem 1rem;
  background-color: rgb(124 58 237);
  color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  width: 100%;
  transition-property: background-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

.btn-test:hover {
  background-color: rgb(109 40 217);
}
</style>
