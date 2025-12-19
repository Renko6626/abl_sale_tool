<template>
  <div class="dashboard-container">
    <header>
      <h1>管理后台</h1>
      <p>在这里管理您的所有展会和商品。</p>
    </header>
    <main>
      <n-space vertical size="large">
        <!-- 创建展会的表单组件 -->
        <CreateEventForm />
        
        <!-- 局域网扫码访问 在网站部署版本里面要隐藏 -->
        <n-card title="手机/平板扫码访问" size="small">
          <n-space vertical size="small">
            <div class="qr-actions">
              <n-button type="primary" :loading="isFetching" @click="fetchServerInfo">
                {{ isFetching ? '获取中...' : '获取局域网二维码' }}
              </n-button>
              <span class="hint">同一局域网内扫码可直接访问对应页面</span>
            </div>
            <n-alert v-if="fetchError" type="error" :bordered="false">{{ fetchError }}</n-alert>
            <div v-if="serverInfo" class="qr-grid">
              <div class="qr-card">
                <div class="qr-title">顾客入口</div>
                <img :src="qrUrl(serverInfo.order_url)" alt="顾客入口二维码" />
                <a :href="serverInfo.order_url" target="_blank">{{ serverInfo.order_url }}</a>
              </div>
              <div class="qr-card">
                <div class="qr-title">摊主入口</div>
                <img :src="qrUrl(serverInfo.vendor_url)" alt="摊主入口二维码" />
                <a :href="serverInfo.vendor_url" target="_blank">{{ serverInfo.vendor_url }}</a>
              </div>
              <div class="qr-card">
                <div class="qr-title">管理员入口</div>
                <img :src="qrUrl(serverInfo.admin_url)" alt="管理员入口二维码" />
                <a :href="serverInfo.admin_url" target="_blank">{{ serverInfo.admin_url }}</a>
              </div>
            </div>
          </n-space>
        </n-card>
        
        <!-- 显示展会列表的组件 -->
        <EventList />
      </n-space>
    </main>
  </div>
</template>

<script setup>
// 导入需要的组件
import CreateEventForm from '@/components/event/CreateEventForm.vue';
import EventList from '@/components/event/EventList.vue';
import { NSpace, NCard, NButton, NAlert } from 'naive-ui';
import api from '@/services/api';
import { ref } from 'vue';

const isFetching = ref(false);
const fetchError = ref('');
const serverInfo = ref(null);

const QR_BASE = 'https://api.qrserver.com/v1/create-qr-code/';

function qrUrl(target) {
  const size = '220x220';
  return `${QR_BASE}?size=${size}&data=${encodeURIComponent(target)}`;
}

async function fetchServerInfo() {
  isFetching.value = true;
  fetchError.value = '';
  try {
    const { data } = await api.get('/server-info');
    serverInfo.value = data;
  } catch (err) {
    fetchError.value = err.response?.data?.error || '获取服务器信息失败，请检查后端服务';
  } finally {
    isFetching.value = false;
  }
}
</script>

<style scoped>
.dashboard-container {
  max-width: 800px;
  margin: 0 auto;
}
header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}
header h1 {
  color: var(--accent-color);
  margin: 0;
}
header p {
  color: #aaa;
  margin-top: 0.5rem;
}

.qr-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.hint {
  color: #aaa;
  font-size: 0.9rem;
}
.qr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}
.qr-card {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.75rem;
  background: var(--card-bg-color);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.qr-title { font-weight: 600; }
.qr-card img {
  width: 180px;
  height: 180px;
  align-self: center;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: #fff;
}
.qr-card a {
  word-break: break-all;
  color: var(--accent-color);
}
</style>