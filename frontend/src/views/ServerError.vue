<template>
  <div class="error-page">
    <n-card :bordered="false" size="large">
      <n-result status="500" title="服务器错误" description="服务器发生了意外错误，请稍后重试或返回首页。">
        <template #footer>
          <RouterLink to="/">
            <n-button type="primary">返回首页</n-button>
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
