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
        {{ loading ? "数据采集中..." : "启动爬取" }}
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
// 输入区样式
.enhanced-container {
  max-width: 1440px;
  margin: 2rem auto;
  padding: 0 2rem;
  background: linear-gradient(135deg, #f8fbff 0%, #f0f7ff 100%);
  min-height: 100vh;
}

.input-group {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 79, 255, 0.08);
}

.modern-input {
  --el-input-border-color: #e0e7ff;
  --el-input-hover-border-color: #a5b4fc;
  --el-input-focus-border-color: #6366f1;

  :deep(.el-input__prefix) {
    color: #6366f1;
    padding-right: 0.75rem;
  }
}

.action-button {
  width: 160px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:disabled {
    background: linear-gradient(135deg, #9a9cf7 0%, #7f79ee 100%);
    &:hover {
      background: linear-gradient(135deg, #9a9cf7 0%, #7f79ee 100%);
    }
  }

  &:not(:disabled):hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }
}

// 结果展示区样式
.result-panel {
  margin-top: 2rem;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 79, 255, 0.08);

  :deep(.el-card__header) {
    border-bottom: 1px solid #e0e7ff;
    padding: 1rem 1.5rem;
  }
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;

  .header-badge {
    color: #6366f1;
    font-size: 1.4em;
    flex-shrink: 0;
  }

  .panel-title {
    font-weight: 600;
    color: #1e293b;
    letter-spacing: -0.5px;
    flex-shrink: 0;
  }

  // 下载按钮样式
  :deep(.download-button) {
    margin-left: auto;
    background: linear-gradient(135deg, #9a9cf7 0%, #7f79ee 100%);
    border: none;
    color: white;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    flex-shrink: 0;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
      background: linear-gradient(135deg, #9a9cf7 0%, #7f79ee 100%);
    }

    &::before {
      content: "";
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(
        120deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
      );
      transition: 0.5s;
    }

    &:hover::before {
      left: 100%;
    }

    .download-icon {
      margin-right: 6px;
      font-size: 1.1em;
      vertical-align: -0.15em;
      transition: transform 0.2s ease;
    }

    &:active .download-icon {
      transform: translateY(1px);
    }
  }

  // 字符统计样式
  .status-tag {
    margin-right: 0.5rem;
    border-color: #6366f1;
    color: #6366f1;
    background: transparent !important;
    flex-shrink: 0;
  }
}

// 内容显示区
.content-viewer {
  background: #f8faff;
  border-radius: 8px;
  max-height: 70vh;
  overflow: auto;
  padding: 1.5rem;

  &::-webkit-scrollbar {
    width: 8px;
    background: rgba(99, 102, 241, 0.05);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.2);
    border-radius: 4px;
  }
}

.data-output {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.95em;
  line-height: 1.7;
  color: #334155;
  white-space: pre-wrap;
  text-align: left;
}

// 响应式调整（移动端适配）
@media (max-width: 768px) {
  .input-group {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .action-button {
    width: 100%;
  }

  .content-viewer {
    max-height: 60vh;
  }

  .panel-header {
    row-gap: 0.8rem;

    :deep(.download-button) {
      order: 1;
      width: 100%;
      margin-left: 0;
    }

    .status-tag {
      margin-left: auto;
    }
  }
}

// 错误提示样式
.error-panel {
  margin-top: 1.5rem;
  border-radius: 8px;
}
</style>
