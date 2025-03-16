<template>
  <div class="enhanced-container">
    <!-- 输入区域增强 -->
    <div class="input-group">
      <el-input
        v-model="url"
        placeholder="输入目标网址 (例: https://example.com)"
        size="large"
        class="modern-input"
        clearable
        :disabled="loading"
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

    <!-- 结果展示优化 -->
    <transition name="el-zoom-in-top">
      <el-card v-if="content" class="result-panel">
        <template #header>
          <div class="panel-header">
            <el-icon class="header-badge"><Document /></el-icon>
            <span class="panel-title">数据抓取结果</span>
            <el-tag type="info" size="small" effect="dark" class="status-tag">
              {{ contentLines }} 行内容
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
import { Link, Document } from "@element-plus/icons-vue";
// import { ElNotification } from "element-plus"; 未来可能会使用，暂时注释掉

export default {
  name: "EnhancedCrawlerView",
  data() {
    return {
      url: "",
      content: "",
      loading: false,
    };
  },
  components: {
    Link,
    Document,
  },
  computed: {
    contentLines() {
      return this.content ? this.content.split("\n").length : 0;
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
        const response = await this.$axios.get("/crawl", {
          params: { url: this.url },
          timeout: 20000,
        });

        this.content = response.data.success
          ? response.data.content
          : `服务器错误: ${response.data.error_message}`;
      } catch (error) {
        this.content = `请求失败: ${error.code || "网络异常"}`;
      } finally {
        this.loading = false;
      }
    },
    validateUrl() {
      const pattern =
        /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
      return pattern.test(this.url);
    },
  },
};
</script>

<style lang="scss" scoped>
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;

  &:disabled {
    background: linear-gradient(135deg, #9a9cf7 0%, #7f79ee 100%);
  }

  &:disabled:hover {
    background: linear-gradient(135deg, #9a9cf7 0%, #7f79ee 100%);
  }

  &:not(:disabled):hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }
}

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
  gap: 1rem;

  .header-badge {
    color: #6366f1;
    font-size: 1.4em;
  }

  .panel-title {
    font-weight: 600;
    color: #1e293b;
    letter-spacing: -0.5px;
  }

  .status-tag {
    margin-left: auto;
  }
}

.content-viewer {
  background: #f8faff;
  border-radius: 8px;
  max-height: 70vh;
  overflow: auto;
  padding: 1.5rem;
}

.data-output {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.95em;
  line-height: 1.7;
  color: #334155;
  white-space: pre-wrap;
  counter-reset: line;
  text-align: left;

  &::before {
    content: attr(data-content);
  }
}

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
}
</style>
