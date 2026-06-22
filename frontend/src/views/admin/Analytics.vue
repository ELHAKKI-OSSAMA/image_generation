<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold">System Analytics</h2>
      
      <!-- Time Range Filter -->
      <div class="flex items-center space-x-4">
        <label class="text-sm text-gray-600">Time Range:</label>
        <select 
          v-model="timeRange" 
          class="rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          @change="fetchAnalytics"
        >
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="custom">Custom Range</option>
        </select>

        <!-- Custom Date Range (shown when custom is selected) -->
        <div v-if="timeRange === 'custom'" class="flex items-center space-x-2">
          <input 
            type="date" 
            v-model="customRange.start"
            class="rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            @change="fetchAnalytics"
          >
          <span>to</span>
          <input 
            type="date" 
            v-model="customRange.end"
            class="rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            @change="fetchAnalytics"
          >
        </div>
      </div>
    </div>
    
    <div v-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
      <p class="text-red-700">{{ error }}</p>
    </div>

    <div v-if="loading" class="text-gray-500">Loading analytics...</div>

    <!-- Stats Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Users Card -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Users</div>
        <div class="mt-2">
          <div class="text-3xl font-semibold">{{ stats.users.total }}</div>
          <div class="mt-2 text-sm">
            <span class="text-green-600">{{ stats.users.active }} active</span>
            <span class="text-yellow-600 ml-2">{{ stats.users.pending }} pending</span>
          </div>
        </div>
      </div>

      <!-- Organizations Card -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Organizations</div>
        <div class="mt-2">
          <div class="text-3xl font-semibold">{{ stats.organizations.total }}</div>
          <div class="mt-2 text-sm">
            <span class="text-green-600">{{ stats.organizations.active }} active</span>
            <span class="text-yellow-600 ml-2">{{ stats.organizations.pending }} pending</span>
          </div>
        </div>
      </div>

      <!-- GPU Usage Card (Placeholder) -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">GPU Usage</div>
        <div class="mt-2 text-gray-500">
          Feature coming soon
        </div>
      </div>

      <!-- Storage Card (Placeholder) -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Storage Used</div>
        <div class="mt-2 text-gray-500">
          Feature coming soon
        </div>
      </div>
    </div>

    <!-- Analytics Section -->
    <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- API Usage Stats -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">API Usage</h3>
        <div v-if="apiUsage.datasets[0].data.length === 0" class="text-gray-500">
          No API usage data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="apiUsage" :options="chartOptions" />
        </div>
      </div>

      <!-- User Activity -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">User Activity</h3>
        <div v-if="userActivity.datasets[0].data.length === 0" class="text-gray-500">
          No activity data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="userActivity" :options="chartOptions" />
        </div>
      </div>

      <!-- Organization Growth -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Organization Growth</h3>
        <div v-if="orgGrowth.datasets[0].data.length === 0" class="text-gray-500">
          No growth data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="orgGrowth" :options="chartOptions" />
        </div>
      </div>

      <!-- Performance Metrics -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Performance Metrics</h3>
        <div v-if="performanceMetrics.datasets[0].data.length === 0" class="text-gray-500">
          No performance data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="performanceMetrics" :options="chartOptions" />
        </div>
      </div>

      <!-- Image Generation Stats (New) -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Image Generation</h3>
        <div v-if="!imageGeneration.datasets?.[0]?.data?.length" class="text-gray-500">
          No image generation data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="imageGeneration" :options="chartOptions" />
        </div>
        <div v-if="imageGeneration.datasets?.[0]?.data?.length" class="mt-4 grid grid-cols-2 gap-4">
          <div class="text-sm">
            <div class="text-gray-500">Success Rate</div>
            <div class="font-semibold">{{ averageSuccessRate }}%</div>
          </div>
          <div class="text-sm">
            <div class="text-gray-500">Avg Processing Time</div>
            <div class="font-semibold">{{ averageProcessingTime }}s</div>
          </div>
        </div>
      </div>

      <!-- Event Analytics (New) -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Event Analytics</h3>
        <div v-if="!eventStats.datasets?.[0]?.data?.length" class="text-gray-500">
          No event data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="eventStats" :options="chartOptions" />
        </div>
        <div v-if="eventStats.datasets?.[0]?.data?.length" class="mt-4 grid grid-cols-2 gap-4">
          <div class="text-sm">
            <div class="text-gray-500">Completion Rate</div>
            <div class="font-semibold">{{ eventCompletionRate }}%</div>
          </div>
          <div class="text-sm">
            <div class="text-gray-500">Avg Participants</div>
            <div class="font-semibold">{{ averageParticipants }}</div>
          </div>
        </div>
      </div>

      <!-- Subscription Distribution (New) -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Subscription Tiers</h3>
        <div v-if="!subscriptionData.datasets?.[0]?.data?.length" class="text-gray-500">
          No subscription data available
        </div>
        <div v-else class="h-64">
          <DoughnutChart :data="subscriptionData" :options="pieChartOptions" />
        </div>
      </div>

      <!-- Resource Utilization (New) -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Resource Utilization</h3>
        <div v-if="!resourceUtilization.datasets?.[0]?.data?.length" class="text-gray-500">
          No resource utilization data available
        </div>
        <div v-else class="h-64">
          <LineChart :data="resourceUtilization" :options="chartOptions" />
        </div>
        <div v-if="resourceUtilization.datasets?.[0]?.data?.length" class="mt-4 grid grid-cols-2 gap-4">
          <div class="text-sm">
            <div class="text-gray-500">Storage Used</div>
            <div class="font-semibold">{{ currentStorageUsage }} GB</div>
          </div>
          <div class="text-sm">
            <div class="text-gray-500">API Calls</div>
            <div class="font-semibold">{{ currentApiCalls }}/hr</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/plugins/axios'
