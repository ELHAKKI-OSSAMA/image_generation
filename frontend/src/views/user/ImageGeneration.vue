<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-white"
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
            <h1 class="text-2xl font-bold text-gray-900">AI Image Generator</h1>
          </div>
          <div class="flex items-center gap-4">
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
            <div class="text-sm text-gray-600">Step {{ currentStep }} of 5</div>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8">
      <!-- Step 1: Model Selection -->
      <div v-if="currentStep === 1" class="space-y-8">
        <div class="text-center">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">
            Choose Your AI Model
          </h2>
          <p class="text-xl text-gray-600">
            Select the style for your generated image
          </p>
        </div>

        <!-- Search and Filter Bar -->
        <div class="flex flex-col sm:flex-row gap-4 mb-6 max-w-4xl mx-auto">
          <div class="flex-1">
            <div class="relative">
              <input
                type="text"
                v-model="modelSearch"
                placeholder="Search models..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <span class="absolute left-3 top-2.5 text-gray-400">
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
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </span>
            </div>
          </div>
          <div class="flex gap-2 sm:w-auto">
            <select
              v-model="modelCategory"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Categories</option>
              <option value="realistic">Realistic</option>
              <option value="artistic">Artistic</option>
              <option value="fantasy">Fantasy</option>
            </select>
            <button
              @click="modelCategory = ''"
              v-if="modelCategory"
              class="px-3 py-2 text-gray-600 hover:text-gray-800 focus:outline-none"
              title="Clear filter"
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Category Pills -->
        <div class="flex flex-wrap gap-2 mb-6 max-w-4xl mx-auto">
          <button
            v-for="category in uniqueCategories"
            :key="category"
            @click="modelCategory = modelCategory === category ? '' : category"
            class="px-3 py-1 rounded-full text-sm font-medium transition-colors duration-200"
            :class="
              modelCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            "
          >
            {{ category }}
            <span class="ml-1 text-xs">{{ getCategoryCount(category) }}</span>
          </button>
        </div>

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
            <div class="relative aspect-square mb-4 overflow-hidden rounded-xl">
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

        <div class="text-center">
          <button
            @click="nextStep"
            :disabled="!selectedModel"
            :class="[
              'px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300',
              selectedModel
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed',
            ]"
          >
            Continue with {{ selectedModel?.name || "Selected Model" }}
          </button>
        </div>
      </div>

      <!-- Step 2: Camera Permission -->
      <div v-if="currentStep === 2" class="space-y-8">
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
            You've already granted camera permission. Click the button below to
            access your camera.
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
          <h2 class="text-4xl font-bold text-gray-900 mb-4">Take Your Photo</h2>
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
              class="w-full aspect-video object-cover"
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
            <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2">
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

      <!-- Step 4: Photo Preview -->
      <div v-if="currentStep === 4" class="space-y-8">
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
                @click="retakePhoto"
                class="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all duration-300"
              >
                Retake Photo
              </button>
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

      <!-- Step 5: Generation & Results -->
      <div v-if="currentStep === 5" class="space-y-8">
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
          <h2 class="text-4xl font-bold text-white mb-4">
            Your AI Generated Image
          </h2>
          <p class="text-xl text-white/70 mb-8">
            Amazing! Here's your transformed image
          </p>

          <div class="max-w-4xl mx-auto">
            <div class="grid md:grid-cols-2 gap-8 mb-8">
              <!-- Original Photo -->
              <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">
                  Original Photo
                </h3>
                <img
                  :src="capturedPhoto"
                  alt="Original photo"
                  class="w-full aspect-square object-cover rounded-xl"
                />
              </div>

              <!-- Generated Image -->
              <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">
                  AI Generated ({{ selectedModel?.name }})
                </h3>
                <img
                  :src="generatedImage"
                  alt="Generated image"
                  class="w-full aspect-square object-cover rounded-xl"
                />
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-wrap gap-4 justify-center">
              <button
                @click="downloadImage"
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
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  ></path>
                </svg>
                Download
              </button>

              <button
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
              </button>

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

              <button
                @click="startOver"
                class="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all duration-300"
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
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  ></path>
                </svg>
                Back to Step 1
              </button>
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
        <div class="bg-gray-100 p-4 rounded-xl mb-4">
          <div
            class="w-48 h-48 bg-black mx-auto flex items-center justify-center text-white text-xs"
          >
            QR Code Placeholder<br />
            (Would contain actual QR code)
          </div>
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
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { handleError } from "@/utils/errorHandler";
import { useToast } from "vue-toast-notification";
import "vue-toast-notification/dist/theme-sugar.css";

