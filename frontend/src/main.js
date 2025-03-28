import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Create the Vue app
const app = createApp(App)

// Use the router
app.use(router)

// Mount the app
app.mount('#app')

console.log('App started with router:', router);

// Note: AuthMixin needs to be updated to use Vue 3 composition API or provide pattern
// For now, we're removing it to make the app compile
