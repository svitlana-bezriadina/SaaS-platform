import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Antd)

const theme = localStorage.getItem('theme') || 'light'
document.documentElement.dataset.theme = theme

axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token');

    if (token){
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
})

app.mount('#app')
