<template>
  <div class="admin-page">
    <header class="page-header">
      <h1>Notifications & Email Templates</h1>
    </header>
    
    <main class="page-content">
      <div class="settings-section">
        <h2>Notification Settings</h2>
        <div class="settings-grid">
          <div class="setting-card">
            <div class="setting-header">
              <h3>Email Notifications</h3>
              <label class="switch">
                <input 
                  type="checkbox" 
                  v-model="settings.emailEnabled"
                  @change="updateSettings"
                >
                <span class="slider"></span>
              </label>
            </div>
            <div class="setting-content" v-if="settings.emailEnabled">
              <div class="form-group">
                <label>Frequency</label>
                <select v-model="settings.emailFrequency" class="form-control">
                  <option value="immediate">Immediate</option>
                  <option value="daily">Daily Digest</option>
                  <option value="weekly">Weekly Digest</option>
                </select>
              </div>
            </div>
          </div>

          <div class="setting-card">
            <div class="setting-header">
              <h3>System Alerts</h3>
              <label class="switch">
                <input 
                  type="checkbox" 
                  v-model="settings.alertsEnabled"
                  @change="updateSettings"
                >
                <span class="slider"></span>
              </label>
            </div>
            <div class="setting-content" v-if="settings.alertsEnabled">
              <div class="form-group">
                <label>Priority Level</label>
                <select v-model="settings.alertPriority" class="form-control">
                  <option value="high">High Only</option>
                  <option value="medium">Medium and High</option>
                  <option value="all">All Alerts</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="templates-section">
        <h2>Email Templates</h2>
        <div class="templates-list">
          <div 
            v-for="template in emailTemplates" 
            :key="template.id" 
            class="template-card"
          >
            <div class="template-header">
              <h3>{{ template.name }}</h3>
              <div class="template-actions">
                <button 
                  @click="editTemplate(template)" 
                  class="btn btn-primary"
                >
                  Edit
                </button>
                <button 
                  @click="previewTemplate(template)" 
                  class="btn btn-secondary"
                >
                  Preview
                </button>
              </div>
            </div>
            <div class="template-info">
              <p class="description">{{ template.description }}</p>
              <div class="template-meta">
                <span>Last Modified: {{ formatDate(template.lastModified) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'Notifications',
  data() {
    return {
      settings: {
        emailEnabled: true,
        emailFrequency: 'immediate',
        alertsEnabled: true,
        alertPriority: 'medium'
      },
      emailTemplates: [
        {
          id: 1,
          name: 'Welcome Email',
          description: 'Sent to new users upon registration',
          lastModified: '2025-02-27'
        },
        {
          id: 2,
          name: 'Password Reset',
          description: 'Password reset instructions template',
          lastModified: '2025-02-26'
        },
        {
          id: 3,
          name: 'Account Verification',
          description: 'Email verification template for new accounts',
          lastModified: '2025-02-25'
        }
      ]
    }
  },
  methods: {
    updateSettings() {
      // TODO: Implement settings update logic
      console.log('Updating settings:', this.settings)
    },
    editTemplate(template) {
      // TODO: Implement template editing logic
      console.log('Editing template:', template)
    },
    previewTemplate(template) {
      // TODO: Implement template preview logic
      console.log('Previewing template:', template)
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString()
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

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.setting-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.setting-header h3 {
  margin: 0;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4CAF50;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.form-group {
  margin-bottom: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.templates-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.template-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.template-header h3 {
  margin: 0;
}

.template-actions {
  display: flex;
  gap: 10px;
}

.template-info {
  color: #666;
}

.description {
  margin-bottom: 10px;
}

.template-meta {
  font-size: 0.875rem;
  color: #888;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}
</style>
