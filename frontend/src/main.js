import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import axios from "axios";

// 设置axios的全局默认配置
axios.defaults.baseURL = "http://localhost:8000/api";

const app = createApp(App);
app.config.globalProperties.$axios = axios;
app.use(router);
app.mount("#app");
