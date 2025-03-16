<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png" />
    <div>
      <input v-model="url" placeholder="请输入URL" />
      <button @click="crawl">开始爬取</button>
    </div>
    <div v-if="content">
      <h3>爬取结果：</h3>
      <pre>{{ content }}</pre>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "HomeView",
  data() {
    return {
      url: "",
      content: "",
    };
  },
  methods: {
    async crawl() {
      try {
        const response = await axios.get("http://localhost:8000/api/crawl", {
          params: {
            url: this.url,
          },
        });
        if (response.data.success) this.content = response.data.content;
        else this.content = `内部处理错误：${response.data.error_message}`;
      } catch (error) {
        this.content = `请求错误：${error.message}`;
      }
    },
  },
};
</script>
