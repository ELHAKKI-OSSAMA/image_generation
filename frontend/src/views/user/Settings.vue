<template>
  <div class="container mx-auto px-4 py-8">
    <header class="page-header mb-8">
      <h1 class="text-3xl font-bold text-gray-800">Account Settings</h1>
    </header>
    
    <main class="page-content">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span class="ml-3 text-gray-600">Loading settings...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-8">
        <strong class="font-bold">Error!</strong>
        <span class="block sm:inline"> {{ error }}</span>
        <button
          @click="loadSettings"
          class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Try Again
        </button>
      </div>

      <div v-else class="bg-white rounded-lg shadow-md p-6">
        <!-- Validation Errors -->
        <div v-if="validationErrors.length" class="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <i class="fas fa-exclamation-triangle text-yellow-400"></i>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-yellow-800">Please fix the following errors:</h3>
              <ul class="mt-2 text-sm text-yellow-700 list-disc list-inside">
                <li v-for="(error, index) in validationErrors" :key="index">{{ error }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Settings Form -->
        <form @submit.prevent="saveSettings" class="space-y-8">
          <!-- Notifications Section -->
          <div class="settings-group">
            <h3 class="text-lg font-semibold mb-4">Notifications</h3>
            <div class="space-y-4">
              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input 
                    type="checkbox" 
                    v-model="settings.notifications.email"
                    class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                </div>
                <div class="ml-3">
                  <label class="font-medium text-gray-700">Email Notifications</label>
                  <p class="text-gray-500 text-sm">Receive updates about your generated images and account activity</p>
                </div>
              </div>

              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input 
                    type="checkbox" 
                    v-model="settings.notifications.browser"
                    class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    :disabled="!browserNotificationsSupported"
                  />
                </div>
                <div class="ml-3">
                  <label class="font-medium text-gray-700">
                    Browser Notifications
                    <span v-if="!browserNotificationsSupported" class="text-red-500 text-sm">(Not supported in your browser)</span>
                  </label>
                  <p class="text-gray-500 text-sm">Get real-time notifications in your browser</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Privacy Section -->
          <div class="settings-group">
            <h3 class="text-lg font-semibold mb-4">Privacy</h3>
            <div class="space-y-4">
              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input 
                    type="checkbox" 
                    v-model="settings.privacy.publicProfile"
                    class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                </div>
                <div class="ml-3">
                  <label class="font-medium text-gray-700">Public Profile</label>
                  <p class="text-gray-500 text-sm">Allow others to view your profile and generated images</p>
                </div>
              </div>

              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input 
                    type="checkbox" 
                    v-model="settings.privacy.shareUsage"
                    class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                </div>
                <div class="ml-3">
                  <label class="font-medium text-gray-700">Share Usage Statistics</label>
                  <p class="text-gray-500 text-sm">Help us improve by sharing anonymous usage data</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Display Section -->
          <div class="settings-group">
            <h3 class="text-lg font-semibold mb-4">Display</h3>
            <div class="space-y-4">
              <div class="form-group">
                <label for="theme" class="block text-sm font-medium text-gray-700">Theme</label>
                <select 
                  id="theme" 
                  v-model="settings.display.theme" 
                  class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System Default</option>
                </select>
              </div>

              <div class="form-group">
                <label for="language" class="block text-sm font-medium text-gray-700">Language</label>
                <select 
                  id="language" 
                  v-model="settings.display.language" 
                  class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Image Generation Section -->
          <div class="settings-group">
            <h3 class="text-lg font-semibold mb-4">Image Generation</h3>
            <div class="space-y-4">
              <div class="form-group">
                <label for="defaultResolution" class="block text-sm font-medium text-gray-700">Default Resolution</label>
                <select 
                  id="defaultResolution" 
                  v-model="settings.generation.defaultResolution" 
                  class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                >
                  <option value="512x512">512 x 512</option>
                  <option value="768x768">768 x 768</option>
                  <option value="1024x1024">1024 x 1024</option>
                </select>
              </div>

              <div class="form-group">
                <label for="quality" class="block text-sm font-medium text-gray-700">Image Quality</label>
                <select 
                  id="quality" 
                  v-model="settings.generation.quality" 
                  class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                >
                  <option value="standard">Standard</option>
                  <option value="high">High</option>
                  <option value="ultra">Ultra</option>
                </select>
              </div>

              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input 
                    type="checkbox" 
                    v-model="settings.generation.autoSave"
                    class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                </div>
                <div class="ml-3">
                  <label class="font-medium text-gray-700">Auto-save Generated Images</label>
                </div>
              </div>
            </div>
          </div>

          <!-- Storage Section -->
          <div class="settings-group">
            <h3 class="text-lg font-semibold mb-4">Data & Storage</h3>
            <div class="space-y-4">
              <div class="storage-info">
                <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-blue-500 transition-all duration-300"
                    :class="{ 'bg-yellow-500': storagePercentage > 70, 'bg-red-500': storagePercentage > 90 }"
                    :style="{ width: `${Math.min(storagePercentage, 100)}%` }"
                  ></div>
                </div>
                <p class="mt-2 text-sm text-gray-600">
                  {{ settings.storage.used }} of {{ settings.storage.total }} used
                  <span 
                    v-if="storagePercentage > 90" 
                    class="text-red-500 ml-2"
                  >
                    (Critical: Please free up space)
                  </span>
                </p>
              </div>

              <div class="form-group">
                <button 
                  @click="clearImageCache" 
                  type="button"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  :disabled="isClearing || !hasCache"
                >
                  <i class="fas fa-trash-alt mr-2"></i>
                  {{ isClearing ? 'Clearing...' : 'Clear Image Cache' }}
                </button>
                <p class="mt-2 text-sm text-gray-500">Free up space by clearing locally cached images</p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-4 pt-6 border-t">
            <button
              type="button"
              @click="resetSettings"
              class="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              :disabled="isSaving || !hasChanges"
            >
              Reset Changes
            </button>
            <button
              type="submit"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              :disabled="isSaving || !hasChanges"
            >
              <i v-if="isSaving" class="fas fa-spinner fa-spin mr-2"></i>
              {{ isSaving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script>
import { handleError } from '@/utils/errorHandler'

export default {
  name: 'UserSettings',
  data() {
    return {
      loading: true,
      error: null,
      validationErrors: [],
      settings: {
        notifications: {
          email: true,
          browser: true
        },
        privacy: {
          publicProfile: false,
          shareUsage: true
        },
        display: {
          theme: 'system',
          language: 'en'
        },
        generation: {
          defaultResolution: '512x512',
          quality: 'standard',
          autoSave: true
        },
        storage: {
          used: '250 MB',
          total: '1 GB'
        }
      },
      isSaving: false,
      isClearing: false,
      originalSettings: null,
      browserNotificationsSupported: false,
      hasCache: true
    }
  },
  computed: {
    storagePercentage() {
      try {
        const used = this.parseStorageSize(this.settings.storage.used);
        const total = this.parseStorageSize(this.settings.storage.total);
        return total === 0 ? 0 : Math.round((used / total) * 100);
      } catch (error) {
        handleError(error, 'Calculate Storage Percentage', {
          message: 'Error calculating storage usage'
        });
        return 0;
      }
    },
    hasChanges() {
      return JSON.stringify(this.settings) !== JSON.stringify(this.originalSettings);
    }
  },
  methods: {
    parseStorageSize(sizeStr) {
      try {
        const match = sizeStr.match(/^(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB)$/i);
        if (!match) return 0;
        
        const size = parseFloat(match[1]);
        const unit = match[2].toUpperCase();
        
        const multipliers = {
          KB: 1024,
          MB: 1024 * 1024,
          GB: 1024 * 1024 * 1024,
          TB: 1024 * 1024 * 1024 * 1024
        };
        
        return size * multipliers[unit];
      } catch (error) {
        handleError(error, 'Parse Storage Size', {
          message: 'Error parsing storage size'
        });
        return 0;
      }
    },

    async loadSettings() {
      try {
        this.loading = true;
        this.error = null;

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Simulated error (10% chance)
        if (Math.random() < 0.1) {
          throw new Error('Failed to load settings');
        }

        // In a real implementation, this would be an API call
        // const response = await api.getSettings();
        // this.settings = response.settings;

        this.originalSettings = JSON.parse(JSON.stringify(this.settings));
        await this.checkBrowserNotificationsSupport();
      } catch (error) {
        this.error = 'Failed to load settings';
        handleError(error, 'Load Settings', {
          message: 'Unable to load settings. Please try again.'
        });
      } finally {
        this.loading = false;
      }
    },

    async checkBrowserNotificationsSupport() {
      try {
        this.browserNotificationsSupported = 'Notification' in window;
        
        if (this.browserNotificationsSupported && this.settings.notifications.browser) {
          const permission = await Notification.requestPermission();
          if (permission !== 'granted') {
            this.settings.notifications.browser = false;
          }
        }
      } catch (error) {
        this.browserNotificationsSupported = false;
        handleError(error, 'Check Browser Notifications', {
          message: 'Error checking browser notification support'
        });
      }
    },

    validateSettings() {
      this.validationErrors = [];

      // Validate language
      if (!['en', 'es', 'fr', 'de'].includes(this.settings.display.language)) {
        this.validationErrors.push('Invalid language selection');
      }

      // Validate theme
      if (!['light', 'dark', 'system'].includes(this.settings.display.theme)) {
        this.validationErrors.push('Invalid theme selection');
      }

      // Validate resolution
      if (!['512x512', '768x768', '1024x1024'].includes(this.settings.generation.defaultResolution)) {
        this.validationErrors.push('Invalid resolution selection');
      }

      // Validate quality
      if (!['standard', 'high', 'ultra'].includes(this.settings.generation.quality)) {
        this.validationErrors.push('Invalid quality selection');
      }

      return this.validationErrors.length === 0;
    },

    async saveSettings() {
      if (this.isSaving) return;

      try {
        if (!this.validateSettings()) {
          this.$toast.error('Please fix the validation errors before saving');
          return;
        }

        this.isSaving = true;

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Simulated error (10% chance)
        if (Math.random() < 0.1) {
          throw new Error('Failed to save settings');
        }

        // In a real implementation, this would be an API call
        // await api.updateSettings(this.settings);

        this.originalSettings = JSON.parse(JSON.stringify(this.settings));
        this.$toast.success('Settings saved successfully');
      } catch (error) {
        handleError(error, 'Save Settings', {
          message: 'Unable to save settings. Please try again.'
        });
      } finally {
        this.isSaving = false;
      }
    },

    async clearImageCache() {
      if (this.isClearing) return;

      try {
        this.isClearing = true;

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Simulated error (10% chance)
        if (Math.random() < 0.1) {
          throw new Error('Failed to clear image cache');
        }

        // In a real implementation, this would clear the cache
        // await api.clearImageCache();

        this.hasCache = false;
        this.$toast.success('Image cache cleared successfully');
      } catch (error) {
        handleError(error, 'Clear Image Cache', {
          message: 'Unable to clear image cache. Please try again.'
        });
      } finally {
        this.isClearing = false;
      }
    },

    resetSettings() {
      try {
        if (!this.hasChanges) return;
        
        this.settings = JSON.parse(JSON.stringify(this.originalSettings));
        this.validationErrors = [];
        this.$toast.info('Settings reset to last saved state');
      } catch (error) {
        handleError(error, 'Reset Settings', {
          message: 'Error resetting settings'
        });
      }
    }
  },
  async created() {
    await this.loadSettings();
  },
  watch: {
    'settings.notifications.browser': {
      async handler(newValue) {
        if (newValue && this.browserNotificationsSupported) {
          try {
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
              this.settings.notifications.browser = false;
              this.$toast.warning('Browser notifications permission denied');
            }
          } catch (error) {
            this.settings.notifications.browser = false;
            handleError(error, 'Request Notification Permission', {
              message: 'Error requesting notification permission'
            });
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.settings-group {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 2rem;
}

.settings-group:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.form-group {
  margin-top: 0.25rem;
}
</style>
