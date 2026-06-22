<template>
  <div>
    <div class="min-h-screen bg-white">
      <!-- Event Selection - Only show in step 1 -->
      <div
        class="mb-4 px-6 pt-4"
        v-if="showEventSelection && currentStep === 1"
      >
        <label class="block text-base font-semibold text-gray-900 mb-1"
          >Select Event</label
        >
        <select
          v-model="selectedEventId"
          :disabled="loadingEvents || !events.length"
          class="w-full px-4 py-2 border border-gray-400 rounded-lg focus:ring-2 focus:ring-blue-700 focus:border-blue-700 bg-white text-gray-900"
        >
          <option value="" disabled>Select an active event</option>
          <option v-for="event in events" :key="event.id" :value="event.id">
            {{ event.name }}
          </option>
        </select>
      </div>

      <div
        class="flex justify-between items-center mb-4 px-6 py-1"
        v-if="currentStep === 1"
      >
        <button
          v-if="selectedEventId && showEventSelection"
          @click="handleFullscreenClick"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold"
        >
          Open Fullscreen Mode
        </button>
      </div>

      <!-- Header -->
      <header class="bg-white border-b border-gray-100">
        <div class="max-w-6xl mx-auto px-4" style="padding-block: 0 !important">
          <div class="flex items-right" style="padding-block: 0 !important">
            <div class="flex items-left gap-4 pb-2 ml-2">
              <button
                v-if="currentStep > 1"
                @click="startOver"
                class="flex items-center gap-1 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200 text-sm font-medium"
              >
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  ></path>
                </svg>
                Back to Start
              </button>
            </div>
          </div>
        </div>
      </header>

      <main class="max-w-6xl mx-auto px-4 py-8">
        <!-- Step 1: Model Selection -->
        <div v-if="currentStep === 1" class="space-y-8">
          <div class="text-center"></div>
          <div class="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div
              v-for="model in filteredModels"
              :key="model.id"
              @click="selectModel(model)"
              :class="[
                'bg-white rounded-2xl p-6 cursor-pointer transition-all duration-300 border-2 shadow-lg',
                selectedModel?.id === model.id
                  ? 'border-blue-400 bg-blue-50 scale-105'
                  : 'border-gray-200 hover:border-blue-200 hover:bg-gray-50',
              ]"
            >
              <div
                class="relative aspect-square mb-4 overflow-hidden rounded-xl"
              >
                <template v-if="model.preview_url">
                  <img
                    :src="model.preview_url"
                    :alt="model.name"
                    loading="lazy"
                    class="w-full h-full object-cover transition-transform duration-200 hover:scale-105"
                    onerror="this.onerror=null; this.style.display='none'; this.nextElementSibling.style.display='flex';"
                  />
                  <div
                    class="absolute inset-0 bg-blue-600 hidden items-center justify-center text-white text-4xl"
                  >
                    {{ model.icon }}
                  </div>
                </template>
                <div
                  v-else
                  class="w-full h-full bg-blue-600 flex items-center justify-center text-white text-4xl"
                >
                  {{ model.icon }}
                </div>
                <div class="absolute top-2 right-2" v-if="model.category">
                  <span
                    class="px-2 py-1 text-xs rounded-full bg-black/50 text-white"
                  >
                    {{ model.category }}
                  </span>
                </div>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {{ model.name }}
              </h3>
              <p class="text-gray-600 text-sm">{{ model.description }}</p>
            </div>
          </div>
        </div>

        <!-- Step 2: Camera Permission -->
        <div v-if="currentStep === 2 && !hasCameraPermission" class="space-y-8">
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">Camera Access</h2>
            <p class="text-xl text-gray-600" v-if="!hasCameraPermission">
              We need access to your camera to take a photo
            </p>
            <p class="text-xl text-gray-600" v-else>
              Camera permission is granted but we need to access your camera
            </p>
          </div>

          <div
            class="max-w-md mx-auto bg-white shadow-lg rounded-2xl p-8 text-center"
          >
            <div
              class="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <svg
                class="w-10 h-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                ></path>
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                ></path>
              </svg>
            </div>

            <h3 class="text-2xl font-semibold text-gray-900 mb-4">
              <template v-if="!hasCameraPermission">Enable Camera</template>
              <template v-else>Access Camera</template>
            </h3>

            <p class="text-gray-600 mb-6" v-if="!hasCameraPermission">
              Click the button below to grant camera permissions
            </p>
            <p class="text-gray-600 mb-6" v-else>
              You've already granted camera permission. Click the button below
              to access your camera.
            </p>

            <button
              @click="requestCameraPermission"
              :disabled="isRequestingPermission"
              class="w-full bg-blue-600 text-white py-4 rounded-xl font-semibold text-lg hover:bg-blue-700 transition-all duration-300 disabled:opacity-50"
            >
              <span v-if="isRequestingPermission">Accessing Camera...</span>
              <span v-else-if="hasCameraPermission">Access Camera</span>
              <span v-else>Grant Camera Access</span>
            </button>
            <!-- Debug info -->
            <div class="mt-2 text-xs text-gray-500">
              Permission state:
              {{ hasCameraPermission ? "Granted" : "Not granted" }}
            </div>
          </div>
        </div>

        <!-- Step 3: Camera View -->
        <div v-if="currentStep === 3" class="space-y-8">
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
              Take Your Photo
            </h2>
            <p class="text-xl text-gray-600">
              Position yourself and click the capture button
            </p>
          </div>

          <div class="max-w-2xl mx-auto">
            <div class="relative bg-black rounded-2xl overflow-hidden">
              <video
                ref="videoElement"
                autoplay
                playsinline
                muted
                class="w-full aspect-video object-cover"
                style="transform: scaleX(-1); background-color: #000"
              ></video>

              <!-- Countdown Overlay -->
              <div
                v-if="isCountingDown"
                class="absolute inset-0 bg-black/50 flex items-center justify-center"
              >
                <div class="text-center">
                  <div class="text-8xl font-bold text-white mb-4">
                    {{ countdown }}
                  </div>
                  <div class="text-2xl text-white/70">Get ready!</div>
                </div>
              </div>

              <!-- Camera Controls -->
              <div
                class="absolute bottom-6 left-1/2 transform -translate-x-1/2"
              >
                <button
                  @click="startCountdown"
                  :disabled="isCountingDown"
                  class="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50"
                >
                  <div class="w-16 h-16 bg-blue-600 rounded-full"></div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4: Guest Information Form -->
        <div v-if="currentStep === 4" class="space-y-8">
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
              Guest Information
            </h2>
            <p class="text-xl text-gray-600">
              Please provide your details before proceeding
            </p>
          </div>

          <div class="max-w-md mx-auto bg-white shadow-lg rounded-2xl p-8">
            <form
              class="flex flex-col gap-4 items-center"
              @submit.prevent="validateAndSubmitUserInfo"
            >
              <h4 class="text-lg font-semibold text-gray-900 mb-2 text-center">
                Fill in your details
              </h4>
              <!-- User Type Selection -->
              <div class="mb-4 w-full">
                <div class="flex items-center mb-2">
                  <input
                    id="newUser"
                    v-model="userInfo.userType"
                    type="radio"
                    value="new"
                    class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                    @change="onUserTypeChange"
                  />
                  <label
                    for="newUser"
                    class="ml-2 text-sm font-medium text-gray-900"
                  >
                    New User
                  </label>
                </div>
                <div class="flex items-center mb-4">
                  <input
                    id="existingUser"
                    v-model="userInfo.userType"
                    type="radio"
                    value="existing"
                    class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                    @change="onUserTypeChange"
                  />
                  <label
                    for="existingUser"
                    class="ml-2 text-sm font-medium text-gray-900"
                  >
                    Existing User
                  </label>
                </div>
              </div>

              <!-- Show full form for new users -->
              <div v-if="userInfo.userType === 'new'" class="w-full">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mb-2">
                  <div class="flex flex-col">
                    <label
                      class="block text-gray-900 font-medium mb-1"
                      for="firstName"
                      >First Name</label
                    >
                    <input
                      id="firstName"
                      v-model="userInfo.firstName"
                      type="text"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-900 placeholder-gray-400"
                    />
                    <div
                      v-if="userInfoErrors.firstName"
                      class="text-red-600 text-xs mt-1"
                    >
                      {{ userInfoErrors.firstName }}
                    </div>
                  </div>
                  <div class="flex flex-col">
                    <label
                      class="block text-gray-900 font-medium mb-1"
                      for="lastName"
                      >Last Name</label
                    >
                    <input
                      id="lastName"
                      v-model="userInfo.lastName"
                      type="text"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-900 placeholder-gray-400"
                    />
                    <div
                      v-if="userInfoErrors.lastName"
                      class="text-red-600 text-xs mt-1"
                    >
                      {{ userInfoErrors.lastName }}
                    </div>
                  </div>
                </div>
                <div class="grid grid-cols-1 gap-4 w-full mb-2">
                  <div class="flex flex-col">
                    <label
                      class="block text-gray-900 font-medium mb-1"
                      for="username"
                      >Username</label
                    >
                    <input
                      id="username"
                      v-model="userInfo.username"
                      type="text"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-900 placeholder-gray-400"
                    />
                    <div
                      v-if="userInfoErrors.username"
                      class="text-red-600 text-xs mt-1"
                    >
                      {{ userInfoErrors.username }}
                    </div>
                  </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mb-2">
                  <div class="flex flex-col">
                    <label
                      class="block text-gray-900 font-medium mb-1"
                      for="email"
                      >Email</label
                    >
                    <input
                      id="email"
                      v-model="userInfo.email"
                      type="email"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-900 placeholder-gray-400"
                    />
                    <div
                      v-if="userInfoErrors.email"
                      class="text-red-600 text-xs mt-1"
                    >
                      {{ userInfoErrors.email }}
                    </div>
                  </div>
                  <div class="flex flex-col">
                    <label
                      class="block text-gray-900 font-medium mb-1"
                      for="phone"
                      >Phone</label
                    >
                    <input
                      id="phone"
                      v-model="userInfo.phone"
                      type="tel"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-900 placeholder-gray-400"
                    />
                    <div
                      v-if="userInfoErrors.phone"
                      class="text-red-600 text-xs mt-1"
                    >
                      {{ userInfoErrors.phone }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Show only username field for existing users -->
              <div v-else class="w-full">
                <div class="grid grid-cols-1 gap-4 w-full mb-2">
                  <div class="flex flex-col">
                    <label
                      class="block text-gray-900 font-medium mb-1"
                      for="username"
                      >Username</label
                    >
                    <input
                      id="username"
                      v-model="userInfo.username"
                      type="text"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-900 placeholder-gray-400"
                    />
                    <div
                      v-if="userInfoErrors.username"
                      class="text-red-600 text-xs mt-1"
                    >
                      {{ userInfoErrors.username }}
                    </div>
                  </div>
                </div>
              </div>
              <button
                type="submit"
                class="w-full bg-blue-700 text-white py-3 rounded-lg font-semibold hover:bg-blue-800 transition-all duration-200 mt-2"
              >
                Submit
              </button>
            </form>
          </div>
        </div>

        <!-- Step 5: Photo Preview -->
        <div v-if="currentStep === 5" class="space-y-8">
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">Photo Preview</h2>
            <p class="text-xl text-gray-600">
              Review your photo before generating the AI image
            </p>
          </div>

          <div class="max-w-2xl mx-auto">
            <div class="bg-white shadow-lg rounded-2xl p-6">
              <img
                :src="capturedPhoto"
                alt="Captured photo"
                class="w-full aspect-video object-cover rounded-xl mb-6"
              />

              <div class="flex gap-4 justify-center">
                <button
                  @click="generateImage"
                  class="px-8 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all duration-300"
                >
                  Generate AI Image
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 6: Generation & Results -->
        <div v-if="currentStep === 6" class="space-y-8">
          <!-- Loading State -->
          <div v-if="isGenerating" class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
              Generating Your Image
            </h2>
            <p class="text-xl text-gray-600 mb-8">
              Please wait while AI creates your masterpiece
            </p>

            <div class="max-w-md mx-auto bg-white shadow-lg rounded-2xl p-8">
              <div class="relative w-32 h-32 mx-auto mb-6">
                <div
                  class="absolute inset-0 border-4 border-blue-300/30 rounded-full"
                ></div>
                <div
                  class="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"
                ></div>
                <div
                  class="absolute inset-4 bg-blue-600 rounded-full flex items-center justify-center"
                >
                  <svg
                    class="w-8 h-8 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    ></path>
                  </svg>
                </div>
              </div>

              <div class="space-y-2">
                <div class="text-gray-900 font-semibold">
                  {{ generationProgress }}%
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    :style="{ width: generationProgress + '%' }"
                  ></div>
                </div>
                <div class="text-gray-600 text-sm">{{ generationStatus }}</div>
              </div>
            </div>
          </div>

          <!-- Results -->
          <div v-else class="text-center">
            <h2 class="text-4xl font-bold text-black mb-4">
              Your AI Generated Image
            </h2>
            <p class="text-xl text-black/70 mb-8">
              Amazing! Here's your transformed image
            </p>

            <div class="max-w-4xl mx-auto">
              <div class="flex flex-col items-center justify-center mb-8">
                <div
                  class="bg-white/20 backdrop-blur-lg shadow-2xl rounded-3xl p-6 w-full max-w-md mx-auto"
                >
                  <h3 class="text-2xl font-bold text-center text-white mb-4">
                    AI Generated Image
                    <span
                      v-if="selectedModel?.name"
                      class="block text-sm font-medium text-emerald-200 mt-1"
                    >
                      ({{ selectedModel?.name }})
                    </span>
                  </h3>
                  <img
                    :src="generatedImage"
                    alt="Generated image"
                    class="w-full max-w-xs aspect-square object-cover rounded-2xl border-4 border-emerald-400 shadow-xl mx-auto transition-all duration-300"
                    style="background: rgba(255, 255, 255, 0.18)"
                  />
                  <!-- Action Buttons -->
                  <div v-if="userInfoValid">
                    <div
                      class="flex flex-row gap-4 justify-center"
                      style="margin-top: 20px"
                    >
                      <button
                        @click="printImage"
                        class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl font-semibold hover:from-green-600 hover:to-emerald-600 transition-all duration-300"
                      >
                        <svg
                          class="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M6 9V2h12v7"
                          />
                          <rect x="6" y="13" width="12" height="8" rx="2" />
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M6 17h12"
                          />
                        </svg>
                        Print
                      </button>

                      <!--<button
                        @click="shareViaEmail"
                        class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-xl font-semibold hover:from-blue-600 hover:to-cyan-600 transition-all duration-300"
                      >
                        <svg
                          class="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                          ></path>
                        </svg>
                        Email
                      </button>-->

                      <button
                        @click="generateQRCode"
                        class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
                      >
                        <svg
                          class="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                          ></path>
                        </svg>
                        QR Code
                      </button>
                    </div>
                    <div class="flex justify-center mt-6">
                      <button
                        @click="startOver"
                        class="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all duration-300"
                        title="Back to Step 1"
                      >
                        <svg
                          class="w-6 h-6"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 5l-7 7 7 7M22 12H3"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- QR Code Modal -->
      <div
        v-if="showQRModal"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
        @click="showQRModal = false"
      >
        <div class="bg-white rounded-2xl p-8 max-w-sm mx-4" @click.stop>
          <h3 class="text-2xl font-bold text-gray-800 mb-4 text-center">
            QR Code
          </h3>
          <div
            class="bg-gray-100 p-4 rounded-xl mb-4 flex items-center justify-center"
          >
            <img
              v-if="qrCodeImage"
              :src="qrCodeImage"
              alt="QR Code"
              class="w-48 h-48"
            />
            <QRCodeDisplay v-else :value="qrValue" />
          </div>
          <p class="text-gray-600 text-center text-sm mb-4">
            Scan to view your generated image
          </p>
          <button
            @click="showQRModal = false"
            class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-xl font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from "vue";
import { handleError } from "@/utils/errorHandler";
import axiosInstance from "@/plugins/axios";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "vue-toast-notification";
import "vue-toast-notification/dist/theme-sugar.css";
import FullscreenButton from "../../components/FullscreenButton.vue";
import QRCodeDisplay from "@/components/QRCodeDisplay.vue";
import { useEventService } from "@/services/api/event";
import { useOrganizationStore } from "@/stores/organization";

export default {
  name: "AIImageGenerator",
  components: {
    FullscreenButton,
    QRCodeDisplay,
  },
  data() {
    return {
      userInfo: {
        userType: "new",
        firstName: "",
        lastName: "",
        username: "",
        email: "",
        phone: "",
      },
      userInfoErrors: {
        firstName: "",
        lastName: "",
        username: "",
        email: "",
        phone: "",
      },
      guestId: null,
      fullscreenMode: false,
      userInfoValid: false,
      qrValue: "",
      qrCodeImage: "",
    };
  },
  computed: {
    showEventSelection() {
      return !this.fullscreenMode;
    },
  },
  mounted() {
    this.loadStoredGuestInfo();

    if (localStorage.getItem("fullscreenMode") === "true") {
      this.fullscreenMode = true;
    }

    // Add event listener to clear fullscreen mode on tab close
    window.addEventListener("beforeunload", this.handleBeforeUnload);

    // Add message event listener to detect fullscreen tab closure
    window.addEventListener("message", this.handleFullscreenTabClose);
  },

  beforeUnmount() {
    // Clean up the event listeners
    window.removeEventListener("beforeunload", this.handleBeforeUnload);
    window.removeEventListener("message", this.handleFullscreenTabClose);
  },
  methods: {
    handleBeforeUnload() {
      // Clear fullscreen mode from localStorage
      localStorage.removeItem("fullscreenMode");

      // Send message to main tab that fullscreen is closing
      if (this.fullscreenMode) {
        window.opener.postMessage("fullscreen-closed", "*");
      }
    },

    handleFullscreenTabClose(event) {
      if (event.data === "fullscreen-closed") {
        // Refresh the main tab when fullscreen tab closes
        window.location.reload();
      }
    },
    loadStoredGuestInfo() {
      //const storedGuestId = localStorage.getItem("guestId");
      const storedGuestUsername = localStorage.getItem("guestUsername");

      if (storedGuestUsername) {
        this.userInfo = {
          userType: "existing",
          firstName: "",
          lastName: "",
          username: storedGuestUsername,
          email: "",
          phone: "",
        };
        //this.guestId = storedGuestId;
        this.userInfoValid = true;
      } else {
        this.resetGuestForm();
      }
    },

    resetGuestForm() {
      this.userInfo.firstName = "";
      this.userInfo.lastName = "";
      this.userInfo.username = "";
      this.userInfo.email = "";
      this.userInfo.phone = "";
      this.userInfoErrors = {
        firstName: "",
        lastName: "",
        username: "",
        email: "",
        phone: "",
      };
    },

    onUserTypeChange() {
      this.resetGuestForm();
    },

    validateAndSubmitUserInfo() {
      const { userType, username, firstName, lastName, email, phone } =
        this.userInfo;

      // Reset errors
      this.userInfoErrors = {
        firstName: "",
        lastName: "",
        username: "",
        email: "",
        phone: "",
      };

      let valid = true;

      // Validate username for both user types
      if (!username) {
        this.userInfoErrors.username = "Username is required.";
        valid = false;
      } else if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
        this.userInfoErrors.username =
          "Username must be 3-20 characters and can include letters, numbers, and underscores.";
        valid = false;
      }

      // Only validate other fields for new users
      if (userType === "new") {
        if (!firstName) {
          this.userInfoErrors.firstName = "First name is required.";
          valid = false;
        }
        if (!lastName) {
          this.userInfoErrors.lastName = "Last name is required.";
          valid = false;
        }
        if (!email) {
          this.userInfoErrors.email = "Email is required.";
          valid = false;
        } else if (!/^\S+@\S+\.\S+$/.test(email)) {
          this.userInfoErrors.email = "Please enter a valid email address.";
          valid = false;
        }
        if (!phone) {
          this.userInfoErrors.phone = "Phone is required.";
          valid = false;
        } else if (!/^\+?[0-9\-\s]{7,}$/.test(phone)) {
          this.userInfoErrors.phone = "Please enter a valid phone number.";
          valid = false;
        }
      }

      if (!valid) return;

      // Clear localStorage for new users
      if (this.userInfo.userType === "new") {
        //localStorage.removeItem("guestId");
        localStorage.removeItem("guestUsername");
      }

      this.registerGuest();
    },

    async registerGuest() {
      const toast = useToast();
      try {
        const { userType, username, firstName, lastName, email, phone } =
          this.userInfo;
        const eventId = this.selectedEventId;

        const payload = {
          username,
          first_name: firstName,
          last_name: lastName,
          mail: email,
          phone_number: phone,
          //event_id: eventId,
        };

        if (userType === "new") {
          // Create new guest
          const response = await axiosInstance.post("/api/v1/guests/", payload);
          this.guestId = response.data.id;

          // Store new guest info
          //localStorage.setItem("guestId", this.guestId);
          //localStorage.setItem("guestUsername", this.userInfo.username);
        } else {
          // Connect existing guest
          const response = await axiosInstance.post("/api/v1/guests/connect", {
            username,
            //event_id: eventId,
          });

          if (!response.data.exists) {
            toast.error(
              "Guest not found. Please check your username or register as a new user.",
              {
                position: "top-right",
                duration: 5000,
              }
            );
            return;
          }

          // Update guest ID and store username
          this.guestId = response.data.guest_id;
          localStorage.setItem("guestUsername", this.userInfo.username);
        }

        this.userInfoValid = true;
        this.nextStep(); // Proceed to next step
        toast.success("Guest registration successful!", {
          position: "top-right",
          duration: 3000,
        });
      } catch (error) {
        console.error("Guest registration error:", error);

        // Improved error handling to prevent [object Object]
        let errorMessage = "An unknown error occurred";
        if (error.response) {
          if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data) {
            errorMessage = JSON.stringify(error.response.data);
          } else {
            errorMessage = `Server responded with status ${error.response.status}`;
          }
        } else if (error.request) {
          errorMessage = "No response from server";
        } else if (error.message) {
          errorMessage = error.message;
        }

        toast.error(`Guest registration failed: ${errorMessage}`, {
          position: "top-right",
          duration: 5000,
        });
      }
    },

    async generateImage() {
      if (!this.userInfoValid) {
        const toast = useToast();
        toast.error("Please complete guest registration first", {
          position: "top-right",
          duration: 3000,
        });
        return;
      }

      const toast = useToast();
      this.nextStep();
      this.isGenerating = true;
      this.generationProgress = 0;
      this.generationStatus = "Initializing...";

      // Simulate progress updates
      const statuses = [
        "Analyzing your photo...",
        "Applying AI model...",
        "Enhancing details...",
        "Adding artistic touches...",
        "Finalizing image...",
      ];
      let statusIndex = 0;
      const progressInterval = setInterval(() => {
        if (this.generationProgress < 90) {
          this.generationProgress += Math.random() * 10 + 2;
        }
        if (
          statusIndex < statuses.length - 1 &&
          this.generationProgress > (statusIndex + 1) * 18
        ) {
          statusIndex++;
          this.generationStatus = statuses[statusIndex];
        }
      }, 200);

      try {
        const base64Data = this.capturedPhoto.split("base64,")[1] || "";
        //const eventId = localStorage.getItem("eventId");
        //const guestId = localStorage.getItem("guestId");
        const payload = {
          source_image: base64Data,
          model_id: this.selectedModel.id,
          //event_id: eventId,
          //guest_id: guestId,
        };

        const response = await axiosInstance.post(
          "/api/v1/images/generate",
          payload
        );

        clearInterval(progressInterval);
        this.generationProgress = 100;
        this.generationStatus = "Complete!";

        setTimeout(() => {
          this.isGenerating = false;
          this.generatedImage = `data:image/jpeg;base64,${response.data.generated_image}`;

          // Check if QR code is present in the response
          if (response.data.qr_code) {
            this.qrCodeImage = `${response.data.qr_code}`;
            this.qrValue = ""; // Clear the text QR code if we have an image
          } else if (response.data.qr_url) {
            this.qrValue = response.data.qr_url; // Fallback to URL if no QR image
          }

          toast.success("Image generated successfully!", {
            position: "top-right",
            duration: 3000,
          });
        }, 1000);
      } catch (error) {
        console.error("Error generating image:", error);
        clearInterval(progressInterval);

        let errorMessage = "An unknown error occurred";
        if (error.response) {
          if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data) {
            errorMessage = JSON.stringify(error.response.data);
          } else {
            errorMessage = `Server responded with status ${error.response.status}`;
          }
        } else if (error.request) {
          errorMessage = "No response from server";
        } else if (error.message) {
          errorMessage = error.message;
        }

        toast.error(`Image generation failed: ${errorMessage}`, {
          position: "top-right",
          duration: 5000,
        });

        setTimeout(() => {
          this.isGenerating = false;
          this.currentStep = 5;
        }, 1000);
      }
    },

    printImage() {
      const printWindow = window.open("", "_blank");
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Generated Image</title>
          <style>
            @page {
              size: auto;
              margin: 0;
            }
            body {
              margin: 0;
              padding: 0;
              display: flex;
              justify-content: center;
              align-items: center;
              min-height: 100vh;
              background: white;
            }
            .print-container {
              max-width: 100%;
              max-height: 100vh;
              text-align: center;
              padding: 20px;
              box-sizing: border-box;
            }
            .print-image {
              max-width: 100%;
              max-height: 95vh;
              width: auto;
              height: auto;
              object-fit: contain;
              display: block;
              margin: 0 auto;
            }
            @media print {
              body * {
                visibility: hidden;
              }
              .print-container, .print-container * {
                visibility: visible;
              }
              .print-container {
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                padding: 0;
                margin: 0;
              }
            }
          </style>
          <script>
            // Close window after printing
            window.onafterprint = function() {
              window.close();
            };
            // Auto-print when window loads
            window.onload = function() {
              setTimeout(function() {
                window.print();
              }, 500);
            };
          <\/script>
        </head>
        <body>
          <div class="print-container">
            <img class="print-image" src="${this.generatedImage}" alt="Generated Image" />
          </div>
        </body>
        </html>
      `);
      printWindow.document.close();
    },

    async handleFullscreenClick() {
      const orgStore = useOrganizationStore();

      orgStore.setEventId(this.selectedEventId);
      this.fullscreenMode = true;
      localStorage.setItem("fullscreenMode", "true");
      //localStorage.setItem("eventId", this.selectedEventId);

      try {
        // Set event context in Redis
        await axiosInstance.post("/api/v1/event/set_event_context", {
          event_id: this.selectedEventId,
        });

        // Open fullscreen mode
        window.open("/fullscreen-image-generation", "_blank");
      } catch (error) {
        console.error("Failed to set event context:", error);
        toast.error("Failed to set event context. Please try again.");
      }
    },

    startOver() {
      // Stop any active streams
      if (this.stream) {
        this.stream.getTracks().forEach((track) => track.stop());
        this.stream = null;
      }

      // Reset all state variables
      this.currentStep = 1;
      this.selectedModel = null;
      this.isCountingDown = false;
      this.countdown = 3;
      this.capturedPhoto = null;
      this.isGenerating = false;
      this.generationProgress = 0;
      this.generationStatus = "Initializing...";
      this.generatedImage = null;
      //this.fullscreenMode = false;
      this.selectedEventId = "";

      // Reset guest information
      this.resetGuestForm();
      //localStorage.removeItem("guestId");
      //localStorage.removeItem("guestUsername");
      //localStorage.removeItem("fullscreenMode");
    },
  },
  setup() {
    // Reactive state
    const currentStep = ref(1);
    const selectedModel = ref(null);
    const isRequestingPermission = ref(false);
    const isCountingDown = ref(false);
    const countdown = ref(3);
    const capturedPhoto = ref(null);
    const isGenerating = ref(false);
    const generationProgress = ref(0);
    const generationStatus = ref("Initializing...");
    const generatedImage = ref(null);
    const showQRModal = ref(false);
    const videoElement = ref(null);
    const stream = ref(null);
    const modelSearch = ref("");
    const modelCategory = ref("");
    const hasCameraPermission = ref(false);
    const events = ref([]);
    const selectedEventId = ref("");
    const loadingEvents = ref(false);
    const guestId = ref(null);
    const userInfoValid = ref(false);

    // Models data
    const models = ref([]);

    // Methods
    const selectModel = async (model) => {
      selectedModel.value = model;
      // Check camera permission
      try {
        const cameraStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
        cameraStream.getTracks().forEach((track) => track.stop());
        hasCameraPermission.value = true;
      } catch (e) {
        hasCameraPermission.value = false;
      }
      // If permission is granted, skip step 2
      if (hasCameraPermission.value) {
        currentStep.value = 3;
      } else {
        nextStep();
      }
    };

    // Fetch models from API using axios
    const fetchModels = async () => {
      try {
        // Get the auth store to access organization ID
        const authStore = useAuthStore();
        const orgId = authStore.organization_id;

        // Use axios to fetch models
        const response = await axiosInstance.get("/api/v1/models/list");
        const data = response.data;

        // Add fallback icons and ensure all required properties exist
        models.value = data.map((model) => ({
          ...model,
          icon: model.icon || "🖼️",
          preview_url: model.preview_url || "",
          category: model.category?.name || model.category,
        }));

        console.log("Fetched models:", models.value);
      } catch (error) {
        console.error("Error fetching models:", error);
        models.value = [];
        handleError(error, "Failed to fetch models");
      }
    };

    const nextStep = () => {
      if (currentStep.value < 6) {
        currentStep.value++;
      }
    };

    const requestCameraPermission = async () => {
      const toast = useToast();

      // If we're not on the permission screen yet, go to it first
      if (currentStep.value !== 2) {
        nextStep();
        return;
      }

      // We're on the permission screen, so try to get permission
      isRequestingPermission.value = true;

      try {
        stream.value = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
          audio: false,
        });

        // If we get here, permission was granted
        console.log("Camera permission granted");
        hasCameraPermission.value = true;

        // Go to camera view step
        nextStep();

        // Setup video element
        if (videoElement.value && stream.value) {
          videoElement.value.srcObject = stream.value;
        }
      } catch (error) {
        console.error("Camera permission error:", error);

        // Check if this is a permission error
        if (
          error.name === "NotAllowedError" ||
          error.name === "PermissionDeniedError"
        ) {
          toast.error(
            "Camera access was denied. Please enable it in your browser settings.",
            {
              position: "top-right",
              duration: 5000,
            }
          );
          hasCameraPermission.value = false;
        } else {
          toast.error(`Camera error: ${error.message}`, {
            position: "top-right",
            duration: 5000,
          });
        }
      } finally {
        isRequestingPermission.value = false;
      }
    };

    const startCountdown = () => {
      isCountingDown.value = true;
      countdown.value = 3;

      const countdownInterval = setInterval(() => {
        countdown.value--;
        if (countdown.value === 0) {
          clearInterval(countdownInterval);
          capturePhoto();
          isCountingDown.value = false;
        }
      }, 1000);
    };

    const capturePhoto = () => {
      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      const video = videoElement.value;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);

      capturedPhoto.value = canvas.toDataURL("image/jpeg");

      // Stop the video stream
      if (stream.value) {
        stream.value.getTracks().forEach((track) => track.stop());
      }

      // Go to guest form step
      nextStep();
    };

    const retakePhoto = async () => {
      // Go directly to camera view (step 3)
      currentStep.value = 3;
      capturedPhoto.value = null;

      // Reinitialize the camera stream
      try {
        stream.value = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
          audio: false,
        });

        // The watcher will handle setting up the video stream since we're changing the step
      } catch (error) {
        console.error("Error reinitializing camera:", error);
        // If we can't get the camera, go back to permission screen
        currentStep.value = 2;
      }
    };

    const downloadImage = async () => {
      const toast = useToast();
      try {
        if (!generatedImage.value) {
          throw new Error("No image available to download");
        }

        const link = document.createElement("a");
        link.href = generatedImage.value;
        link.download = `generated-image-${Date.now()}.jpg`;

        // Validate data URL
        if (!generatedImage.value.startsWith("data:image/")) {
          throw new Error("Invalid image format");
        }

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        toast.success("Image downloaded successfully", {
          position: "top-right",
          duration: 3000,
        });
      } catch (error) {
        console.error("Download error:", error);
        toast.error(`Failed to download image: ${error.message}`, {
          position: "top-right",
          duration: 5000,
        });
      }
    };

    const shareViaEmail = () => {
      const toast = useToast();
      try {
        if (!generatedImage.value) {
          throw new Error("No image available to share");
        }

        const subject = encodeURIComponent("Check out my AI-generated image!");
        const body = encodeURIComponent(
          "I created this image using the AI Image Generator. Take a look!"
        );

        window.location.href = `mailto:?subject=${subject}&body=${body}`;

        toast.success("Email client opened", {
          position: "top-right",
          duration: 3000,
        });
      } catch (error) {
        console.error("Share error:", error);
        toast.error(`Failed to share image: ${error.message}`, {
          position: "top-right",
          duration: 5000,
        });
      }
    };

    const generateQRCode = () => {
      showQRModal.value = true;
    };

    // Setup video stream when reaching camera step
    const setupVideoStream = async () => {
      if (currentStep.value === 3) {
        try {
          // Stop any existing stream
          if (stream.value) {
            stream.value.getTracks().forEach((track) => track.stop());
          }

          // Get new stream with explicit constraints
          stream.value = await navigator.mediaDevices.getUserMedia({
            video: {
              facingMode: "user",
              width: { ideal: 1280 },
              height: { ideal: 720 },
            },
            audio: false,
          });

          // Make sure video element is available
          if (!videoElement.value) {
            console.error("Video element not found");
            return;
          }

          // Set source and play
          videoElement.value.srcObject = stream.value;
          videoElement.value.muted = true;

          // Force play
          try {
            await videoElement.value.play();
            console.log("Camera video playback started");
          } catch (err) {
            console.error("Error playing video:", err);
            // Try again with muted
            videoElement.value.muted = true;
            await videoElement.value.play();
          }

          hasCameraPermission.value = true;
        } catch (error) {
          console.error("Camera setup error:", error);
          hasCameraPermission.value = false;

          // If we're on the camera step but can't access camera, go back to permission step
          if (currentStep.value === 3) {
            currentStep.value = 2;
          }
        }
      }
    };

    // Watch for step changes
    watch(currentStep, async (newStep) => {
      console.log("Step changed to:", newStep);
      if (newStep === 3) {
        await nextTick();
        setupVideoStream();
      }
    });

    // Initialize component
    onMounted(async () => {
      // Fetch models from API when component mounts
      fetchModels();

      // Try to access the camera to check permission
      try {
        const cameraStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
        hasCameraPermission.value = true;
        cameraStream.getTracks().forEach((track) => track.stop());
      } catch (error) {
        hasCameraPermission.value = false;
      }
      // If model is selected and permission is granted, skip to camera view
      if (selectedModel.value && hasCameraPermission.value) {
        currentStep.value = 3;
      }

      const authStore = useAuthStore();
      const orgId = authStore.organization_id;
      if (!orgId) return;
      loadingEvents.value = true;
      try {
        const eventService = useEventService();
        const allEvents = await eventService.getEventsByOrganization(orgId);
        events.value = allEvents.filter((e) => e.active);
      } finally {
        loadingEvents.value = false;
      }
    });

    // Cleanup
    onUnmounted(() => {
      if (stream.value) {
        stream.value.getTracks().forEach((track) => track.stop());
      }
    });

    // Computed properties for filtering
    const uniqueCategories = computed(() => {
      const categories = models.value.map((model) => model.category);
      return [...new Set(categories)];
    });

    const filteredModels = computed(() => {
      return models.value.filter((model) => {
        // Filter by search term
        const searchMatch =
          modelSearch.value === "" ||
          model.name.toLowerCase().includes(modelSearch.value.toLowerCase()) ||
          model.description
            .toLowerCase()
            .includes(modelSearch.value.toLowerCase());

        // Filter by category
        const categoryMatch =
          modelCategory.value === "" || model.category === modelCategory.value;

        return searchMatch && categoryMatch;
      });
    });

    // Method to get category count
    const getCategoryCount = (category) => {
      return models.value.filter((model) => model.category === category).length;
    };

    return {
      currentStep,
      selectedModel,
      models,
      modelSearch,
      modelCategory,
      uniqueCategories,
      filteredModels,
      isRequestingPermission,
      isCountingDown,
      countdown,
      capturedPhoto,
      isGenerating,
      generationProgress,
      generationStatus,
      generatedImage,
      showQRModal,
      videoElement,
      hasCameraPermission,
      selectModel,
      nextStep,
      requestCameraPermission,
      startCountdown,
      retakePhoto,
      downloadImage,
      shareViaEmail,
      generateQRCode,
      getCategoryCount,
      fetchModels,
      events,
      selectedEventId,
      loadingEvents,
      guestId,
      userInfoValid,
    };
  },
};
</script>
