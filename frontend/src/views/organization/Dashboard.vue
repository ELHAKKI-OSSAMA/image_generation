<template>
  <div class="organization-dashboard">
    <!-- Organization Header -->
    <div class="bg-primary p-6 text-white">
      <h1 class="text-2xl font-semibold mb-2">
        {{ organization?.name || "Organization Name" }}
      </h1>
      <p class="text-sm opacity-80">{{ organization_plan }} Plan</p>
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
      class="p-6 bg-red-50 border border-red-200 m-6 rounded-lg"
    >
      <p class="text-red-700">{{ error }}</p>
      <button @click="initialize" class="mt-2 text-sm text-red-700 underline">
        Retry
      </button>
    </div>

    <div v-else>
      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 p-6">
        <div
          v-for="stat in quick_stats"
          :key="stat.label"
          class="bg-white rounded-xl p-6 shadow-sm"
        >
          <h3 class="text-gray-500 text-sm mb-2">{{ stat.label }}</h3>
          <p class="text-2xl font-semibold">{{ stat.value }}</p>
          <p class="text-sm text-gray-600">{{ stat.change }}</p>
        </div>
      </div>

      <!-- Active Events -->
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold">Active Events</h2>
          <button
            @click="create_new_event"
            class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark"
            v-if="canCreateEvent"
          >
            Create New Event
          </button>
        </div>

        <!-- No Events Message -->
        <div
          v-if="processed_active_events.length === 0"
          class="bg-gray-50 p-8 rounded-xl text-center"
        >
          <p class="text-gray-500">No active events found</p>
          <button
            v-if="canCreateEvent"
            @click="create_new_event"
            class="mt-4 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark"
          >
            Create Your First Event
          </button>
        </div>

        <!-- Event Cards -->
        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <div
            v-for="event in processed_active_events"
            :key="event.id"
            class="bg-white rounded-xl p-6 shadow-sm"
          >
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-lg font-semibold">{{ event.name }}</h3>
              <span
                :class="event.status_class"
                class="px-2 py-1 rounded-full text-sm"
              >
                {{ event.status_label }}
              </span>
            </div>
            <p class="text-gray-600 text-sm mb-4">
              {{ event.description || "No description available" }}
            </p>
            <div
              class="flex justify-between items-center text-sm text-gray-500"
            >
              <span>{{ event.date_display }}</span>
              <span>{{ event.attendees_count || 0 }} Attendees</span>
            </div>
            <div class="mt-4 flex gap-2">
              <button
                @click="manage_event(event.id)"
                class="flex-1 bg-gray-100 px-3 py-2 rounded-lg hover:bg-gray-200"
              >
                Manage
              </button>
              <button
                @click="view_gallery(event.id)"
                class="flex-1 bg-gray-100 px-3 py-2 rounded-lg hover:bg-gray-200"
              >
                Gallery
              </button>
            </div>
          </div>
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
import { useOrganizationService } from "@/services/api/organization";
import { computed } from "vue";

export default {
  name: "OrganizationDashboard",
  data() {
    return {
      organization: null,
      organization_plan: "Professional",
      loading: true,
      error: null,
      event_count: 0,
      photo_count: 0,
      user_count: 0,
      events: [],
      members: [],
      members_count: 0,
    };
  },
  computed: {
    canCreateEvent() {
      const permissionsStore = usePermissionsStore();
      return permissionsStore.canCreateEvent;
    },
    quick_stats() {
      return [
        {
          label: "Active Events",
          value: this.event_count,
        },
        {
          label: "Total Photos",
          value: this.formatNumber(this.photo_count),
          change: "+500 this month",
        },
        {
          label: "Organization Members",
          value: this.members_count,
          change: "Total members",
        },
      ];
    },
    processed_active_events() {
      return this.events
        .filter((event) => event.active)
        .map((event) => {
          // Format start date and time
          let dateDisplay = "";
          if (event.event_time) {
            const startDate = new Date(event.event_time);
            const startFormatted = startDate.toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            });

            // If there's an end date and it's different from start date
            if (event.event_end_timed) {
              const endDate = new Date(event.event_end_timed);
              const endFormatted = endDate.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              });

              if (startFormatted !== endFormatted) {
                dateDisplay = `${startFormatted} - ${endFormatted}`;
              } else {
                dateDisplay = startFormatted;
              }
            } else {
              dateDisplay = startFormatted;
            }
          }

          // Determine status and class based on the event's active boolean field
          let status_label = event.active ? "Active" : "Inactive";
          let status_class = event.active
            ? "bg-green-100 text-green-800"
            : "bg-gray-100 text-gray-800";

          return {
            ...event,
            date_display: dateDisplay,
            status_label,
            status_class,
          };
        });
    },
  },
  methods: {
    formatNumber(num) {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + "k";
      }
      return num.toString();
    },
    async initialize() {
      this.loading = true;
      this.error = null;

      try {
        const store = useOrganizationStore();
        const authStore = useAuthStore();
        const eventService = useEventService();
        const organizationService = useOrganizationService();

        // Fetch organization if needed
        if (!store.organization) {
          await store.fetch_organizations();
        }

        this.organization = store.organization;

        if (!this.organization) {
          this.error =
            "No organization found. Please create an organization first.";
          this.loading = false;
          return;
        }

        // Fetch events
        const events = await eventService.getEventsByOrganization(
          this.organization.id
        );
        this.events = events;

        // Get event count
        const eventCountResponse = await eventService.getEventCount(
          this.organization.id
        );
        this.event_count =
          eventCountResponse.event_count ||
          events.filter((e) => e.active).length;

        // Set photo count from events
        this.photo_count = events.reduce(
          (total, event) => total + (event.photos_count || 0),
          0
        );

        // Fetch organization members
        try {
          // Use the organization service initialized above
          const members = await organizationService.getMembers(
            this.organization.id
          );
          this.members = Array.isArray(members) ? members : [];

          // Filter to only include users with role 'member' (exclude admins/owners)
          const memberRoleOnly = this.members.filter(
            (member) => member.role === "member"
          );
          this.members_count = memberRoleOnly.length;

          console.log("Fetched organization members:", this.members);
          console.log("Members with role=member only:", memberRoleOnly);
        } catch (memberErr) {
          console.error("Error fetching organization members:", memberErr);
          this.members_count = 0;
        }
      } catch (err) {
        console.error("Error initializing dashboard:", err);
        this.error = "Failed to load dashboard data. Please try again.";
      } finally {
        this.loading = false;
      }
    },
    create_new_event() {
      this.$router.push("/organization/events?create=true");
    },
    manage_event(event_id) {
      const store = useOrganizationStore();
      store.set_current_event(event_id);
      // Redirect to the same place as create_new_event
      this.$router.push("/organization/events?create=true");
    },
    view_gallery(event_id) {
      const store = useOrganizationStore();
      store.set_current_event(event_id);
      this.$router.push({
        name: "organization-image-gallery",
        params: { id: event_id }, // Make sure your route expects this param
      });
    },
  },
  mounted() {
    this.initialize();
  },
};
</script>
