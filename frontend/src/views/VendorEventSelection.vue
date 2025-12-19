<template>
  <div class="selection-container">
    <n-card class="selection-box" :bordered="false">
      <template #header>
        <h2>请选择您所在的展会</h2>
      </template>
      <p>选择后将需要输入该展会的摊主密码。</p>

      <div v-if="eventStore.isLoading" class="loading-message">
        <n-spin>
          <template #description>正在加载展会列表...</template>
        </n-spin>
      </div>
      <div v-else-if="eventStore.error" class="error-message">
        <n-alert type="error" :bordered="false">{{ eventStore.error }}</n-alert>
      </div>

      <div v-else-if="ongoingEvents.length" class="event-list">
        <n-space vertical size="large">
          <n-card
            v-for="event in ongoingEvents"
            :key="event.id"
            class="event-item"
            hoverable
            :bordered="true"
            @click="selectEvent(event)"
          >
            <h3>{{ event.name }}</h3>
            <span>{{ event.date }}</span>
          </n-card>
        </n-space>
      </div>

      <p v-else class="no-events-message">当前没有正在进行的展会。</p>

      <div class="admin-login-link">
        <RouterLink to="/login/admin">
          <n-button text>管理员入口</n-button>
        </RouterLink>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
import { useEventStore } from '@/stores/eventStore';
import { NCard, NSpin, NAlert, NSpace, NButton } from 'naive-ui';

const eventStore = useEventStore();
const router = useRouter();

// 计算属性，只筛选出“进行中”的展会
const ongoingEvents = computed(() => {
  return eventStore.events.filter(event => event.status === '进行中');
});

function selectEvent(event) {
  // 当用户选择一个展会时，跳转到该展会的摊主登录页面
  router.push({
    name: 'login',
    params: { role: 'vendor' },
    query: { 
      eventId: event.id,
      // 登录成功后，我们希望他跳转到这个展会的摊主页面
      redirect: `/vendor/${event.id}` 
    }
  });
}

onMounted(() => {
  // 页面加载时，获取所有展会列表
  eventStore.fetchEvents();
});
</script>

<style scoped>
.selection-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
.selection-box {
  width: 500px;
  max-width: 90%;
  padding: 2rem;
  background-color: var(--card-bg-color);
  border-radius: 8px;
  text-align: center;
}
.event-list {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.event-item {
  cursor: pointer;
}
.no-events-message {
  margin-top: 2rem;
  color: #888;
}
.admin-login-link {
  margin-top: 2rem;
  font-size: 0.9rem;
}
.admin-login-link a { text-decoration: none; }
</style>