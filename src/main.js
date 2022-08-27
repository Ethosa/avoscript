import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import App from './App.vue'
import router from "./router"

import './main.css'
import 'vuetify/styles'

createApp(App)
  .use(router)
  .use(createVuetify())
  .use(createPinia())
  .mount('#app')
