<template>
  <div class="admin-page">
    <header class="page-header">
      <h1>Billing & Subscription</h1>
    </header>
    
    <main class="page-content">
      <div class="subscription-info">
        <h2>Current Subscription</h2>
        <div class="info-card">
          <div class="info-row">
            <span class="label">Plan Name:</span>
            <span class="value">{{ subscription.planName }}</span>
          </div>
          <div class="info-row">
            <span class="label">Billing Cycle:</span>
            <span class="value">{{ subscription.billingCycle }}</span>
          </div>
          <div class="info-row">
            <span class="label">Next Billing Date:</span>
            <span class="value">{{ formatDate(subscription.nextBillingDate) }}</span>
          </div>
        </div>
      </div>

      <div class="usage-stats">
        <h2>Usage Statistics</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <h3>API Calls</h3>
            <div class="stat-value">{{ usage.apiCalls }}/{{ usage.apiCallsLimit }}</div>
            <div class="progress-bar">
              <div 
                class="progress" 
                :style="{ width: (usage.apiCalls / usage.apiCallsLimit * 100) + '%' }"
              ></div>
            </div>
          </div>
          <div class="stat-card">
            <h3>Storage Used</h3>
            <div class="stat-value">{{ formatStorage(usage.storageUsed) }}/{{ formatStorage(usage.storageLimit) }}</div>
            <div class="progress-bar">
              <div 
                class="progress" 
                :style="{ width: (usage.storageUsed / usage.storageLimit * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="payment-history">
        <h2>Payment History</h2>
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Invoice</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in payments" :key="payment.id">
              <td>{{ formatDate(payment.date) }}</td>
              <td>{{ payment.description }}</td>
              <td>{{ formatCurrency(payment.amount) }}</td>
              <td>
                <span :class="'status-badge ' + payment.status.toLowerCase()">
                  {{ payment.status }}
                </span>
              </td>
              <td>
                <button @click="downloadInvoice(payment.id)" class="btn btn-link">
                  Download
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'BillingSubscription',
  data() {
    return {
      subscription: {
        planName: 'Enterprise Plan',
        billingCycle: 'Monthly',
        nextBillingDate: '2025-03-27'
      },
      usage: {
        apiCalls: 75000,
        apiCallsLimit: 100000,
        storageUsed: 1.5e9, // 1.5GB in bytes
        storageLimit: 5e9 // 5GB in bytes
      },
      payments: [] // This would be populated from your API
    }
  },
  methods: {
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },
    formatStorage(bytes) {
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let size = bytes
      let unitIndex = 0
      
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
      }
      
      return `${size.toFixed(1)} ${units[unitIndex]}`
    },
    downloadInvoice(paymentId) {
      // TODO: Implement invoice download logic
      console.log('Downloading invoice for payment:', paymentId)
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

.info-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.info-row {
  display: flex;
  margin-bottom: 10px;
}

.info-row .label {
  font-weight: bold;
  width: 150px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.stat-card h3 {
  margin-top: 0;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.progress-bar {
  background: #e9ecef;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
}

.progress {
  background: #4CAF50;
  height: 100%;
  transition: width 0.3s ease;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.table th,
.table td {
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status-badge.success {
  background-color: #4CAF50;
  color: white;
}

.status-badge.pending {
  background-color: #ff9800;
  color: white;
}

.status-badge.failed {
  background-color: #f44336;
  color: white;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-link {
  background: none;
  border: none;
  color: #2196F3;
  text-decoration: underline;
  padding: 0;
}

.btn-link:hover {
  color: #0b7dda;
}
</style>
