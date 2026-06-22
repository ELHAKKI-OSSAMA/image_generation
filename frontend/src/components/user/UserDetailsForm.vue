<template>
  <div class="bg-white shadow-md rounded-lg p-6">
    <div v-if="loading" class="flex justify-center items-center py-4">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"
      ></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Role Section (Display Only) -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Role</label>
        <div
          class="mt-2 px-4 py-3 bg-gray-50 rounded-md border border-gray-200"
        >
          <span class="text-lg font-semibold text-primary">{{
            userDetailsStore.userRole
          }}</span>
        </div>
      </div>

      <!-- Permissions Section -->
      <div v-if="!isUserRole">
        <label class="block text-sm font-medium text-gray-700"
          >Permissions</label
        >
        <div class="mt-2 space-y-2">
          <div
            v-for="(value, permission) in formData.permissions"
            :key="permission"
            class="flex items-center p-3 bg-gray-50 rounded-md"
          >
            <input
              :id="permission"
              v-model="formData.permissions[permission]"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label
              :for="permission"
              class="ml-3 text-sm text-gray-900 capitalize"
            >
              {{ permission.replaceAll("_", " ") }}
            </label>
          </div>
        </div>

        <!-- Add Permission Input
        <div class="flex items-center space-x-2 mt-4">
          <input
            v-model="newPermission"
            type="text"
            placeholder="Enter new permission (e.g., view_reports)"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary text-sm"
          />
          <button
            type="button"
            @click="addPermission"
            class="px-4 py-2 bg-primary text-white text-sm rounded-md hover:bg-primary-dark"
          >
            Add
          </button>
        </div> -->
        <p v-if="permissionError" class="text-sm text-red-600 mt-1">
          {{ permissionError }}
        </p>
      </div>

      <!-- Status Section -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Status</label>
        <div
          class="mt-2 px-4 py-3 bg-gray-50 rounded-md border border-gray-200"
        >
          <span class="text-lg font-semibold text-primary">{{
            userDetailsStore.userStatus
          }}</span>
        </div>
        <div class="mt-2">
          <select
            v-model="formData.status"
            class="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
            :class="{
              'bg-green-50': formData.status === 'VERIFIED',
              'bg-yellow-50': formData.status === 'PENDING',
              'bg-red-50': formData.status === 'SUSPENDED',
            }"
          >
            <!-- Add dynamic fallback option only if needed -->
            <option
              v-if="
                formData.status &&
                !['VERIFIED', 'PENDING', 'SUSPENDED'].includes(formData.status)
              "
              :value="formData.status"
              disabled
            >
              {{ formData.status }}
            </option>

            <!-- Always show fixed known options -->
            <option value="VERIFIED">Verified</option>
            <option value="PENDING">Pending</option>
            <option value="SUSPENDED">Suspended</option>
          </select>
        </div>
      </div>

      <!-- Error Message -->
      <div
        v-if="error"
        class="mt-2 p-3 text-sm text-red-600 bg-red-50 rounded-md"
      >
        {{ error }}
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between pt-4">
        <button
          type="submit"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          :disabled="loading"
        >
          Save Changes
        </button>

        <button
          type="button"
          @click="handleReset"
          class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          :disabled="loading"
        >
          Reset to Default
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { useUserDetailsStore } from "@/stores/userDetails";
import { useAuthStore } from "@/stores/auth";

export default {
  name: "UserDetailsForm",

  data() {
    const store = useUserDetailsStore();
    const authStore = useAuthStore();
    return {
      userDetailsStore: store,
      authStore: authStore,
      loading: false,
      error: null,
      permissionError: "",
      newPermission: "",
      formData: {
        permissions: {},
        status: "",
      },
    };
  },

  computed: {
    isUserRole() {
      return this.authStore.is_regular_user;
    },
  },

  methods: {
    initializeForm() {
      if (this.userDetailsStore.details) {
        this.formData = {
          permissions: { ...this.userDetailsStore.userPermissions },
          status: this.userDetailsStore.userStatus,
        };
      }
    },
    addPermission() {
      const perm = this.newPermission.trim().toLowerCase().replace(/\s+/g, "_");
      this.permissionError = "";

      if (!perm) {
        this.permissionError = "Permission cannot be empty.";
        return;
      }

      if (this.formData.permissions.hasOwnProperty(perm)) {
        this.permissionError = "Permission already exists.";
        return;
      }

      this.formData.permissions = {
        ...this.formData.permissions,
        [perm]: true,
      };

      this.newPermission = "";
    },
    async handleSubmit() {
      try {
        this.loading = true;
        this.error = null;
        await this.userDetailsStore.updateUserDetails({
          role: this.userDetailsStore.userRole, // Keep existing role
          permissions: this.formData.permissions,
          status: this.formData.status,
        });
      } catch (err) {
        this.error = err.message || "Failed to update user details";
      } finally {
        this.loading = false;
      }
    },

    async handleReset() {
      try {
        this.loading = true;
        this.error = null;
        await this.userDetailsStore.resetUserDetails();
        this.initializeForm();
      } catch (err) {
        this.error = err.message || "Failed to reset user details";
      } finally {
        this.loading = false;
      }
    },
  },

  async mounted() {
    try {
      this.loading = true;
      await this.userDetailsStore.fetchUserDetails();
      console.log("Store details:", this.userDetailsStore.details);
      console.log("Store permissions:", this.userDetailsStore.userPermissions);
      console.log("Store role:", this.userDetailsStore.userRole);
      console.log("Store status:", this.userDetailsStore.userStatus);
      this.initializeForm();
    } catch (err) {
      this.error = err.message || "Failed to load user details";
    } finally {
      this.loading = false;
    }
  },
};
</script>