import { Line as LineChart, Doughnut as DoughnutChart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'Analytics',
  components: {
    LineChart,
    DoughnutChart
  },
  data() {
    return {
      timeRange: '24h',
      customRange: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end: new Date().toISOString().split('T')[0]
      },
      stats: {
        users: {
          total: 0,
          active: 0,
          pending: 0
        },
        organizations: {
          total: 0,
          active: 0,
          pending: 0
        }
      },
      apiUsage: {
        labels: [],
        datasets: [{
          label: 'API Calls',
          data: [],
          borderColor: '#3B82F6',
          tension: 0.1
        }]
      },
      userActivity: {
        labels: [],
        datasets: [{
          label: 'Active Users',
          data: [],
          borderColor: '#10B981',
          tension: 0.1
        }]
      },
      orgGrowth: {
        labels: [],
        datasets: [{
          label: 'Organizations',
          data: [],
          borderColor: '#8B5CF6',
          tension: 0.1
        }]
      },
      performanceMetrics: {
        labels: [],
        datasets: [{
          label: 'Response Time (ms)',
          data: [],
          borderColor: '#F59E0B',
          tension: 0.1
        }]
      },
      imageGeneration: {
        labels: [],
        datasets: [{
          label: 'Images Generated',
          data: [],
          borderColor: '#6366F1',
          tension: 0.1
        }]
      },
      eventStats: {
        labels: [],
        datasets: [{
          label: 'Events',
          data: [],
          borderColor: '#EC4899',
          tension: 0.1
        }]
      },
      subscriptionData: {
        labels: [],
        datasets: [{
          data: [],
          backgroundColor: [
            '#4F46E5',
            '#10B981',
            '#F59E0B',
            '#EC4899'
          ]
        }]
      },
      resourceUtilization: {
        labels: [],
        datasets: [
          {
            label: 'Storage (GB)',
            data: [],
            borderColor: '#8B5CF6',
            tension: 0.1,
            yAxisID: 'y'
          },
          {
            label: 'API Calls/hr',
            data: [],
            borderColor: '#F59E0B',
            tension: 0.1,
            yAxisID: 'y1'
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          }
        }
      },
      pieChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right'
          }
        }
      },
      error: null,
      loading: true,
      refreshInterval: null,
      dailyStats: {
        new_users: 0,
        api_calls: 0,
        avg_response_time: null
      },
      averageSuccessRate: 0,
      averageProcessingTime: 0,
      eventCompletionRate: 0,
      averageParticipants: 0,
      currentStorageUsage: 0,
      currentApiCalls: 0
    }
  },
  methods: {
    getTimeRangeParams() {
      if (this.timeRange === 'custom') {
        return {
          start: this.customRange.start,
          end: this.customRange.end
        }
      }

      const end = new Date()
      const start = new Date()

      switch (this.timeRange) {
        case '24h':
          start.setHours(start.getHours() - 24)
          break
        case '7d':
          start.setDate(start.getDate() - 7)
          break
        case '30d':
          start.setDate(start.getDate() - 30)
          break
      }

      return {
        start: start.toISOString().split('T')[0],
        end: end.toISOString().split('T')[0]
      }
    },

    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    },

    async fetchAnalytics() {
      try {
        this.loading = true
        const { start, end } = this.getTimeRangeParams()
        
        const userStatsResponse = await axios.get('/api/v1/admin/stats/users')
        this.stats.users = userStatsResponse.data
        
        const orgStatsResponse = await axios.get('/api/v1/admin/stats/organizations')
        this.stats.organizations = orgStatsResponse.data

        const trendsResponse = await axios.get('/api/v1/admin/stats/trends', {
          params: { start, end }
        })
        
        this.apiUsage.labels = trendsResponse.data.api_usage.map(d => this.formatDate(d.time))
        this.apiUsage.datasets[0].data = trendsResponse.data.api_usage.map(d => d.count)

        this.userActivity.labels = trendsResponse.data.user_activity.map(d => this.formatDate(d.time))
        this.userActivity.datasets[0].data = trendsResponse.data.user_activity.map(d => d.count)

        this.performanceMetrics.labels = trendsResponse.data.performance.map(d => this.formatDate(d.time))
        this.performanceMetrics.datasets[0].data = trendsResponse.data.performance.map(d => d.avg_response_time)

        const dailyStatsResponse = await axios.get('/api/v1/admin/stats/daily')
        this.dailyStats = dailyStatsResponse.data

        if (trendsResponse.data.image_generation) {
          this.updateImageGenerationChart(trendsResponse.data.image_generation)
        }
        
        if (trendsResponse.data.events) {
          this.updateEventChart(trendsResponse.data.events)
        }
        
        if (trendsResponse.data.subscription_tiers) {
          this.updateSubscriptionChart(trendsResponse.data.subscription_tiers)
        }
        
        if (trendsResponse.data.resource_utilization) {
          this.updateResourceChart(trendsResponse.data.resource_utilization)
        }

        this.error = null
      } catch (error) {
        console.error('Error fetching analytics:', error)
        this.error = 'Failed to fetch analytics data'
      } finally {
        this.loading = false
      }
    },
    
    updateImageGenerationChart(data) {
      this.imageGeneration.labels = data.map(item => this.formatDate(item.time))
      this.imageGeneration.datasets[0].data = data.map(item => item.total_images)
      this.averageSuccessRate = data.reduce((acc, curr) => acc + curr.success_rate, 0) / data.length
      this.averageProcessingTime = data.reduce((acc, curr) => acc + curr.avg_processing_time, 0) / data.length
    },
    
    updateEventChart(data) {
      this.eventStats.labels = data.map(item => this.formatDate(item.time))
      this.eventStats.datasets[0].data = data.map(item => item.total_events)
      this.eventCompletionRate = data.reduce((acc, curr) => acc + curr.completion_rate, 0) / data.length
      this.averageParticipants = data.reduce((acc, curr) => acc + curr.avg_participants, 0) / data.length
    },
    
    updateSubscriptionChart(data) {
      this.subscriptionData.labels = data.map(item => item.tier)
      this.subscriptionData.datasets[0].data = data.map(item => item.count)
    },
    
    updateResourceChart(data) {
      this.resourceUtilization.labels = data.map(item => this.formatDate(item.time))
      this.resourceUtilization.datasets[0].data = data.map(item => item.storage.average_gb)
      this.resourceUtilization.datasets[1].data = data.map(item => item.api_calls.average)
      
      const latest = data[data.length - 1]
      this.currentStorageUsage = latest?.storage.average_gb.toFixed(2) || 0
      this.currentApiCalls = latest?.api_calls.average.toFixed(0) || 0
    }
  },
  mounted() {
    this.fetchAnalytics()
    this.refreshInterval = setInterval(this.fetchAnalytics, 5 * 60 * 1000)
  },
  beforeUnmount() {
    clearInterval(this.refreshInterval)
  }
}
</script>
