import { createApp } from 'vue'
import App from './App.vue'
import withUUID from "vue-uuid";
import router from "./modules/router";
import { createPinia } from 'pinia'

const pinia = createPinia()
withUUID(createApp(App).use(router).use(pinia)).mount('#app')
