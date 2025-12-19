<template>
  <div class="portal-container">
    <n-card class="portal-box" :bordered="false">
      <header>
        <h1>欢迎光临</h1>
        <p>请选择您所在的展会进入点单页面</p>
      </header>
      
      <div v-if="eventStore.isLoading" class="loading">
        <n-spin>
          <template #description>正在加载展会列表...</template>
        </n-spin>
      </div>
      <div v-else-if="eventStore.error" class="error">
        <n-alert type="error" :bordered="false">{{ eventStore.error }}</n-alert>
      </div>
      
      <div v-else-if="ongoingEvents.length" class="event-list">
        <n-space vertical size="large">
          <RouterLink 
            v-for="event in ongoingEvents" 
            :key="event.id"
            :to="`/events/${event.id}/order`"
            class="event-link-card"
          >
            <n-card hoverable :bordered="true">
              <h2>{{ event.name }}</h2>
              <span>{{ event.date }} @ {{ event.location || '会场' }}</span>
            </n-card>
          </RouterLink>
        </n-space>
      </div>
      
      <div v-else class="no-events">
        <p>当前没有正在进行的贩售活动 (´·ω·`)</p>
        <p>请联系摊主确认展会状态。</p>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { useEventStore } from '@/stores/eventStore'; // 复用我们已有的 eventStore
import { NCard, NSpin, NAlert, NSpace } from 'naive-ui';

const eventStore = useEventStore();

// 计算属性，筛选出“进行中”的展会
const ongoingEvents = computed(() => {
  return eventStore.events.filter(event => event.status === '进行中');
});

// 组件加载时，获取所有展会数据
onMounted(() => {
  eventStore.fetchEvents();
});
</script>

<style scoped>
.portal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  box-sizing: border-box;
}
.portal-box {
  width: 100%;
  max-width: 600px;
  background-color: var(--card-bg-color);
  border-radius: 8px;
  padding: 2rem 3rem;
  border: 1px solid var(--border-color);
  text-align: center;
}
header h1 {
  color: var(--accent-color);
  margin-top: 0;
}
header p {
  color: #aaa;
  margin-bottom: 2rem;
}
.event-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.event-link-card {
  display: block;
  text-decoration: none;
  color: var(--primary-text-color);
}
.event-link-card h2 {
  margin: 0 0 0.5rem 0;
}
.event-link-card span {
  color: #aaa;
}
.no-events p {
  line-height: 1.6;
}
</style>