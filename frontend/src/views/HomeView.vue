<template>
  <div class="enhanced-container">
    <div class="input-group">
      <el-input
        v-model="url"
        placeholder="输入目标网址 (例: https://example.com)"
        size="large"
        class="modern-input"
        clearable
        :disabled="loading"
        @keyup.enter="crawl"
      >
        <template #prefix>
          <el-icon class="input-prefix"><Link /></el-icon>
        </template>
      </el-input>

      <el-button
        type="primary"
        size="large"
        :loading="loading"
        @click="crawl"
        class="action-button"
        :disabled="loading || !url"
      >
        {{ loading ? "数据采集中..." : "开始爬取" }}
      </el-button>
    </div>

    <transition name="el-zoom-in-top">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        class="error-panel"
        @close="errorMessage = ''"
      />
    </transition>

    <transition name="el-zoom-in-top">
      <el-card v-if="content" class="result-panel">
        <template #header>
          <div class="panel-header">
            <el-icon class="header-badge"><Document /></el-icon>
            <span class="panel-title">数据抓取结果</span>
            <el-button
              type="success"
              size="small"
              @click="downloadContent"
              class="download-button"
              v-if="effectiveCharCount > 0"
            >
              <el-icon class="download-icon"><Download /></el-icon>
              下载结果
            </el-button>
            <el-tag type="info" size="small" effect="dark" class="status-tag">
              {{ effectiveCharCount }} 个字符
            </el-tag>
          </div>
        </template>

        <div class="content-viewer">
          <pre class="data-output">{{ content }}</pre>
        </div>
      </el-card>
    </transition>
  </div>
</template>

<script>
import { Link, Document, Download } from "@element-plus/icons-vue";
// import { ElNotification } from "element-plus"; 未来可能会使用，暂时注释掉

export default {
  name: "EnhancedCrawlerView",
  data() {
    return {
      url: "",
      content: "",
      errorMessage: "",
      loading: false,
    };
  },
  components: {
    Link,
    Document,
    Download,
  },
  computed: {
    effectiveCharCount() {
      return this.content ? this.content.replace(/\s/g, "").length : 0;
    },
  },
  methods: {
    async crawl() {
      if (!this.validateUrl()) {
        this.$message.warning("请输入有效的网页地址");

        // 弹窗形式提示，未来可能会使用，暂时注释掉
        // ElNotification.warning({
        //   title: "警告",
        //   message: "请输入有效的网页地址",
        //   position: "top-right",
        // });
        return;
      }

      try {
        this.loading = true;
        this.content = "";
        this.errorMessage = "";
        this.url = this.processUrl();

        const response = await this.$axios.get("/crawl", {
          params: { url: this.url },
          timeout: 15000,
        });

        if (response.data.success) {
          this.content = response.data.content;
          this.$message.success("🎉 数据采集成功");
        } else {
          this.errorMessage = `服务器错误：${response.data.error_message}`;
          this.$message.error("❌ 数据采集失败");
        }
      } catch (error) {
        if (
          error.code === "ECONNABORTED" &&
          error.message.includes("timeout")
        ) {
          this.errorMessage = `请求超时：${error.code} : ${error.message}`;
          this.$message.error("⏳ 请求超时，请稍后重试");
        } else {
          this.errorMessage = `请求失败: ${error.code} : ${
            error.message || "未知错误"
          }`;
          this.$message.error("⚠️ 请求失败");
        }
      } finally {
        this.loading = false;
      }
    },
    validateUrl() {
      const pattern =
        /^(https?:\/\/)?((([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)|localhost)(:(0|[1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]))?([\w\-.,@?^=%&:/~+#]*[\w@?^=%&:/~+#])?$/i;
      return pattern.test(this.url);
    },
    processUrl() {
      let processedUrl = this.url.split("#")[0];
      if (!/^https?:\/\//i.test(processedUrl)) {
        processedUrl = "https://" + processedUrl;
      }

      let urlObj;
      try {
        urlObj = new URL(processedUrl);
      } catch (e) {
        return processedUrl;
      }

      urlObj.pathname = urlObj.pathname
        .replace(/\/+/g, "/")
        .replace(/^\/?/, "/");

      if (!this.isFilePath(urlObj.pathname)) {
        if (!urlObj.pathname.endsWith("/")) {
          urlObj.pathname += "/";
        }
      }

      return urlObj.toString();
    },
    isFilePath(pathname) {
      if (pathname === "/") return false;
      const segments = pathname.split("/");
      const lastSegment = segments[segments.length - 1];
      if (lastSegment === "") return false;
      const dotIndex = lastSegment.lastIndexOf(".");
      return dotIndex > -1 && dotIndex < lastSegment.length - 1;
    },
    downloadContent() {
      const blob = new Blob([this.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      const domain = new URL(this.url).hostname.replace(/\./g, "-");
      const timestamp = new Date()
        .toISOString()
        .slice(0, 19)
        .replace(/[-:T]/g, "");
      link.download = `crawler-${domain}-${timestamp}.md`;

      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/styles/home-view.scss";
</style>
