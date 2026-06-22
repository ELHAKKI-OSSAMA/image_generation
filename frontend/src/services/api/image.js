import { useApi } from "@/composables/useApi";
import { useAuthStore } from "@/stores/auth";
import { useOrganizationStore } from "@/stores/organization";

export const useImageService = () => {
  const api = useApi();
  
  // Fetches a list of images for the organization, optionally filtered by event or model
  const getOrganizationImages = async (filters = {}) => {
    const authStore = useAuthStore();
    console.log("authStore1", authStore.user.id);
    const organizationStore = useOrganizationStore();
    console.log("organizationStore", organizationStore.organizations);
    const org = organizationStore.organizations.find(
      (org) => org.owner && org.owner.id === authStore.user.id
    );
    console.log("organization data ", org)
    const organization_id = org.id;
    if (!organization_id) {
      console.warn("No organization ID found in auth store");
      throw new Error("No organization access - organization ID not found");
    }

    try {
      // Base URL for organization images
      let url = "/api/v1/image/organization/me";

      // If we have both event and model IDs, use the specific endpoint
      if (filters.event_id && filters.model_id) {
        url = `/api/v1/image/organization/me/model/${filters.model_id}/event/${filters.event_id}`;
      }
      // If we have an event ID, use the event-specific endpoint
      else if (filters.event_id) {
        url = `/api/v1/image/organization/me/event/${filters.event_id}`;
      }
      // If we have a model ID, use the model-specific endpoint
      else if (filters.model_id) {
        url = `/api/v1/image/organization/me/model/${filters.model_id}`;
      }

      console.log(`Fetching organization images from: ${url}`);

      // Always include org_id in the request
      const response = await api.get(url);

      console.log("Successfully fetched organization images:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error details:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config,
      });
      console.error("Error fetching organization images:", error);
      throw error;
    }
  };

  const deleteOrganizationImage = async (imageId) => {
    try {
      const response = await api.delete(
        `/api/v1/image/organization/${imageId}`,
        {
          params: {
            org_id: organization_id,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Error deleting image ${imageId}:`, error);
      throw error;
    }
  };

  // Fetches a list of models available to the organization
  const getOrganizationModels = async () => {
    const authStore = useAuthStore();
    console.log("authStore1", authStore.user.id);
    const organizationStore = useOrganizationStore();
    console.log("organizationStore", organizationStore.organizations);
    const org = organizationStore.organizations.find(
      (org) => org.owner && org.owner.id === authStore.user.id
    );
    console.log("organization data ", org)
    const organization_id = org.id;
    if (!organization_id) {
      console.warn("No organization ID found in auth store");
      throw new Error("No organization access - organization ID not found");
    }

    try {
      console.log("Fetching organization models...");
      console.log("Organization ID from store:", authStore.organization_id);

      // Use the models endpoint that filters by the current organization
      const response = await api.get("/api/v1/models/list");

      console.log("Successfully fetched organization models:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error details:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config,
      });
      console.error("Error fetching organization models:", error);
      throw error;
    }
  };

  // Fetches images for the currently authenticated user
  const getUserImages = async () => {
    try {
      const response = await api.get(`/api/v1/image/user/me`);
      return response.data;
    } catch (error) {
      console.error("Error fetching user images:", error);
      throw error;
    }
  };

  // Fetches images for a specific user by ID
  const getImagesByUserId = async (userId) => {
    try {
      const response = await api.get(`/api/v1/image/user/id/${userId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching images for user ${userId}:`, error);
      throw error;
    }
  };

  // Fetches a specific image by its ID
  const getImageById = async (id) => {
    try {
      const response = await api.get(`/api/v1/image/id/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching image ${id}:`, error);
      throw error;
    }
  };

  // Fetches data from the /api/v1/image/root endpoint
  const getRootImageData = async () => {
    try {
      const response = await api.get(`/api/v1/image/root`);
      return response.data;
    } catch (error) {
      console.error("Error fetching root image data:", error);
      throw error;
    }
  };

  // Deletes a specific image by its ID (general)
  const deleteImageById = async (id) => {
    try {
      const response = await api.delete(`/api/v1/image/id/${id}`);
      return response.data; // Or handle success/failure based on response status
    } catch (error) {
      console.error(`Error deleting image ${id}:`, error);
      throw error;
    }
  };

  return {
    getOrganizationImages,
    deleteOrganizationImage,
    getOrganizationModels,
    getUserImages,
    getImagesByUserId,
    getImageById,
    getRootImageData,
    deleteImageById,
  };
};