export default {
  name: "AIImageGenerator",
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
    const hasCameraPermission = ref(false); // Will be set properly in onMounted

    // Models data
    const models = ref([]);

    // Methods
    const selectModel = (model) => {
      selectedModel.value = model;
    };

    // Fetch models from API
    const fetchModels = async () => {
      try {
        // Try the original endpoint first
        let response = await fetch(import.meta.env.VITE_API_URL +"/api/v1/models/list");

        // If that fails, try the alternative endpoint
        if (!response.ok) {
          console.log("Trying alternative endpoint...");
          response = await fetch(import.meta.env.VITE_API_URL +"/api/v1/models/list");
        }

        if (!response.ok) {
          throw new Error(
            `Failed to fetch models: ${response.status} ${response.statusText}`
          );
        }

        // Ensure the response is JSON
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new Error(
            "Invalid response format: Expected JSON but got something else"
          );
        }

        // Get the models and add fallback icons if needed
        const data = await response.json();

        // Map icons to categories if they're missing
        const iconMap = {
          realistic: "📸",
          artistic: "🎨",
          fantasy: "✨",
          portrait: "👤",
          cartoon: "🎭",
          scifi: "🚀",
        };

        // Add fallback icons and ensure all required properties exist
        models.value = data.map((model) => ({
          ...model,
          icon: model.icon || iconMap[model.category] || "🖼️",
          preview_url: model.preview_url || "",
        }));

        console.log("Fetched models:", models.value);
      } catch (error) {
        console.error("Error fetching models:", error);
        // Add some fallback models if the API fails
        models.value = [
          {
            id: "realistic",
            name: "Realistic",
            description:
              "Photorealistic style with natural lighting and details",
            icon: "📸",
            category: "realistic",
            preview_url: "",
          },
          {
            id: "artistic",
            name: "Artistic",
            description:
              "Creative artistic interpretation with enhanced colors",
            icon: "🎨",
            category: "artistic",
            preview_url: "",
          },
          {
            id: "fantasy",
            name: "Fantasy",
            description:
              "Magical and fantastical elements with vibrant effects",
            icon: "✨",
            category: "fantasy",
            preview_url: "",
          },
        ];
      }
    };

    const nextStep = () => {
      if (currentStep.value < 5) {
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
        // This will either:
        // 1. Use existing permission if already granted
        // 2. Show the browser's permission dialog if not yet decided
        // 3. Throw an error if permission was denied
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

      nextStep();
    };

    const retakePhoto = async () => {
      // Go directly to camera view (step 3) instead of step 2
      currentStep.value = 3;
      capturedPhoto.value = null;
      
      // Need to reinitialize the camera stream since we stopped it when taking the photo
      try {
        stream.value = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user' },
          audio: false
        });
        
        // The watcher will handle setting up the video stream since we're changing the step
      } catch (error) {
        console.error('Error reinitializing camera:', error);
        // If we can't get the camera, go back to permission screen
        currentStep.value = 2;
      }
    };

    const generateImage = async () => {
      if (!selectedModel.value || !capturedPhoto.value) return;

      const toast = useToast();
      nextStep();
      isGenerating.value = true;
      generationProgress.value = 0;
      generationStatus.value = "Initializing...";

      // Simulate progress updates while waiting for API response
      const statuses = [
        "Analyzing your photo...",
        "Applying AI model...",
        "Enhancing details...",
        "Adding artistic touches...",
        "Finalizing image...",
      ];

      let statusIndex = 0;
      const progressInterval = setInterval(() => {
        // Don't go all the way to 100% until we get the response
        if (generationProgress.value < 90) {
          generationProgress.value += Math.random() * 10 + 2;
        }

        if (
          statusIndex < statuses.length - 1 &&
          generationProgress.value > (statusIndex + 1) * 18
        ) {
          statusIndex++;
          generationStatus.value = statuses[statusIndex];
        }
      }, 200);

      try {
        // Extract the Base64 data
        const base64Data = capturedPhoto.value.split("base64,")[1] || "";
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 60000); // 60 seconds timeout

        // Prepare the payload
        const payload = {
          source_image: base64Data, // Key to match backend expectation
          model_id: selectedModel.value.id, // Key to match backend expectation
        };

        const response = await fetch(
          import.meta.env.VITE_API_URL +"/api/images/generate",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          const errorText = await response.text().catch(() => "Unknown error");
          throw new Error(`Server error (${response.status}): ${errorText}`);
        }

        const data = await response.json();

        // Complete the progress
        clearInterval(progressInterval);
        generationProgress.value = 100;
        generationStatus.value = "Complete!";

        setTimeout(() => {
          isGenerating.value = false;
          generatedImage.value = `data:image/jpeg;base64,${data.generated_image}`;
          toast.success("Image generated successfully!", {
            position: "top-right",
            duration: 3000,
          });
        }, 1000);
      } catch (error) {
        console.error("Error generating image:", error);
        clearInterval(progressInterval);

        // Show error toast notification
        toast.error(`Image generation failed: ${error.message}`, {
          position: "top-right",
          duration: 5000,
        });

        // Reset to step 4 (photo preview) to let the user try again
        setTimeout(() => {
          isGenerating.value = false;
          currentStep.value = 4;
        }, 1000);
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

        // Note: We can't attach the image directly via mailto, so we'd need a server-side solution
        // This is just a basic email composition link
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

    const startOver = () => {
      // Stop any active streams
      if (stream.value) {
        stream.value.getTracks().forEach((track) => track.stop());
        stream.value = null;
      }

      // Reset all state variables
      currentStep.value = 1;
      selectedModel.value = null;
      isCountingDown.value = false;
      countdown.value = 3;
      capturedPhoto.value = null;
      isGenerating.value = false;
      generationProgress.value = 0;
      generationStatus.value = "Initializing...";
      generatedImage.value = null;

      // Keep the model search and category filters as they were
      // as they're useful for the user to maintain between sessions
    };

    // Setup video stream when reaching camera step
    const setupVideoStream = async () => {
      if (currentStep.value === 3 && stream.value && videoElement.value) {
        videoElement.value.srcObject = stream.value;

        
        // Explicitly start the video playback
        try {
          await videoElement.value.play();
          console.log('Camera video playback started');
        } catch (err) {
          console.error('Error starting camera video:', err);
        }


      }
    };

    // Watch for step changes
    const watchStep = () => {
      if (currentStep.value === 3) {
        setTimeout(setupVideoStream, 100);
      }
    };
    watch(currentStep, (newStep) => {
      console.log("Step changed to:", newStep);
      watchStep(); // Call the existing watchStep function when step changes
    });
    // Initialize component
    onMounted(async () => {
      // Fetch models from API when component mounts
      fetchModels();

      // IMPORTANT: We'll immediately try to access the camera
      // This is the most reliable way to check if permission is granted
      try {
        console.log("Checking camera permission status...");

        // Set a short timeout to make this non-blocking
        const cameraCheckPromise = navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });

        // Comment out the timeout as it's causing issues with permission detection
        /*
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => {
            console.log('TIMEOUT TRIGGERED - this is likely causing the issue');
            reject(new Error('Permission check timeout'));
          }, 500);
        });
        
        // Race between actual check and timeout
        try {
          const cameraStream = await Promise.race([cameraCheckPromise, timeoutPromise]);
          console.log('CAMERA CHECK SUCCEEDED before timeout');
        } catch (err) {
          console.log('RACE ERROR:', err.message);
          throw err; // Re-throw to maintain original behavior
        }
        */

        // Use the camera check directly without a timeout
        const cameraStream = await cameraCheckPromise;
        console.log("CAMERA CHECK SUCCEEDED without timeout");

        // If we get here without an error, permission is already granted
        console.log("Camera permission is already granted");
        hasCameraPermission.value = true;
        console.log("hasCameraPermission set to:", hasCameraPermission.value);

        // We don't need this stream yet, so stop it
        cameraStream.getTracks().forEach((track) => track.stop());

        // AUTO-ADVANCE to step 3 if user already has permission
        // This skips the camera permission screen entirely
        if (currentStep.value === 1 && selectedModel.value) {
          currentStep.value = 3; // Skip directly to camera view
        }
      } catch (error) {
        // This is expected if permission isn't granted yet
        console.log("Camera permission check:", error.name);
        hasCameraPermission.value = false;
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
      generateImage,
      downloadImage,
      shareViaEmail,
      generateQRCode,
      startOver,
      getCategoryCount,
      watchStep,
      fetchModels,
    };
  },
};
</script>
