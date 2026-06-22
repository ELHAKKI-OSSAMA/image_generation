<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <!-- Filter Section -->
    <div class="mb-8 p-6 bg-white rounded-xl shadow-lg">
      <h2 class="text-2xl font-semibold mb-4 text-gray-700">Filter Images</h2>
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-end"
      >
        <div>
          <label
            for="eventFilter"
            class="block text-sm font-medium text-gray-600 mb-1"
            >Filter by Event:</label
          >
          <select
            v-model="selectedEventId"
            id="eventFilter"
            class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 transition-shadow duration-150 hover:shadow-md"
          >
            <option value="">All Events</option>
            <option
              v-for="event in availableEvents"
              :key="event.id"
              :value="event.id"
            >
              {{ event.name }}
            </option>
          </select>
        </div>
        <div>
          <label
            for="modelFilter"
            class="block text-sm font-medium text-gray-600 mb-1"
            >Filter by Model:</label
          >
          <select
            v-model="selectedModelId"
            id="modelFilter"
            class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 transition-shadow duration-150 hover:shadow-md"
          >
            <option value="">All Models</option>
            <option
              v-for="model in availableModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
        <!-- <div>
          <label
            for="imageSourceFilter"
            class="block text-sm font-medium text-gray-600 mb-1"
            >Image Source:</label
          >
          <select
            v-model="imageSource"
            id="imageSourceFilter"
            class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 transition-shadow duration-150 hover:shadow-md"
          >
            <option value="organization">All Organization Images</option>
            <option value="user">User Images</option>
          </select>
        </div> -->
        <div class="flex space-x-3">
          <button
            @click="applyFilters"
            class="w-full px-4 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition-colors duration-150"
          >
            Apply Filters
          </button>
          <button
            @click="resetFilters"
            class="w-full px-4 py-3 bg-gray-300 text-gray-700 font-semibold rounded-lg shadow-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-opacity-50 transition-colors duration-150"
          >
            Reset Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="text-center py-12">
      <svg
        class="animate-spin h-10 w-10 text-indigo-600 mx-auto"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <p class="text-lg text-gray-600 mt-4">Loading images...</p>
    </div>

    <!-- Images Table -->
    <div v-else-if="images.length > 0" class="overflow-x-auto bg-white rounded-xl shadow-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Image
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Model ID
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created At
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Updated At
            </th>
            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="image in images" :key="image.id" class="hover:bg-gray-50 transition-colors duration-150">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-16 w-16">
                  <img 
                    class="h-16 w-16 object-cover rounded-md" 
                    :src="'data:image/png;base64,' + image.image_base64" 
                    :alt="'Generated Image ' + image.id"
                    @error="$event.target.src = '/placeholder-image.png'"
                  >
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-500 font-mono">{{ image.model_id || 'N/A' }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-500">{{ formatDate(image.created_at) }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-500">{{ formatDate(image.updated_at) }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex justify-end space-x-2">
               <!--<button 
                  @click="viewImage('data:image/png;base64,' + image.image_base64)" 
                  class="text-indigo-600 hover:text-indigo-900 mr-4"
                  title="View Image"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                --> 
                <button 
                  @click="confirmDeleteImage(image.id)" 
                  class="text-red-600 hover:text-red-900"
                  title="Delete Image"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No Images Found -->
    <div v-else class="text-center py-12 bg-white rounded-xl shadow-lg">
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          vector-effect="non-scaling-stroke"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
        />
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900">No Images Found</h3>
      <p class="mt-1 text-sm text-gray-500">
        No images match your current filters, or your organization has no images
        yet.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useToast } from "vue-toast-notification";
import { useImageService } from "@/services/api/image";
import { useEventService } from "@/services/api/event";
import { useAuthStore } from "@/stores/auth";
import "vue-toast-notification/dist/theme-sugar.css"; // Or your preferred theme
import { useOrganizationStore } from "@/stores/organization";

const $toast = useToast();
const imageService = useImageService();
const eventService = useEventService(); // Initialize event service
const authStore = useAuthStore();
console.log("authStore1", authStore.user.id);
const organizationStore = useOrganizationStore();
console.log("authStore2", organizationStore.organizations);

const images = ref([]);
const orgiD = ref(null);
const isLoading = ref(false);
const isLoadingFilters = ref(false); // For loading dropdown data

const availableEvents = ref([]);
const availableModels = ref([]);
const selectedEventId = ref("");
const selectedModelId = ref("");
const imageSource = ref("organization"); // 'organization' or 'user'

