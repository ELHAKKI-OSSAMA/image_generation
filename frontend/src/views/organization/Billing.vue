<template>
  <div class="billing-page">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-gray-900">Billing & Subscription</h1>
      <p class="text-gray-600 mt-1">Manage your organization's billing information and subscription plan</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-6 bg-red-50 border border-red-200 mb-6 rounded-lg">
      <p class="text-red-700">{{ error }}</p>
      <button @click="fetchBillingData" class="mt-2 text-sm text-red-700 underline">Retry</button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Current Plan Section -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div class="flex justify-between items-start mb-6">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Current Plan</h2>
              <p class="text-gray-600 text-sm mt-1">Your organization is currently on the {{ currentPlan.name }} plan</p>
            </div>
            <span 
              :class="currentPlan.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
              class="px-3 py-1 rounded-full text-sm font-medium"
            >
              {{ currentPlan.status === 'active' ? 'Active' : 'Pending' }}
            </span>
          </div>

          <div class="border-t border-gray-200 pt-4 mt-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Billing Period</p>
                <p class="font-medium">{{ currentPlan.billingPeriod }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Next Billing Date</p>
                <p class="font-medium">{{ currentPlan.nextBillingDate }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Monthly Price</p>
                <p class="font-medium">${{ currentPlan.price }}/month</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Plan Features</p>
                <ul class="mt-1 text-sm">
                  <li v-for="(feature, index) in currentPlan.features" :key="index" class="flex items-center">
                    <font-awesome-icon icon="check" class="text-primary mr-2 text-xs" />
                    <span>{{ feature }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div class="mt-6 flex flex-wrap gap-3">
            <button 
              @click="showUpgradePlans = true" 
              class="bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg transition-colors"
            >
              Upgrade Plan
            </button>
            <button 
              @click="cancelSubscription" 
              class="border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg transition-colors"
            >
              Cancel Subscription
            </button>
          </div>
        </div>

        <!-- Payment Methods -->
        <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Payment Methods</h2>
          
          <div v-if="paymentMethods.length === 0" class="text-center py-6 bg-gray-50 rounded-lg">
            <p class="text-gray-500">No payment methods found</p>
            <button 
              @click="showAddPaymentMethod = true" 
              class="mt-3 text-primary hover:text-primary-dark font-medium"
            >
              Add Payment Method
            </button>
          </div>
          
          <div v-else>
            <div 
              v-for="method in paymentMethods" 
              :key="method.id" 
              class="flex justify-between items-center p-4 border border-gray-200 rounded-lg mb-3"
            >
              <div class="flex items-center">
                <div class="bg-gray-100 p-2 rounded-md mr-4">
                  <font-awesome-icon 
                    :icon="method.type === 'card' ? 'credit-card' : 'university'" 
                    class="text-gray-600" 
                  />
                </div>
                <div>
                  <p class="font-medium">{{ method.name }}</p>
                  <p class="text-sm text-gray-500">
                    {{ method.type === 'card' ? `**** **** **** ${method.last4}` : method.accountNumber }}
                    <span v-if="method.default" class="ml-2 text-xs bg-gray-100 px-2 py-0.5 rounded-full">Default</span>
                  </p>
                </div>
              </div>
              <div class="flex gap-2">
                <button 
                  v-if="!method.default" 
                  @click="setDefaultPaymentMethod(method.id)" 
                  class="text-sm text-primary hover:text-primary-dark"
                >
                  Set Default
                </button>
                <button 
                  @click="removePaymentMethod(method.id)" 
                  class="text-sm text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
            </div>
            
            <button 
              @click="showAddPaymentMethod = true" 
              class="mt-4 text-primary hover:text-primary-dark font-medium flex items-center"
            >
              <font-awesome-icon icon="plus" class="mr-2" />
              Add New Payment Method
            </button>
          </div>
        </div>
      </div>

      <!-- Billing History -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Billing History</h2>
          
          <div v-if="billingHistory.length === 0" class="text-center py-6 bg-gray-50 rounded-lg">
            <p class="text-gray-500">No billing history available</p>
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="invoice in billingHistory" 
              :key="invoice.id" 
              class="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0"
            >
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-medium">{{ invoice.description }}</p>
                  <p class="text-sm text-gray-500">{{ invoice.date }}</p>
                </div>
                <span 
                  :class="getStatusClass(invoice.status)" 
                  class="px-2 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ invoice.status }}
                </span>
              </div>
              <div class="flex justify-between items-center mt-2">
                <p class="font-medium">${{ invoice.amount }}</p>
                <button 
                  @click="downloadInvoice(invoice.id)" 
                  class="text-sm text-primary hover:text-primary-dark flex items-center"
                >
                  <font-awesome-icon icon="download" class="mr-1" />
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upgrade Plans Modal -->
    <div v-if="showUpgradePlans" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold">Choose a Plan</h2>
          <button @click="showUpgradePlans = false" class="text-gray-500 hover:text-gray-700">
            <font-awesome-icon icon="times" class="text-xl" />
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div 
            v-for="plan in availablePlans" 
            :key="plan.id" 
            class="border rounded-xl p-6 hover:shadow-md transition-shadow"
            :class="{'border-primary': plan.recommended, 'border-gray-200': !plan.recommended}"
          >
            <div v-if="plan.recommended" class="bg-primary text-white text-xs font-semibold uppercase tracking-wide py-1 px-3 rounded-full inline-block mb-3">
              Recommended
            </div>
            <h3 class="text-lg font-semibold">{{ plan.name }}</h3>
            <p class="text-gray-600 text-sm mb-4">{{ plan.description }}</p>
            
            <div class="mb-6">
              <span class="text-3xl font-bold">${{ plan.price }}</span>
              <span class="text-gray-500">/month</span>
            </div>
            
            <ul class="mb-6 space-y-2">
              <li v-for="(feature, index) in plan.features" :key="index" class="flex items-start">
                <font-awesome-icon icon="check" class="text-primary mt-1 mr-2" />
                <span class="text-sm">{{ feature }}</span>
              </li>
            </ul>
            
            <button 
              @click="selectPlan(plan.id)" 
              class="w-full py-2 rounded-lg font-medium"
              :class="plan.recommended ? 'bg-primary hover:bg-primary-dark text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-800'"
            >
              {{ currentPlan.id === plan.id ? 'Current Plan' : 'Select Plan' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Payment Method Modal -->
    <div v-if="showAddPaymentMethod" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold">Add Payment Method</h2>
          <button @click="showAddPaymentMethod = false" class="text-gray-500 hover:text-gray-700">
            <font-awesome-icon icon="times" class="text-xl" />
          </button>
        </div>
        
        <form @submit.prevent="addPaymentMethod">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Card Holder Name</label>
            <input 
              v-model="newPaymentMethod.name" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="John Doe"
              required
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Card Number</label>
            <input 
              v-model="newPaymentMethod.cardNumber" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="4242 4242 4242 4242"
              required
            />
          </div>
          
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
              <input 
                v-model="newPaymentMethod.expiryDate" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary"
                placeholder="MM/YY"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">CVC</label>
              <input 
                v-model="newPaymentMethod.cvc" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary"
                placeholder="123"
                required
              />
            </div>
          </div>
          
          <div class="mb-6">
            <label class="flex items-center">
              <input 
                v-model="newPaymentMethod.setDefault" 
                type="checkbox" 
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <span class="ml-2 text-sm text-gray-600">Set as default payment method</span>
            </label>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button 
              type="button" 
              @click="showAddPaymentMethod = false" 
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
            >
              Add Payment Method
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useOrganizationStore } from '@/stores/organization'

// Store
const organizationStore = useOrganizationStore()

// UI State
const loading = ref(true)
const error = ref(null)
const showUpgradePlans = ref(false)
const showAddPaymentMethod = ref(false)

// Current Plan
const currentPlan = ref({
  id: 'pro',
  name: 'Professional',
  status: 'active',
  billingPeriod: 'Monthly',
  nextBillingDate: 'June 15, 2025',
  price: 49.99,
  features: [
    'Unlimited events',
    'Advanced analytics',
    'Priority support',
    'Custom branding'
  ]
})

// Payment Methods
const paymentMethods = ref([
  {
    id: 'pm_1',
    name: 'Visa ending in 4242',
    type: 'card',
    last4: '4242',
    default: true
  },
  {
    id: 'pm_2',
    name: 'Mastercard ending in 5555',
    type: 'card',
    last4: '5555',
    default: false
  }
])

// Billing History
const billingHistory = ref([
  {
    id: 'inv_1',
    description: 'Professional Plan - Monthly',
    date: 'May 15, 2025',
    amount: '49.99',
    status: 'paid'
  },
  {
    id: 'inv_2',
    description: 'Professional Plan - Monthly',
    date: 'April 15, 2025',
    amount: '49.99',
    status: 'paid'
  },
  {
    id: 'inv_3',
    description: 'Professional Plan - Monthly',
    date: 'March 15, 2025',
    amount: '49.99',
    status: 'paid'
  }
])

// Available Plans
const availablePlans = ref([
  {
    id: 'basic',
    name: 'Basic',
    description: 'Perfect for small organizations',
    price: 29.99,
    features: [
      '5 events per month',
      'Basic analytics',
      'Email support',
      '1,000 images per month'
    ],
    recommended: false
  },
  {
    id: 'pro',
    name: 'Professional',
    description: 'Most popular for growing organizations',
    price: 49.99,
    features: [
      'Unlimited events',
      'Advanced analytics',
      'Priority support',
      'Custom branding',
      '5,000 images per month'
    ],
    recommended: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'For large organizations with advanced needs',
    price: 99.99,
    features: [
      'Unlimited everything',
      'Dedicated account manager',
      'Custom integrations',
      'Advanced security features',
      'Unlimited images'
    ],
    recommended: false
  }
])

// New Payment Method Form
const newPaymentMethod = ref({
  name: '',
  cardNumber: '',
  expiryDate: '',
  cvc: '',
  setDefault: false
})

// Methods
const fetchBillingData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // In a real app, you would fetch data from your API
    // For now, we're just simulating a delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // If the organization store has organization data, use it
    if (organizationStore.organization) {
      console.log('Organization data:', organizationStore.organization)
      // You could update currentPlan with real data here
    }
    
  } catch (err) {
    console.error('Error fetching billing data:', err)
    error.value = 'Failed to load billing information. Please try again.'
  } finally {
    loading.value = false
  }
}

const selectPlan = (planId) => {
  // In a real app, this would call your API to change the subscription
  console.log('Selected plan:', planId)
  
  // For demo purposes, just close the modal
  showUpgradePlans.value = false
  
  // You could show a success message here
  alert('Plan selection successful! This is a demo, so no actual changes were made.')
}

const cancelSubscription = () => {
  // In a real app, this would call your API to cancel the subscription
  if (confirm('Are you sure you want to cancel your subscription? This action cannot be undone.')) {
    console.log('Subscription cancelled')
    // You could show a success message here
    alert('Subscription cancelled! This is a demo, so no actual changes were made.')
  }
}

const setDefaultPaymentMethod = (methodId) => {
  // In a real app, this would call your API to set the default payment method
  console.log('Setting default payment method:', methodId)
  
  // For demo purposes, update the local state
  paymentMethods.value = paymentMethods.value.map(method => ({
    ...method,
    default: method.id === methodId
  }))
}

const removePaymentMethod = (methodId) => {
  // In a real app, this would call your API to remove the payment method
  if (confirm('Are you sure you want to remove this payment method?')) {
    console.log('Removing payment method:', methodId)
    
    // For demo purposes, update the local state
    paymentMethods.value = paymentMethods.value.filter(method => method.id !== methodId)
  }
}

const addPaymentMethod = () => {
  // In a real app, this would call your API to add the payment method
  console.log('Adding payment method:', newPaymentMethod.value)
  
  // For demo purposes, update the local state
  const last4 = newPaymentMethod.value.cardNumber.slice(-4)
  
  // If setting as default, update all others
  if (newPaymentMethod.value.setDefault) {
    paymentMethods.value = paymentMethods.value.map(method => ({
      ...method,
      default: false
    }))
  }
  
  // Add the new method
  paymentMethods.value.push({
    id: `pm_${Date.now()}`,
    name: `Card ending in ${last4}`,
    type: 'card',
    last4,
    default: newPaymentMethod.value.setDefault
  })
  
  // Reset form and close modal
  newPaymentMethod.value = {
    name: '',
    cardNumber: '',
    expiryDate: '',
    cvc: '',
    setDefault: false
  }
  
  showAddPaymentMethod.value = false
}

const downloadInvoice = (invoiceId) => {
  // In a real app, this would download the invoice
  console.log('Downloading invoice:', invoiceId)
  alert('This is a demo. In a real app, this would download the invoice PDF.')
}

const getStatusClass = (status) => {
  switch (status) {
    case 'paid':
      return 'bg-green-100 text-green-800'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'failed':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Initialize
onMounted(() => {
  fetchBillingData()
})
</script>