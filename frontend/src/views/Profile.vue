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
            <v-avatar size="120" class="mr-4">
              <v-img :src="profile.avatar_url" alt="Profile Avatar">
                <template v-slot:placeholder>
                  <v-progress-circular indeterminate color="grey lighten-5"></v-progress-circular>
                </template>
              </v-img>
            </v-avatar>

            <v-file-input
              v-model="avatarFile"
              accept="image/*"
              label="Change Avatar"
              prepend-icon=""
              @change="handleAvatarChange"
              hide-details
              class="ml-4"
            ></v-file-input>
          </div>

          <v-text-field
            v-model="profile.full_name"
            label="Full Name"
            required
            :rules="[v => !!v || 'Name is required']"
          ></v-text-field>

          <v-select
            v-model="profile.timezone"
            :items="timezones"
            label="Timezone"
            required
            :rules="[v => !!v || 'Timezone is required']"
          ></v-select>

          <v-switch
            v-model="profile.two_factor_enabled"
            label="Two-Factor Authentication"
            @change="handleTwoFactorToggle"
            color="primary"
          ></v-switch>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              type="submit"
              :loading="saving"
              :disabled="saving"
            >
              Save Changes
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card-text>
    </v-card>

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3000"
    >
      {{ snackbar.text }}
    </v-snackbar>
    <button @change="handleAvatarChange">deug</button>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useProfileStore } from '@/stores/profile'
import { storeToRefs } from 'pinia'
import moment from 'moment-timezone'

const profileStore = useProfileStore()
const { profile } = storeToRefs(profileStore)

const form = ref(null)
const avatarFile = ref(null)
const saving = ref(false)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

const timezones = computed(() => {
  return moment.tz.names().map(tz => ({
    text: `${tz} (${moment.tz(tz).format('Z')})`,
    value: tz
  }))
})

onMounted(async () => {
  try {
    await profileStore.fetchProfile()
  } catch (error) {
    showError('Failed to load profile')
  }
})

async function handleSubmit() {
  if (!form.value.validate()) return

  saving.value = true
  try {
    await profileStore.updateProfile({
      full_name: profile.value.full_name,
      timezone: profile.value.timezone
    })
    showSuccess('Profile updated successfully')
  } catch (error) {
    showError('Failed to update profile')
  } finally {
    saving.value = false
  }
}

async function handleAvatarChange(file) {
  console.log('File received:', file)
  // if (!file) return

  // saving.value = true
  // try {
  //   console.log('File received:', file)
  //   // Create FormData and append the file
  //   const formData = new FormData()
  //   formData.append('avatar', file, file.name)
  //   // Log FormData entries and content type for debugging
  //   for (let pair of formData.entries()) {
  //     console.log('FormData entry:', pair[0], pair[1])
  //     if (pair[1] instanceof File) {
  //       console.log('File type:', pair[1].type)
  //       console.log('File name:', pair[1].name)
  //       console.log('File size:', pair[1].size)
  //     }
  //   }
  //   await profileStore.uploadAvatar(formData)
  //   showSuccess('Avatar updated successfully')
  // } catch (error) {
  //   console.error('Avatar change error:', error)
  //   showError('Failed to update avatar')
  // } finally {
  //   saving.value = false
  //   avatarFile.value = null
  // }
}

async function handleTwoFactorToggle() {
  try {
    await profileStore.toggleTwoFactor()
    showSuccess(
      profile.value.two_factor_enabled
        ? 'Two-factor authentication enabled'
        : 'Two-factor authentication disabled'
    )
  } catch (error) {
    showError('Failed to toggle two-factor authentication')
    // Revert the switch if the API call failed
    profile.value.two_factor_enabled = !profile.value.two_factor_enabled
  }
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

.v-avatar {
  border: 2px solid var(--v-primary-base);
}
</style>