const fetchImages = async (retryCount = 0) => {
  isLoading.value = true;
  images.value = [];

  try {
    if (!organizationStore.organizations?.length) {
      await organizationStore.fetch_organizations();
    }

    const org = organizationStore.organizations.find(
      (org) => org.owner && org.owner.id === authStore.user.id
    );

    if (!org) {
      if (retryCount < 3) {
        console.log("Organization not found, retrying...", retryCount + 1);
        setTimeout(() => fetchImages(retryCount + 1), 500);
        return;
      }
      throw new Error("No organization found after retries");
    }

    orgiD.value = org.id;
    console.log("Using organization ID:", orgiD.value);

    let response;
    if (imageSource.value === "user") {
      if (selectedEventId.value || selectedModelId.value) {
        $toast.info(
          'Event/Model filters do not apply to "My Uploaded Images"',
          {
            position: "top-right",
            duration: 5000,
          }
        );
      }
      response = await imageService.getUserImages();
    } else {
      // Use the regular organization images endpoint with filters
      const apiFilters = {
        org_id: orgiD.value,
        event_id: selectedEventId.value || undefined,
        model_id: selectedModelId.value || undefined,
      };
      response = await imageService.getOrganizationImages(apiFilters);
    }

    console.log(" images API Response:", response); // Log the full response

    images.value = response[0];

    console.log("Processed images:", images.value);
  } catch (error) {
    console.error("Failed to fetch images:", error);
    if (retryCount < 3) {
      setTimeout(() => fetchImages(retryCount + 1), 500);
    } else {
      $toast.error("Failed to load images. Please try again.", {
        position: "top-right",
      });
    }
  } finally {
    isLoading.value = false;
  }
};

const applyFilters = () => {
  fetchImages();
};

const resetFilters = () => {
  selectedEventId.value = "";
  selectedModelId.value = "";
  imageSource.value = "organization";
  fetchImages();
};

const confirmDeleteImage = (imageId) => {
  if (
    window.confirm(
      "Are you sure you want to delete this image? This action cannot be undone."
    )
  ) {
    deleteImage(imageId);
  }
};

const deleteImage = async (imageId) => {
  try {
    await imageService.deleteOrganizationImage(imageId);
    $toast.success("Image deleted successfully!", { position: "top-right" });
    images.value = images.value.filter((img) => img.id !== imageId);
    if (images.value.length === 0) {
      $toast.info("No images remaining.", { position: "top-right" });
    }
  } catch (error) {
    console.error(`Error deleting image ${imageId}:`, error);
    let errorMessage = "Failed to delete image. Please try again.";
    if (error.response && error.response.data && error.response.data.detail) {
      errorMessage =
        typeof error.response.data.detail === "string"
          ? error.response.data.detail
          : JSON.stringify(error.response.data.detail);
    } else if (error.response && error.response.statusText) {
      errorMessage = `Failed to delete image: ${error.response.statusText}`;
    }
    $toast.error(errorMessage, { position: "top-right" });
  }
};

// Replace the existing onMounted with this:
const fetchInitialData = async () => {
  try {
    if (!organizationStore.organizations?.length) {
      await organizationStore.fetch_organizations();
    }
    await Promise.all([fetchImages(), fetchFilterData()]);
  } catch (error) {
    console.error("Error initializing data:", error);
    $toast.error("Failed to load data. Please refresh.", {
      position: "top-right",
    });
  }
};

const fetchFilterData = async (retryCount = 0) => {
  isLoadingFilters.value = true;

  try {
    if (!organizationStore.organizations?.length) {
      await organizationStore.fetch_organizations();
    }

    const org = organizationStore.organizations.find(
      (org) => org.owner && org.owner.id === authStore.user.id
    );

    if (!org) {
      if (retryCount < 3) {
        console.log("Organization not found, retrying...", retryCount + 1);
        setTimeout(() => fetchFilterData(retryCount + 1), 500);
        return;
      }
      throw new Error("No organization found after retries");
    }

    orgiD.value = org.id;
    console.log("Using organization ID:", orgiD.value);

    const [events, models] = await Promise.all([
      eventService.getOrganizationEvents(orgiD.value),
      imageService.getOrganizationModels(orgiD.value),
    ]);

    availableEvents.value = Array.isArray(events) ? events : [];
    availableModels.value = Array.isArray(models) ? models : [];
  } catch (error) {
    console.error("Error fetching filter data:", error);
    if (retryCount >= 3) {
      $toast.error("Failed to load filters. Please refresh.", {
        position: "top-right",
      });
    } else {
      setTimeout(() => fetchFilterData(retryCount + 1), 500);
    }
  } finally {
    isLoadingFilters.value = false;
  }
};

// Format date to display only the date part
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

onMounted(() => {
  fetchInitialData();
  // Call your other functions that need the org ID
  fetchImages();
  fetchFilterData();
});

watch(imageSource, (newSource) => {
  // When image source changes, fetch images for the new source.
  // Event/model filters will be applied if applicable to the new source by fetchImages logic.
  fetchImages();
});
</script>

<style scoped>
/* Add any additional scoped styles if Tailwind isn't enough */
.group:hover .group-hover\:scale-110 {
  transform: scale(1.1);
}
</style>
