<template>
  <div class="event-management p-6">
    <!-- Event Header -->
    <div class="mb-8">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-semibold">Event Management</h1>
          <p class="text-gray-500 text-sm mt-1">
            Total Events: {{ event_count }}
          </p>
        </div>
        <button
          @click="show_create_modal = true"
          class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark"
          v-if="canCreateEvent"
        >
          Create New Event
        </button>
      </div>

      <!-- Event Filters -->
      <div class="flex gap-4 mb-6">
        <div class="flex-1">
          <input
            v-model="search_query"
            type="text"
            placeholder="Search events..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>
        <select
          v-model="status_filter"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
    </div>
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div
        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"
      ></div>
    </div>
    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6"
    >
      <div class="flex">
        <div class="flex-shrink-0">
          <svg
            class="h-5 w-5 text-red-500"
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
          <p class="text-sm">{{ error }}</p>
        </div>
        <div class="ml-auto pl-3">
          <button
            @click="fetch_events"
            class="text-sm font-medium text-red-700 hover:text-red-900"
          >
            Retry
          </button>
        </div>
      </div>
    </div>
    <!-- Events Table -->
    <div v-else class="bg-white rounded-xl shadow-sm overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Event Name
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Date
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Start Time
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              End Time
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Status
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Visibility
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Attendees
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Photos
            </th>
            <th
              class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <!-- Empty state message when no events are found -->
          <tr v-if="filtered_events.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-500">
              <div class="flex flex-col items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-12 w-12 text-gray-400 mb-3"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <p class="text-lg font-medium">No events found</p>
                <p class="text-sm mt-1">
                  Create your first event to get started
                </p>
              </div>
            </td>
          </tr>
          <!-- Event rows -->
          <tr v-for="event in filtered_events" :key="event.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ event.name }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ event.location }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ event.date }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ event.start_time }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ event.end_time }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="get_status_class(event.status)"
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ event.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="
                  event.is_public === 'Public'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                "
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ event.is_public }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ event.attendees || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ event.photos_count || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-center">
              <div class="flex justify-center space-x-4">
                <button
                  @click="edit_event(event)"
                  class="text-blue-600 hover:text-blue-800 focus:outline-none"
                  title="Edit"
                  v-if="canUpdateEvent"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>
                <button
                  @click="view_gallery(event)"
                  class="text-blue-600 hover:text-blue-800 focus:outline-none"
                  title="Gallery"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </button>
                <!-- <button
                  @click="manage_staff(event)"
                  class="text-blue-600 hover:text-blue-800 focus:outline-none"
                  title="Add Staff"
                  v-if="canManageStaff"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                    />
                  </svg>
                </button> -->
                <button
                  @click="delete_event(event)"
                  class="text-red-600 hover:text-red-800 focus:outline-none"
                  title="Delete"
                  v-if="canDeleteEvent"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Event Modal -->
    <div
      v-if="show_create_modal"
      class="fixed inset-0 flex items-center justify-center z-50 px-4 sm:px-0"
      @click="close_modal"
    >
      <div class="absolute inset-0 bg-black opacity-30"></div>
      <div
        class="bg-white rounded-xl p-4 sm:p-6 w-full max-w-lg mx-auto shadow-xl relative max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <h2 class="text-xl font-semibold mb-4">
          {{ editing_event ? "Edit Event" : "Create New Event" }}
        </h2>

        <form @submit.prevent="save_event" id="event-form" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Event Name
            </label>
            <input
              v-model="event_form.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <input
              v-model="event_form.location"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <input
                v-model="event_form.date"
                type="date"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Start Time
              </label>
              <input
                v-model="event_form.time"
                type="time"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                End Time
              </label>
              <input
                v-model="event_form.end_time"
                type="time"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
          </div>

          <!-- Event Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Event Type
            </label>
            <select
              v-model="event_form.event_type"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value="">Select Event Type</option>
              <option value="conference">Conference</option>
              <option value="workshop">Workshop</option>
              <option value="seminar">Seminar</option>
              <option value="meetup">Meetup</option>
              <option value="exhibition">Exhibition</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Expected Attendees -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Expected Attendees
            </label>
            <input
              v-model.number="event_form.attendees"
              type="number"
              min="0"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="Enter expected number of attendees"
              required
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              v-model="event_form.description"
              rows="4"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="Provide a detailed description of the event..."
            ></textarea>
          </div>

          <!-- Event Settings - Responsive Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
            <!-- Active Status -->
            <div class="flex items-center">
              <input
                type="checkbox"
                id="active_status"
                v-model="event_form.is_active"
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <label
                for="active_status"
                class="ml-2 block text-sm text-gray-700"
              >
                Active Event
              </label>
              <span class="ml-2 text-xs text-gray-500">(Visible to users)</span>
            </div>

            <!-- Public/Private Setting -->
            <div class="flex items-center">
              <input
                type="checkbox"
                id="is_public"
                v-model="event_form.is_public"
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <label for="is_public" class="ml-2 block text-sm text-gray-700">
                Public Event
              </label>
              <span class="ml-2 text-xs text-gray-500"
                >(Visible to everyone)</span
              >
            </div>
          </div>
        </form>
        <!-- Modal Error Message -->
        <div
          v-if="modal_error"
          class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
        >
          <p class="text-sm">{{ modal_error }}</p>
        </div>
        <div class="flex flex-col sm:flex-row justify-end gap-3 mt-6">
          <button
            type="button"
            @click="close_modal"
            class="w-full sm:w-auto px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 order-2 sm:order-1"
            :disabled="form_loading"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="event-form"
            class="w-full sm:w-auto px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark flex items-center justify-center order-1 sm:order-2"
            :disabled="form_loading"
          >
            <span
              v-if="form_loading"
              class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
            ></span>
            {{ editing_event ? "Save Changes" : "Create Event" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useOrganizationStore } from "@/stores/organization";
import { usePermissionsStore } from "@/stores/permissions";
import { useAuthStore } from "@/stores/auth";
import { useEventService } from "@/services/api/event";
import { onMounted, computed } from "vue";

export default {
  name: "EventManagement",
  setup() {
    const permissionsStore = usePermissionsStore();
    const authStore = useAuthStore();

    // Permission-based computed properties
    const canCreateEvent = computed(() => permissionsStore.canCreateEvent);
    const canUpdateEvent = computed(() => permissionsStore.canUpdateEvent);
    const canDeleteEvent = computed(() => permissionsStore.canDeleteEvent);

    // Allow organization admins to manage staff regardless of specific permission
    const canManageStaff = computed(() => {
      return (
        authStore.is_organization_admin ||
        permissionsStore.hasPermission("staff:manage")
      );
    });

    return {
      canCreateEvent,
      canUpdateEvent,
      canDeleteEvent,
      canManageStaff,
    };
  },
  data() {
    return {
      search_query: "",
      status_filter: "",
      show_create_modal: false,
      editing_event: null,
      event_form: {
        name: "",
        location: "",
        date: "",
        time: "",
        end_time: "",
        event_type: "",
        description: "",
        is_active: true,
        is_public: false,
        attendees: 0,
      },
      loading: false,
      form_loading: false,
      error: null,
      modal_error: null,
      event_count: 0,
    };
  },
  computed: {
    // Transform events for display
    processed_events() {
      const store = useOrganizationStore();
      return store.events.map((event) => {
        // Format start date and time
        let formattedDate = "";
        let startTime = "";
        let startDateTime = "";
        if (event.event_time) {
          const eventDate = new Date(event.event_time);
          formattedDate = eventDate.toLocaleDateString();
          startTime = eventDate.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          });
          startDateTime = `${formattedDate} ${startTime}`;
        }

        // Format end date and time
        let endDateTime = "";
        let endTime = "";
        if (event.event_end_timed) {
          const endDate = new Date(event.event_end_timed);
          const endFormattedDate = endDate.toLocaleDateString();
          endTime = endDate.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          });
          endDateTime = `${endFormattedDate} ${endTime}`;
        }

        // Return all available fields
        return {
          ...event,
          date: formattedDate,
          start_time: startTime,
          end_time: endTime,
          start_datetime: startDateTime,
          end_datetime: endDateTime,
          status: event.active ? "active" : "inactive",
          is_public: event.public ? "Public" : "Private",
          attendees_count: 0, // Default value
          photos_count: 0, // Default value
        };
      });
    },
    filtered_events() {
      let events = this.processed_events;

      if (this.search_query) {
        events = events.filter(
          (event) =>
            event.name
              .toLowerCase()
              .includes(this.search_query.toLowerCase()) ||
            event.location
              .toLowerCase()
              .includes(this.search_query.toLowerCase())
        );
      }

      if (this.status_filter) {
        events = events.filter((event) => event.status === this.status_filter);
      }

      return events;
    },
  },
  methods: {
    get_status_class(status) {
      // Simple mapping for active/inactive status
      if (status === "active") {
        return "bg-green-100 text-green-800";
      } else {
        return "bg-gray-100 text-gray-800";
      }
    },
    close_modal() {
      this.show_create_modal = false;
      this.reset_form();
    },
    edit_event(event) {
      // Check if user has permission to update events
      const permissionsStore = usePermissionsStore();
      if (!permissionsStore.canUpdateEvent) {
        this.error = "You don't have permission to edit events";
        return;
      }

      this.editing_event = event;
      this.event_form = { ...event };
      this.show_create_modal = true;
    },
    async save_event() {
      const store = useOrganizationStore();
      const permissionsStore = usePermissionsStore();
      const eventService = useEventService();
      const authStore = useAuthStore();
      // Create a copy of the form data to modify
      const event_data = { ...this.event_form };

      // Combine date and time into proper datetime strings
      if (event_data.date && event_data.time) {
        // Format: YYYY-MM-DDThh:mm:00
        event_data.event_time = `${event_data.date}T${event_data.time}:00`;
        delete event_data.time;
      }

      if (event_data.date && event_data.end_time) {
        // Format: YYYY-MM-DDThh:mm:00
        event_data.event_end_timed = `${event_data.date}T${event_data.end_time}:00`;
        delete event_data.end_time;
      }

      // Remove the date field as it's now incorporated into the datetime fields
      delete event_data.date;

      // Check permissions before saving
      if (this.editing_event && !permissionsStore.canUpdateEvent) {
        this.modal_error = "You don't have permission to update events";
        return;
      }

      if (!this.editing_event && !permissionsStore.canCreateEvent) {
        this.modal_error = "You don't have permission to create events";
        return;
      }

      try {
        this.form_loading = true;
        this.modal_error = null;

        const orgId = store.organization?.id;
        if (!orgId) {
          throw new Error("No organization selected");
        }

        // Add organization_id to event data
        event_data.organization_id = orgId;

        if (this.editing_event) {
          await eventService.updateEvent(this.editing_event.id, event_data);
        } else {
          await eventService.createEvent(event_data);
        }

        // Refresh events list
        await this.fetch_events();

        this.show_create_modal = false;
        this.reset_form();
      } catch (err) {
        this.modal_error =
          "Failed to save event. Please check your inputs and try again.";
        console.error("Error saving event:", err);
      } finally {
        this.form_loading = false;
      }
    },
    reset_form() {
      this.event_form = {
        name: "",
        location: "",
        date: "",
        time: "",
        end_time: "",
        event_type: "",
        description: "",
        is_active: true,
        is_public: false,
        attendees: 0,
      };
      this.editing_event = null;
      this.modal_error = null;
    },
    view_gallery(event) {
      //const store = useOrganizationStore();
      //store.set_current_event(event_id);
      this.$router.push({
        name: "organization-image-gallery",
      });
    },
    manage_staff(event) {
      // Check if user has permission to manage staff
      const permissionsStore = usePermissionsStore();
      const authStore = useAuthStore();

      // Allow organization admins to manage staff
      if (
        !authStore.is_organization_admin &&
        !permissionsStore.hasPermission("staff:manage")
      ) {
        this.error = "You don't have permission to manage staff";
        return;
      }

      const store = useOrganizationStore();
      store.set_current_event(event.id);
      this.$router.push(`/organization/events/${event.id}/staff`);
    },
    async fetch_events() {
      try {
        this.loading = true;
        this.error = null;
        const store = useOrganizationStore();
        const authStore = useAuthStore();
        const eventService = useEventService();

        // First check if we already have an organization in the store
        if (store.organization?.id) {
          console.log("Using organization from store:", store.organization.id);
          const events = await eventService.getEventsByOrganization(
            store.organization.id
          );
          store.events = events;
          this.fetch_event_count();
          return;
        }

        // If not, fetch organizations from API
        console.log("No organization in store, fetching organizations");
        await store.fetch_organizations();

        // Now we should have an organization
        if (store.organization?.id) {
          console.log("Using organization after fetch:", store.organization.id);
          const events = await eventService.getEventsByOrganization(
            store.organization.id
          );
          store.events = events;
          this.fetch_event_count();
          return;
        }

        // If we still don't have an organization, show error
        this.error =
          "No organizations found. Please create an organization first.";
        this.loading = false;
      } catch (err) {
        this.error = "Failed to load events. Please try again.";
        console.error("Error loading events:", err);
      } finally {
        this.loading = false;
      }
    },
    async fetch_event_count() {
      try {
        const store = useOrganizationStore();

        // Simply use the length of the events array
        this.event_count = store.events.length;
      } catch (err) {
        console.error("Error setting event count:", err);
        this.event_count = 0;
      }
    },
    async delete_event(event) {
      // Check if user has permission to delete events
      const permissionsStore = usePermissionsStore();
      if (!permissionsStore.canDeleteEvent) {
        this.error = "You don't have permission to delete events";
        return;
      }

      if (!confirm(`Are you sure you want to delete "${event.name}"?`)) {
        return;
      }

      try {
        this.loading = true;
        const eventService = useEventService();
        await eventService.deleteEvent(event.id);

        // Refresh events and count
        await this.fetch_events();
      } catch (err) {
        this.error = "Failed to delete event. Please try again.";
        console.error("Error deleting event:", err);
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    const permissionsStore = usePermissionsStore();
    const organizationStore = useOrganizationStore();

    console.log("EventManagement mounted, initializing...");

    // Initialize everything in sequence
    const initialize = async () => {
      try {
        // First, fetch organizations if needed
        if (!organizationStore.organization) {
          console.log("No organization in store, fetching organizations");
          await organizationStore.fetch_organizations();
        }

        // Then fetch permissions
        await permissionsStore.fetchUserPermissions();

        // Finally fetch events
        await this.fetch_events();
      } catch (err) {
        console.error("Error during initialization:", err);
        this.error = "Failed to initialize. Please refresh the page.";
      }
    };

    // Start initialization
    initialize();
  },
};
</script>
