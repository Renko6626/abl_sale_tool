<template>
  <div class="login-container">
    <n-card class="login-box" :bordered="false">
      <h2>{{ title }}</h2>
      <p>{{ subtitle }}</p>
      <form @submit.prevent="handleLogin">
        <n-input v-model:value="password" type="password" placeholder="请输入密码" size="large" />
        <div style="margin-top: 1rem;">
          <n-button type="primary" attr-type="submit" block>进入</n-button>
        </div>
        <div v-if="error" class="error-message" style="margin-top: 1rem;">
          <n-alert type="error" :bordered="false">{{ error }}</n-alert>
        </div>
      </form>
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { NCard, NInput, NButton, NAlert } from 'naive-ui';

const props = defineProps({
  role: { type: String, required: true } // 'admin' or 'vendor'
});

const store = useAuthStore();
const router = useRouter();
const route = useRoute();
const password = ref('');
const error = ref('');

const title = computed(() => props.role === 'admin' ? '管理员后台' : '摊主页面');
const subtitle = computed(() => `请输入${title.value}密码以继续`);

async function handleLogin() {
  error.value = '';
  try {
    // 1. 【核心改动】从路由的 query 中获取 eventId
    const eventId = route.query.eventId;
    
    // 2. 准备重定向路径
    const redirectPath = route.query.redirect || (props.role === 'admin' ? '/admin' : '/');
    
    // 3. 【核心改动】将 eventId 和 redirectPath 都传给 store 的 login action
    await store.login(password.value, props.role, eventId, redirectPath);

  } catch (err) {
    error.value = err.message;
  }
}
</script>

<style scoped>
/* 登录页面的居中样式 */
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; }
.login-box { width: 350px; padding: 2rem; background-color: var(--card-bg-color); border-radius: 8px; text-align: center; }
</style>