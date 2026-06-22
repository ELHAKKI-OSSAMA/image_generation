<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <h2 class="text-2xl font-bold">Profile Settings</h2>

    <!-- Profile Information -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">Personal Information</h3>
      <div class="space-y-4">
        <div class="flex items-center">
          <div class="relative">
            <div class="h-24 w-24 rounded-full bg-gray-200 flex items-center justify-center">
              <img v-if="profile.avatar" :src="profile.avatar" alt="Profile" 
                   class="h-24 w-24 rounded-full object-cover">
              <i v-else class="fas fa-user text-4xl text-gray-400"></i>
            </div>
            <button class="absolute bottom-0 right-0 bg-primary text-white rounded-full p-2 hover:bg-primary-dark">
              <i class="fas fa-camera"></i>
            </button>
          </div>
          <div class="ml-6">
            <h4 class="text-xl font-medium">{{ profile.name }}</h4>
            <p class="text-gray-500">{{ profile.email }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Display Name</label>
            <input type="text" v-model="profile.name" class="mt-1 input-primary">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" v-model="profile.email" class="mt-1 input-primary" disabled>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Bio</label>
          <textarea v-model="profile.bio" rows="3" class="mt-1 input-primary"></textarea>
        </div>
      </div>
    </div>

    <!-- Preferences -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">Generation Preferences</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Default Model</label>
          <select v-model="preferences.defaultModel" class="mt-1 input-primary">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Image Resolution</label>
          <select v-model="preferences.resolution" class="mt-1 input-primary">
            <option value="512">512x512</option>
            <option value="768">768x768</option>
            <option value="1024">1024x1024</option>
          </select>
        </div>

        <div class="flex items-center">
          <input type="checkbox" v-model="preferences.autoSave" class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded">
          <label class="ml-2 text-sm text-gray-700">Automatically save generated images</label>
        </div>
      </div>
    </div>

    <!-- Notification Settings -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">Notification Settings</h3>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-700">Generation Complete</h4>
            <p class="text-sm text-gray-500">Get notified when your image generation is complete</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="notifications.generationComplete" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-700">Email Updates</h4>
            <p class="text-sm text-gray-500">Receive updates about new features and models</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="notifications.emailUpdates" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end">
      <button class="btn-primary" @click="saveSettings">
        Save Changes
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileSettings',
  data() {
    return {
      profile: {
        name: 'John Doe',
        email: 'john@example.com',
        avatar: null,
        bio: ''
      },
      preferences: {
        defaultModel: 1,
        resolution: '512',
        autoSave: true
      },
      notifications: {
        generationComplete: true,
        emailUpdates: false
      },
      models: [
        { id: 1, name: 'Standard SD' },
        { id: 2, name: 'Artistic Style' },
        { id: 3, name: 'Photorealistic' }
      ]
    }
  },
  methods: {
    async saveSettings() {
      // Implement Firebase update
      this.$toast.success('Settings saved successfully!')
    },
    async fetchProfile() {
      // Implement Firebase fetch
    }
  },
  mounted() {
    this.fetchProfile()
  }
}
</script>
