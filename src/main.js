import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

import './assets/styles.css'

// Настройка Axios для глобального использования
axios.defaults.baseURL = 'http://localhost:8000';

const app = createApp(App)

app.config.globalProperties.$axios = axios; // Глобально доступен через this.$axios
app.config.globalProperties.$backend = "http://localhost:8000"

app.use(router).mount('#app')

