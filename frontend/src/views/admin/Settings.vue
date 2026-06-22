<template>
  <div class="admin-page">
    <header class="page-header">
      <h1>Admin Settings</h1>
    </header>
    
    <main class="page-content">
      <div class="settings-section">
        <div class="settings-card">
          <h2>System Settings</h2>
          
          <div class="settings-group">
            <h3>General</h3>
            <div class="form-group">
              <label for="siteName">Site Name</label>
              <input 
                type="text" 
                id="siteName" 
                v-model="settings.siteName" 
                class="form-control"
              />
            </div>

            <div class="form-group">
              <label for="siteUrl">Site URL</label>
              <input 
                type="url" 
                id="siteUrl" 
                v-model="settings.siteUrl" 
                class="form-control"
              />
            </div>

            <div class="form-group">
              <label for="adminEmail">Admin Email</label>
              <input 
                type="email" 
                id="adminEmail" 
                v-model="settings.adminEmail" 
                class="form-control"
              />
            </div>
          </div>

          <div class="settings-group">
            <h3>Security</h3>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="settings.requireEmailVerification"
                />
                Require Email Verification
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="settings.allowRegistration"
                />
                Allow New User Registration
              </label>
            </div>

            <div class="form-group">
              <label for="sessionTimeout">Session Timeout (minutes)</label>
              <input 
                type="number" 
                id="sessionTimeout" 
                v-model="settings.sessionTimeout" 
                class="form-control"
                min="5"
              />
            </div>
          </div>

          <div class="settings-group">
            <h3>Email Settings</h3>
            <div class="form-group">
              <label for="smtpHost">SMTP Host</label>
              <input 
                type="text" 
                id="smtpHost" 
                v-model="settings.smtp.host" 
                class="form-control"
              />
            </div>

            <div class="form-group">
              <label for="smtpPort">SMTP Port</label>
              <input 
                type="number" 
                id="smtpPort" 
                v-model="settings.smtp.port" 
                class="form-control"
              />
            </div>

            <div class="form-group">
              <label for="smtpUser">SMTP Username</label>
              <input 
                type="text" 
                id="smtpUser" 
                v-model="settings.smtp.username" 
                class="form-control"
              />
            </div>

            <div class="form-group">
              <label for="smtpPass">SMTP Password</label>
              <input 
                type="password" 
                id="smtpPass" 
                v-model="settings.smtp.password" 
                class="form-control"
              />
            </div>

            <div class="form-group">
              <button @click="testEmailSettings" class="btn btn-secondary">
                Test Email Settings
              </button>
            </div>
          </div>

          <div class="settings-group">
            <h3>Backup & Maintenance</h3>
            <div class="form-group">
              <button @click="backupDatabase" class="btn btn-secondary">
                Backup Database
              </button>
            </div>

            <div class="form-group">
              <button @click="clearCache" class="btn btn-secondary">
                Clear System Cache
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button @click="saveSettings" class="btn btn-primary">
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminSettings',
  data() {
    return {
      settings: {
        siteName: 'Image Generator',
        siteUrl: 'https://example.com',
        adminEmail: 'admin@example.com',
        requireEmailVerification: true,
        allowRegistration: true,
        sessionTimeout: 30,
        smtp: {
          host: '',
          port: 587,
          username: '',
          password: ''
        }
      }
    }
  },
  methods: {
    async saveSettings() {
      try {
        // TODO: Implement settings save logic
        console.log('Saving settings:', this.settings)
      } catch (error) {
        console.error('Error saving settings:', error)
      }
    },
    async testEmailSettings() {
      try {
        // TODO: Implement email test logic
        console.log('Testing email settings')
      } catch (error) {
        console.error('Error testing email:', error)
      }
    },
    async backupDatabase() {
      try {
        // TODO: Implement database backup logic
        console.log('Backing up database')
      } catch (error) {
        console.error('Error backing up database:', error)
      }
    },
    async clearCache() {
      try {
        // TODO: Implement cache clear logic
        console.log('Clearing system cache')
      } catch (error) {
        console.error('Error clearing cache:', error)
      }
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

.settings-card {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.settings-group {
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid #eee;
}

.settings-group:last-child {
  border-bottom: none;
}

.settings-group h3 {
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
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
  margin-right: 10px;
}

.btn:hover {
  opacity: 0.9;
}
</style>
