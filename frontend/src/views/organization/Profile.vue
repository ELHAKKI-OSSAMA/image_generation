<template>
  <div class="profile-container p-6">
    <v-card class="mx-auto">
      <v-card-title class="text-h4 mb-4">Profile Settings</v-card-title>

      <v-card-text>
        <div v-if="profileStore.loading" class="text-center">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else-if="profileStore.error" class="text-center error--text">
          {{ profileStore.error }}
        </div>

        <v-form v-else @submit.prevent="handleSubmit" ref="form">
          <div class="d-flex align-center mb-6">
            <div class="avatar-container">
              <v-avatar size="120" class="profile-avatar">
                {{ console.log("v-if='avatarPreview'", avatarPreview) }}
                <v-img v-if="localProfile.avatar_url" :src="getFullAvatarUrl(localProfile.avatar_url)" alt="Profile Avatar">
                  <template v-slot:placeholder>
                    <v-icon size="40" color="grey-lighten-1">mdi-account</v-icon>
                  </template>
                </v-img>
                <v-img v-else-if="avatarPreview " :src="avatarPreview" alt="Profile Avatar">
                  {{ console.log("v-if='localProfile.avatar_url'", localProfile.avatar_url) }}
                  <template v-slot:placeholder>
                    <v-icon size="40" color="grey-lighten-1">mdi-account</v-icon>
                  </template>
                </v-img>
                <v-img v-else :src="'/default-avatar.png'" alt="Profile Avatar">
                  {{ console.log("if not both show default") }}
                  <template v-slot:placeholder>
                    <v-icon size="40" color="grey-lighten-1">mdi-account</v-icon>
                  </template>
                </v-img>
              </v-avatar>
              <!-- {{ localProfile.avatar_url }} -->
              <div class="avatar-overlay">
                <label for="avatar-upload" class="upload-label">
                  <v-icon size="24" color="white">mdi-camera</v-icon>
                </label>
                <input
                  type="file"
                  id="avatar-upload"
                  accept="image/*"
                  @change="handleAvatarChange"
                  class="hidden-input"
                />
              </div>
            </div>
          </div>

          <v-text-field
            v-model="localProfile.full_name"
            label="Full Name"
            variant="outlined"
            density="comfortable"
            prepend-icon="mdi-account"
            required
            :rules="[v => !!v || 'Name is required']"
            class="mb-4"
          ></v-text-field>

          <v-select
            v-model="localProfile.timezone"
            :items="timezones"
            item-title="text"
            item-value="value"
            label="Timezone"
            variant="outlined"
            density="comfortable"
            prepend-icon="mdi-earth"
            required
            :rules="[v => !!v || 'Timezone is required']"
            class="mb-4"
          ></v-select>

          <v-switch
            v-model="localProfile.two_factor_enabled"
            label="Two-Factor Authentication"
            @change="handleTwoFactorToggle"
            color="primary"
            class="mb-4"
            inset
            hide-details
          ></v-switch>

          <v-divider class="my-4"></v-divider>

          <v-card-actions class="px-0">
            <v-spacer></v-spacer>
            <v-btn
              color="grey-darken-1"
              variant="text"
              class="me-4"
              :disabled="saving"
              @click="resetForm"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              type="submit"
              :loading="saving"
              :disabled="saving || !form?.validate()"
              variant="elevated"
            >
              <v-icon start>mdi-content-save</v-icon>
              Save Changes
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- User Details Card -->
    <v-card class="mx-auto mt-6">
      <v-card-title class="text-h4 mb-4">User Details</v-card-title>
      <v-card-text>
        <UserDetailsForm />
      </v-card-text>
    </v-card>

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useProfileStore } from '@/stores/profile'
import { storeToRefs } from 'pinia'
import moment from 'moment-timezone'
import axiosInstance from '@/plugins/axios'
import UserDetailsForm from '@/components/user/UserDetailsForm.vue'

const profileStore = useProfileStore()
const { profile } = storeToRefs(profileStore)

const form = ref(null)
const avatarPreview = ref(null)
const saving = ref(false)
const uploadingAvatar = ref(false)
const localProfile = ref({
  full_name: '',
  timezone: '',
  avatar_url: '',
  two_factor_enabled: false,
  avatar_file: null
})

