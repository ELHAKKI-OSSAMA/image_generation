import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter } from '@/router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import './assets/main.css'
import 'vue-multiselect/dist/vue-multiselect.css'
// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
})

// Toast Notifications
import ToastPlugin from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

// Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { 
  faUserSecret, 
  faHome, 
  faMagic, 
  faImages, 
  faUserCircle,
  faUser,
  faSignOutAlt,
  faTachometerAlt,
  faUsers,
  faCube,
  faCubes,
  faPlus,
  faTrash,
  faEdit,
  faSearch,
  faFilter,
  faSort,
  faChevronDown,
  faChevronUp,
  faExclamationCircle,
  faCheckCircle,
  faTimesCircle,
  faTimes,
  faInfoCircle,
  faSync,
  faSpinner,
  faShieldAlt,
  faCalendar,
  faBook,
  faQuestionCircle,
  faCog,
  faChevronLeft,
  faChevronRight,
  faCalendarAlt,
  faClipboardList,
  faCreditCard,
  faBell,
  faChartLine,
  faDownload,
  faClock,
  faBuilding
} from '@fortawesome/free-solid-svg-icons'
import {
  faGithub,
  faTwitter
} from '@fortawesome/free-brands-svg-icons'

// Add icons to library
library.add(
  faUserSecret,
  faHome,
  faMagic,
  faImages,
  faUserCircle,
  faUser,
  faSignOutAlt,
  faTachometerAlt,
  faUsers,
  faCube,
  faCubes,
  faPlus,
  faTrash,
  faEdit,
  faSearch,
  faFilter,
  faSort,
  faChevronDown,
  faChevronUp,
  faExclamationCircle,
  faCheckCircle,
  faTimesCircle,
  faTimes,
  faInfoCircle,
  faSync,
  faSpinner,
  faShieldAlt,
  faGithub,
  faCalendar,
  faBook,
  faQuestionCircle,
  faCog,
  faChevronLeft,
  faChevronRight,
  faCalendarAlt,
  faClipboardList,
  faCreditCard,
  faBell,
  faChartLine,
  faDownload,
  faTwitter,
  faClock,
  faBuilding
)

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
const router = createRouter()

app.use(router)
app.use(pinia)
app.use(vuetify)
app.use(ToastPlugin, {
  position: 'top-right',
  duration: 3000,
  dismissible: true
})
app.component('font-awesome-icon', FontAwesomeIcon)

// Make router and pinia globally available
window.router = router
window.pinia = pinia

// Initialize auth store
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore(pinia)

// Mount app first
app.mount('#app')

// Then initialize auth
authStore.initAuth()
