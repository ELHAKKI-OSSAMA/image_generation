<template>
  <div
    class="min-h-screen bg-gradient-to-br from-primary to-primary-light flex items-center justify-center px-4"
  >
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-xl">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm -space-y-px">
          <!-- Email field -->
          <div>
            <label for="email" class="sr-only">Email address</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="Email address"
            />
          </div>

          <!-- Password field -->
          <div class="relative">
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="Password (min 8 chars, must include !@#$%^&*)"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
              @click="showPassword = !showPassword"
            >
              <svg
                v-if="!showPassword"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 text-gray-500"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 text-gray-500"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                />
              </svg>
            </button>
          </div>

          <!-- Confirm Password field -->
          <div class="relative">
            <label for="confirmPassword" class="sr-only"
              >Confirm Password</label
            >
            <input
              id="confirmPassword"
              v-model="formData.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="Confirm Password"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center" style="z-index: 99999;"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <svg
                v-if="!showConfirmPassword"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 text-gray-500"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 text-gray-500"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- First Name and Last Name -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="firstName" class="sr-only">First Name</label>
            <input
              id="firstName"
              v-model="formData.firstName"
              type="text"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="First Name"
            />
          </div>
          <div>
            <label for="lastName" class="sr-only">Last Name</label>
            <input
              id="lastName"
              v-model="formData.lastName"
              type="text"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="Last Name"
            />
          </div>
        </div>

        <!-- Role selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700"
            >Account Type</label
          >
          <select
            v-model="formData.role"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
          >
            <option value="">Select role</option>
            <!-- <option value="user">Regular User</option> -->
            <!-- <option value="super_admin">Super Admin</option> -->
            <option value="organization">Organization</option>
            <option value="member">Organization Member</option>
          </select>
        </div>

        <!-- Organization fields -->
        <div v-if="formData.role === 'organization' || formData.role === 'member'" class="space-y-4">
          <div>
            <label
              for="organizationName"
              class="block text-sm font-medium text-gray-700"
              >Organization Name</label
            >
            <input
              id="organizationName"
              v-model="formData.organizationName"
              type="text"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="Organization Name"
            />
          </div>
          <div v-if="formData.role === 'organization'">
            <label
              for="organizationDescription"
              class="block text-sm font-medium text-gray-700"
              >Organization Description</label
            >
            <textarea
              id="organizationDescription"
              v-model="formData.organizationDescription"
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="Organization Description (Optional)"
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- Error messages -->
        <div
          v-if="error || validationErrors.length > 0"
          class="rounded-md bg-red-50 p-4"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5 text-red-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                There were errors with your submission
              </h3>
              <div class="mt-2 text-sm text-red-700">
                <ul class="list-disc pl-5 space-y-1">
                  <li v-if="error">{{ error }}</li>
                  <li v-for="(error, index) in validationErrors" :key="index">
                    {{ error }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Success message -->
        <div v-if="success" class="rounded-md bg-green-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5 text-green-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9V7a4 4 0 0112 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2h2a4 4 0 01-4 4z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">{{ success }}</h3>
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
              <svg
                class="h-5 w-5 text-primary-dark group-hover:text-primary"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                  clip-rule="evenodd"
                />
              </svg>
            </span>
            {{ loading ? "Registering..." : "Register" }}
          </button>
        </div>

        <!-- Login link -->
        <div class="text-sm text-center">
          <router-link
            to="/login"
            class="font-medium text-primary hover:text-primary-dark"
          >
            Already have an account? Sign in
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import axiosInstance from "../../plugins/axios";
import { useAuthStore } from "@/stores/auth";

export default {
  name: "RegisterView",

  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const showPassword = ref(false);
    const showConfirmPassword = ref(false);

    const formData = reactive({
      email: "",
      password: "",
      confirmPassword: "",
      firstName: "",
      lastName: "",
      role: "",
      organizationName: "",
      organizationDescription: "",
    });
    const error = ref("");
    const loading = ref(false);
    const validationErrors = ref([]);
    const success = ref("");

    const validateForm = () => {
      const errors = [];

      // Email validation
      if (!formData.email) {
        errors.push("Email is required");
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        errors.push("Invalid email format");
      }

      // Password validation
      if (!formData.password) {
        errors.push("Password is required");
      } else if (formData.password.length < 8) {
        errors.push("Password must be at least 8 characters");
      } else if (!/[!@#$%^&*]/.test(formData.password)) {
        errors.push(
          "Password must contain at least one special character (!@#$%^&*)"
        );
      }

      // Confirm password validation
      if (formData.password !== formData.confirmPassword) {
        errors.push("Passwords do not match");
      }

      // Name validation
      if (!formData.firstName) errors.push("First name is required");
      if (!formData.lastName) errors.push("Last name is required");

      // Role validation
      if (!formData.role) {
        errors.push("Please select an account type");
      }

      // Organization fields validation
      if (formData.role === "organization" || formData.role === "member") {
        if (!formData.organizationName) {
          errors.push("Organization name is required");
        }
      }

      validationErrors.value = errors;
      return errors.length === 0;
    };

    const handleRegister = async () => {
      if (!validateForm()) {
        return;
      }

      loading.value = true;
      error.value = "";

      try {
        if (formData.role === "organization") {
          const registrationData = {
            email: formData.email,
            password: formData.password,
            confirm_password: formData.confirmPassword,
            first_name: formData.firstName,
            last_name: formData.lastName,
            role: "ORGANIZATION",
            organization_name: formData.organizationName,
            organization_description: formData.organizationDescription,
          };

          await axiosInstance.post("/api/v1/auth/register", registrationData);
        } else if (formData.role === "member") {
          const registrationData = {
            email: formData.email,
            password: formData.password,
            confirm_password: formData.confirmPassword,
            first_name: formData.firstName,
            last_name: formData.lastName,
            role: "MEMBER",
            organization_name: formData.organizationName,
          };

          await axiosInstance.post("/api/v1/auth/register", registrationData);
        } else {
          // Regular user/admin registration
          const registrationData = {
            email: formData.email,
            password: formData.password,
            confirm_password: formData.confirmPassword,
            first_name: formData.firstName,
            last_name: formData.lastName,
            role: formData.role.toUpperCase(),
          };

          await axiosInstance.post("/api/v1/auth/register", registrationData);
        }

        success.value =
          "Registration successful! Please check your email to verify your account.";
        error.value = "";
        // Reset form
        formData.email = "";
        formData.password = "";
        formData.confirmPassword = "";
        formData.firstName = "";
        formData.lastName = "";
        formData.role = "";
        formData.organizationName = "";
        formData.organizationDescription = "";

        setTimeout(() => {
          router.push("/login");
        }, 3000);
      } catch (e) {
        console.error("Registration error:", e);
        error.value =
          e.response?.data?.detail || "Registration failed. Please try again.";
      } finally {
        loading.value = false;
      }
    };

    return {
      formData,
      error,
      loading,
      validationErrors,
      success,
      showPassword,
      showConfirmPassword,
      handleRegister,
    };
  },
};
</script>
