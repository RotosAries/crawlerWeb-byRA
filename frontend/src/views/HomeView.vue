<template>
  <div class="home">
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
        const response = await this.$axios.get("/crawl", {
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
