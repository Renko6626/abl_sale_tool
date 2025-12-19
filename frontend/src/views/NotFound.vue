<template>
  <div class="error-page">
    <n-card :bordered="false" size="large">
      <n-result status="404" title="页面未找到" description="抱歉，您访问的页面不存在或已被移除。">
        <template #footer>
          <RouterLink to="/">
            <n-button type="primary">返回首页</n-button>
          </RouterLink>
          <RouterLink to="/login/admin" style="margin-left: 8px;">
            <n-button tertiary>管理员入口</n-button>
          </RouterLink>
        </template>
      </n-result>
    </n-card>
  </div>
  
</template>

<script setup>
import { NResult, NButton, NCard } from 'naive-ui';
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
</style>
