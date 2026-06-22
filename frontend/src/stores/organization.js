import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useAuthStore } from "./auth";
import { useOrganizationSettingsService } from "@/services/api/organizationSettings";
import { useOrganizationService } from "@/services/api/organization";

export const useOrganizationStore = defineStore("organization", () => {
  // State
  const organization = ref(null);
  const organizations = ref([]);
  const events = ref([]);
  const current_event = ref(null);
  const event_photos = ref([]);
  const staff = ref([]);
  const settings = ref({
    profile: {
      name: "",
      contact_email: "",
      phone_number: "",
      description: "",
      avatar_url: "",
    },
    event_settings: {
      default_type: "public",
      default_duration: 2,
      require_approval: false,
      auto_gallery: true,
      allow_downloads: true,
    },
    branding: {
      primary_color: "#000000",
      secondary_color: "#ffffff",
      logo_url: null,
      watermark_url: null,
    },
  });
  const loading = ref(false);
  const error = ref(null);
  const eventId = ref(null);
  const fullscreenMode = ref(false);

  // Getters
  const active_events = computed(() => {
    return events.value.filter(
      (event) => event.status === "active" || event.status === "live"
    );
  });

  const total_photos = computed(() => {
    return events.value.reduce(
      (total, event) => total + (event.photos_count || 0),
      0
    );
  });

  const total_attendees = computed(() => {
    return events.value.reduce(
      (total, event) => total + (event.attendees_count || 0),
      0
    );
  });

  const event_stats = computed(() => {
    if (!current_event.value) return null;
    return {
      total_photos: current_event.value.photos_count || 0,
      total_attendees: current_event.value.attendees_count || 0,
      total_likes: event_photos.value.reduce(
        (total, photo) => total + (photo.likes || 0),
        0
      ),
    };
  });

  const active_staff = computed(() => {
    return staff.value.filter((member) => member.status === "active");
  });

  // Organizations Actions
  const fetch_organizations = async () => {
    loading.value = true;
    try {
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      console.log("Fetching organizations for user");

      // Use getOwnedOrganizations instead of getOrganizations for organization accounts
      const response = await organizationService.getOwnedOrganizations();
      organizations.value = response;
      console.log("Organizations fetched:", organizations.value);

      // If we have organizations and no current organization selected,
      // set the first one as the current organization
      if (organizations.value.length > 0 && !organization.value) {
        organization.value = organizations.value[0];
        console.log(
          "Setting first organization as current:",
          organization.value
        );
      }

      return organizations.value;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching organizations:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetch_organization = async (id) => {
    loading.value = true;
    try {
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const response = await organizationService.getOrganization(id);
      organization.value = response;
      return organization.value;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching organization:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Events Actions
  const fetch_events = async () => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      const response = await organizationService.getEvents(org_id);
      events.value = response;
      return events.value;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching events:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetch_event = async (event_id) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      // First check if we already have this event in our state
      const existingEvent = events.value.find((e) => e.id === event_id);
      if (existingEvent) {
        current_event.value = existingEvent;
        return existingEvent;
      }

      // If not, fetch it from the API
      const response = await organizationService.getEvent(org_id, event_id);
      current_event.value = response;
      return current_event.value;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching event:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const create_event = async (event_data) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      const response = await organizationService.createEvent(
        org_id,
        event_data
      );
      events.value.push(response);
      return response;
    } catch (err) {
      error.value = err.message;
      console.error("Error creating event:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const update_event = async (event_id, event_data) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      const response = await organizationService.updateEvent(
        org_id,
        event_id,
        event_data
      );

      // Update local state
      const index = events.value.findIndex((e) => e.id === event_id);
      if (index !== -1) {
        const updated_event = { ...events.value[index], ...event_data };
        events.value[index] = updated_event;
        if (current_event.value?.id === event_id) {
          current_event.value = updated_event;
        }
        return updated_event;
      }
      throw new Error("Event not found");
    } catch (err) {
      error.value = err.message;
      console.error("Error updating event:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const set_current_event = async (event_id) => {
    const event = events.value.find((e) => e.id === event_id);
    if (event) {
      current_event.value = event;
      await fetch_event_photos(event_id);
    } else {
      current_event.value = null;
      event_photos.value = [];
    }
  };

  const fetch_event_photos = async (event_id) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      const response = await organizationService.getEventPhotos(
        org_id,
        event_id
      );
      event_photos.value = response;
      return event_photos.value;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching event photos:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const upload_event_photo = async (event_id, photo_data) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      const response = await organizationService.uploadEventPhoto(
        org_id,
        event_id,
        photo_data
      );
      event_photos.value.push(response);
      return response;
    } catch (err) {
      error.value = err.message;
      console.error("Error uploading event photo:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const toggle_photo_like = async (photo_id) => {
    try {
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id || !current_event.value?.id) {
        throw new Error("No organization or event selected");
      }

      const response = await organizationService.togglePhotoLike(
        org_id,
        current_event.value.id,
        photo_id
      );

      // Update local state
      const index = event_photos.value.findIndex((p) => p.id === photo_id);
      if (index !== -1) {
        event_photos.value[index].is_liked = response.is_liked;
        event_photos.value[index].likes = response.likes;
      }
    } catch (err) {
      error.value = err.message;
      console.error("Error toggling photo like:", err);
      throw err;
    }
  };

  // Staff Actions
  const fetch_staff = async (org_id = null) => {
    loading.value = true;
    try {
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();

      // If no org_id is provided, try to get it from auth store
      if (!org_id) {
        if (auth_store.organization?.id) {
          // Use the organization from auth store
          org_id = auth_store.organization.id;
          console.log("Using organization ID from auth store:", org_id);
        } else {
          console.warn("No organization selected, returning empty staff list");
          staff.value = [];
          return staff.value;
        }
      }

      console.log("Fetching staff members for organization:", org_id);
      const response = await organizationService.getMembers(org_id);
      staff.value = response;
      return staff.value;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching staff:", err);
      // Return empty array instead of throwing to prevent component errors
      staff.value = [];
      return staff.value;
    } finally {
      loading.value = false;
    }
  };

  const invite_staff = async (invite_data) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      await organizationService.inviteStaffMember(org_id, invite_data);
      // Refresh staff list after successful invite
      await fetch_staff();
    } catch (err) {
      error.value = err.message;
      console.error("Error inviting staff:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const update_staff = async (staff_id, staff_data) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      await organizationService.updateMemberRole(
        org_id,
        staff_id,
        staff_data.role
      );

      // Update local state
      const index = staff.value.findIndex((s) => s.id === staff_id);
      if (index !== -1) {
        staff.value[index] = { ...staff.value[index], ...staff_data };
      }
    } catch (err) {
      error.value = err.message;
      console.error("Error updating staff:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const update_staff_status = async (staff_id, status) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      await organizationService.updateMemberStatus(org_id, staff_id, status);

      // Update local state
      const index = staff.value.findIndex((s) => s.id === staff_id);
      if (index !== -1) {
        staff.value[index].status = status;
      }
    } catch (err) {
      error.value = err.message;
      console.error("Error updating staff status:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const remove_staff = async (staff_id) => {
    try {
      loading.value = true;
      const auth_store = useAuthStore();
      const organizationService = useOrganizationService();
      const org_id = auth_store.organization?.id;

      if (!org_id) {
        throw new Error("No organization selected");
      }

      await organizationService.removeMember(org_id, staff_id);

      // Update local state
      staff.value = staff.value.filter((s) => s.id !== staff_id);
    } catch (err) {
      error.value = err.message;
      console.error("Error removing staff:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Settings Actions
  const fetch_settings = async () => {
    const authStore = useAuthStore();
    const orgId = authStore.organization?.id;
    if (!orgId) return;
    const service = useOrganizationSettingsService();
    const data = await service.getSettings(orgId);
    settings.value.profile = {
      name: data.name || "",
      description: data.description || "",
      contact_email: data.contact_email || "",
      phone_number: data.phone_number || "",
      avatar_url: data.avatar_url || "",
    };
  };

  const update_settings = async (payload) => {
    const authStore = useAuthStore();
    const orgId = authStore.organization?.id;
    if (!orgId) return;
    const service = useOrganizationSettingsService();
    const data = await service.updateSettings(orgId, payload.profile);
    settings.value.profile = {
      name: data.name || "",
      description: data.description || "",
      contact_email: data.contact_email || "",
      phone_number: data.phone_number || "",
      avatar_url: data.avatar_url || "",
    };
  };

  const upload_avatar = async (file) => {
    const authStore = useAuthStore();
    const orgId = authStore.organization?.id;
    if (!orgId) return;
    const service = useOrganizationSettingsService();
    const data = await service.uploadAvatar(orgId, file);
    settings.value.profile.avatar_url = data.avatar_url;
  };

  const setEventId = (id) => {
    eventId.value = id;
  };

  const setFullscreenMode = (val) => {
    fullscreenMode.value = val;
  };

  return {
    // State
    organization,
    organizations,
    events,
    current_event,
    event_photos,
    staff,
    settings,
    loading,
    error,
    eventId,
    fullscreenMode,

    // Getters
    active_events,
    total_photos,
    total_attendees,
    event_stats,
    active_staff,

    // Actions
    fetch_organizations,
    fetch_organization,
    fetch_events,
    fetch_event,
    create_event,
    update_event,
    set_current_event,
    fetch_event_photos,
    upload_event_photo,
    toggle_photo_like,
    fetch_staff,
    invite_staff,
    update_staff,
    update_staff_status,
    remove_staff,
    fetch_settings,
    update_settings,
    upload_avatar,
    setEventId,
    setFullscreenMode,
  };
});