const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// Update local profile when store profile changes
watch(() => profile.value, (newProfile) => {
  console.log( "old profile value", profile.value);
  console.log("new profile value: ",newProfile);
  
  if (newProfile) {
    // Preserve avatar_file (don't overwrite it)
    const { avatar_file, ...rest } = localProfile.value

    localProfile.value = {
      ...rest,
      ...newProfile,
      avatar_file: avatar_file || null  // keep it intact if set
    }
    console.log("local profile value ", localProfile.value);
    
  }
}, { immediate: true })

const timezones = computed(() => {
  return moment.tz.names().map(tz => ({
    text: `${tz} (${moment.tz(tz).format('Z')})`,
    value: tz
  }))
})

const getFullAvatarUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${axiosInstance.defaults.baseURL}${url}`
}

onMounted(async () => {
  try {
    await profileStore.fetchProfile()
  } catch (error) {
    showError('Failed to load profile')
  }
})

async function handleSubmit() {
  if (!form.value?.validate()) return
  console.log('from value ', form.value);
  
  saving.value = true
  try {
    console.log('Starting form submission...')
    console.log('Avatar file before profile update:', localProfile.value.avatar_file)
    
    // First update profile data
    await profileStore.updateProfile({
      full_name: localProfile.value.full_name,
      timezone: localProfile.value.timezone
    })

    // Then upload avatar if changed
    if (localProfile.value.avatar_file) {
      console.log('Preparing to upload avatar file:', localProfile.value.avatar_file)
      
      // Create FormData and append the file
      const formData = new FormData()
      formData.append('avatar', localProfile.value.avatar_file)
      
      // Log FormData contents
      for (let pair of formData.entries()) {
        console.log('FormData entry:', pair[0], pair[1])
      }
      
      await profileStore.uploadAvatar(formData)
      console.log('Avatar upload successful')
      // Force refresh by appending a timestamp
      localProfile.value.avatar_url = `${localProfile.value.avatar_url}?updated=${Date.now()}`
      avatarPreview.value = null
      localProfile.value.avatar_file = null
      
      // Clean up the old preview URL
      if (avatarPreview.value) {
        URL.revokeObjectURL(avatarPreview.value)
      }
      // Clear preview and file after successful upload
      avatarPreview.value = null
      localProfile.value.avatar_file = null
    } else {
      console.log('No avatar file to upload')
    }

    showSuccess('Profile updated successfully')
  } catch (error) {
    console.error('Profile update error:', error)
    showError('Failed to update profile')
  } finally {
    saving.value = false
  }
}

async function handleAvatarChange(event) {
  console.log("event ", event)
  const file = event.target.files[0]
  console.log("this is the file", file)
  if (!file) {
    avatarPreview.value = null
    localProfile.value.avatar_file = null
    return
  }

  // Validate file size
  // if (file.size > 5000000) {
  //   showError('File size should be less than 5MB')
  //   return
  // }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    showError('Please select an image file')
    return
  }
  
  
  // Show preview immediately
  avatarPreview.value = URL.createObjectURL(file)
  console.log("avatar preview ", avatarPreview.value)
  
  // Store the file in the reactive object instead
  localProfile.value.avatar_file = file
  console.log('avatar file after setting:', localProfile.value.avatar_file)
}

async function handleTwoFactorToggle() {
  try {
    await profileStore.toggleTwoFactor()
    showSuccess(
      localProfile.value.two_factor_enabled
        ? 'Two-factor authentication enabled'
        : 'Two-factor authentication disabled'
    )
  } catch (error) {
    showError('Failed to toggle two-factor authentication')
    // Revert the switch if the API call failed
    localProfile.value.two_factor_enabled = !localProfile.value.two_factor_enabled
  }
}

function resetForm() {
  // Reset form to original values
  if (profile.value) {
    localProfile.value = { 
      ...profile.value,
      avatar_file: null
    }
  }
  avatarPreview.value = null
  form.value?.resetValidation()
}

function showSuccess(text) {
  snackbar.value = {
    show: true,
    text,
    color: 'success'
  }
}

function showError(text) {
  snackbar.value = {
    show: true,
    text,
    color: 'error'
  }
}
</script>

<style scoped>
.profile-container {
  margin: 0 auto;
}

.avatar-container {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
}

.profile-avatar {
  border: 3px solid var(--v-primary-base);
  transition: all 0.3s ease;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.avatar-container:hover .profile-avatar {
  transform: scale(1.02);
}

.upload-label {
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.upload-label:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.hidden-input {
  display: none;
}
</style>
