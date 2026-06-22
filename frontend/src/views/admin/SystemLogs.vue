<template>
  <div class="admin-page">
    <header class="page-header">
      <h1>System Logs</h1>
    </header>
    
    <main class="page-content">
      <div class="filters">
        <div class="filter-group">
          <label for="dateRange">Date Range:</label>
          <select v-model="filters.dateRange" id="dateRange" class="form-control" @change="fetchLogs">
            <option value="today">Today</option>
            <option value="week">Last 7 Days</option>
            <option value="month">Last 30 Days</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="level">Level:</label>
          <select v-model="filters.level" id="level" class="form-control" @change="fetchLogs">
            <option value="all">All</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="ERROR">Error</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="category">Category:</label>
          <select v-model="filters.category" id="category" class="form-control" @change="fetchLogs">
            <option value="all">All</option>
            <option value="AUTH">Authentication</option>
            <option value="USER">User Activity</option>
            <option value="ADMIN">Admin Activity</option>
            <option value="SYSTEM">System</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading">
        Loading...
      </div>

      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-else-if="!filteredLogs.length" class="no-logs-message">
        No logs found for the selected filters
      </div>

      <div v-else class="logs-table">
        <table class="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Level</th>
              <th>Category</th>
              <th>Action</th>
              <th>User</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in paginatedLogs" :key="log.id" class="log-row">
              <td>{{ formatDate(log.timestamp) }}</td>
              <td>
                <span class="level-badge">
                  {{ log.category }}
                </span>
              </td>
              <td>{{ log.category }}</td>
              <td>{{ log.action }}</td>
              <td>{{ log.user_id ? log.user_id : 'System' }}</td>
              <td>
                <div class="details-cell">
                  <span class="details-text">{{ log.details }}</span>
                  <button v-if="log.metadata" 
                          class="view-metadata-btn"
                          @click="showMetadata(log)">
                    View Metadata
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loading && !error && filteredLogs.length > 0" class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="btn btn-secondary"
        >
          Previous
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="btn btn-secondary"
        >
          Next
        </button>
      </div>
    </main>

    <!-- Metadata Modal -->
    <div v-if="selectedMetadata" class="modal">
      <div class="modal-content">
        <h3>Log Metadata</h3>
        <pre>{{ JSON.stringify(selectedMetadata, null, 2) }}</pre>
        <button @click="selectedMetadata = null" class="btn btn-secondary">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import axiosInstance from '@/plugins/axios'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'SystemLogs',
  data() {
    return {
      filters: {
        dateRange: 'week',
        level: 'all',
        category: 'all'
      },
      logs: [],
      loading: false,
      error: null,
      currentPage: 1,
      itemsPerPage: 10,
      selectedMetadata: null
    }
  },
  computed: {
    filteredLogs() {
      return this.logs;
    },
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredLogs.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.itemsPerPage);
    },
    dateRangeParams() {
      const now = new Date();
      const end = now.toISOString();
      let start;

      switch (this.filters.dateRange) {
        case 'today':
          start = new Date(now.setHours(0, 0, 0, 0)).toISOString();
          break;
        case 'week':
          start = new Date(now.setDate(now.getDate() - 7)).toISOString();
          break;
        case 'month':
          start = new Date(now.setDate(now.getDate() - 30)).toISOString();
          break;
        default:
          start = new Date(now.setDate(now.getDate() - 7)).toISOString();
      }

      return { start_date: start, end_date: end };
    }
  },
  methods: {
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    async fetchLogs() {
      this.loading = true;
      this.error = null;
      const authStore = useAuthStore();

      try {
        // Check if we have a PostgreSQL token
        // if (!authStore.access_token) {
        //   throw new Error('Not authenticated. Please log in.');
        // }

        const params = {
          ...this.dateRangeParams,
          level: this.filters.level !== 'all' ? this.filters.level : undefined,
          category: this.filters.category !== 'all' ? this.filters.category : undefined
        };

        const response = await axiosInstance.get('/api/v1/admin/system-logs', { params });
        this.logs = response.data.logs;
        this.currentPage = 1;
      } catch (error) {
        if (error.response?.status === 401) {
          this.error = 'Session expired. Please log in again.';
          // Redirect to login
          this.$router.push('/login');
        } else {
          this.error = error.message || 'Failed to fetch logs. Please try again later.';
        }
        console.error('Error fetching logs:', error);
      } finally {
        this.loading = false;
      }
    },
    showMetadata(log) {
      this.selectedMetadata = log.metadata;
    }
  },
  mounted() {
    this.fetchLogs();
  },
  watch: {
    currentPage() {
      // Scroll to top when page changes
      window.scrollTo(0, 0);
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-control {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table th,
.table td {
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.log-row {
  transition: background-color 0.2s;
}

.log-row:hover {
  background-color: #f8f9fa;
}

.level-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.level-badge.info {
  background-color: #17a2b8;
  color: white;
}

.level-badge.warning {
  background-color: #ffc107;
  color: #000;
}

.level-badge.error {
  background-color: #dc3545;
  color: white;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

.error-message {
  text-align: center;
  padding: 1rem;
  background-color: #fee;
  color: #dc3545;
  border-radius: 4px;
  margin: 1rem 0;
}

.no-logs-message {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1.1rem;
}

.details-cell {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.details-text {
  flex: 1;
}

.view-metadata-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  background-color: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.view-metadata-btn:hover {
  background-color: #138496;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 80%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content pre {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    gap: 10px;
  }

  .table {
    display: block;
    overflow-x: auto;
  }

  .modal-content {
    max-width: 95%;
    padding: 1rem;
  }
}
</style>
