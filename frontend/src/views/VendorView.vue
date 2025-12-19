<template>
  <div class="vendor-view">
    <header class="page-header">
      <div class="header-content">
        
        <h1>待处理订单</h1>
        <p v-if="eventName">当前展会: <strong>{{ eventName }}</strong></p>
        <p v-else>正在加载展会信息...</p>
      </div>
      <!-- 这个按钮现在是主要的交互方式，而不是下拉菜单 -->
      <button class="btn btn-refresh" @click="manualRefresh" :disabled="isRefreshing">
        {{ isRefreshing ? '刷新中...' : '手动刷新' }}
      </button>
    </header>

    <main class="order-feed-container">
      <LiveStats class="live-stats-module" :event-id="props.id" />
      <n-alert v-if="store.pendingOrders.length" type="warning" :bordered="false" style="margin-bottom: 1rem;">
        有 {{ store.pendingOrders.length }} 条待处理订单，请及时处理。
      </n-alert>
      <div class="order-tabs">
        <n-tabs v-model:value="currentTab" type="line">
          <n-tab-pane :label="'待处理 (' + store.pendingOrders.length + ')'" name="pending" />
          <n-tab-pane label="已完成" name="completed" />
        </n-tabs>
      </div>

      <!-- 待处理订单列表 -->
      <div v-show="currentTab === 'pending'" class="order-feed">
        <div v-if="!store.pendingOrders.length" class="no-orders-message">
          暂无待处理订单
        </div>
        <TransitionGroup name="list" tag="div">
          <OrderCard 
            v-for="order in store.pendingOrders" 
            :key="order.id"
            :order="order"
            @complete="completeOrder"
            @cancel="cancelOrder"
          />
        </TransitionGroup>
      </div>

      <!-- 已完成订单列表 -->
      <div v-show="currentTab === 'completed'" class="order-feed">
         <p class="revenue-summary">
            今日已完成订单总额: <strong>¥{{ store.totalRevenue.toFixed(2) }}</strong>
         </p>
         <div v-if="!store.completedOrders.length" class="no-orders-message">
            暂无已完成订单
         </div>
         <OrderCard 
            v-for="order in store.completedOrders" 
            :key="order.id"
            :order="order"
            :is-completed="true"
         />
      </div>
    </main>
    <audio ref="audioRef" src="/assets/notify.wav" preload="auto"></audio>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { NButton, NTabs, NTabPane, NAlert, useDialog, useMessage } from 'naive-ui';
// ...existing imports...

import { useOrderStore } from '@/stores/orderStore';
import { useEventStore } from '@/stores/eventStore';
// 【步骤 1】导入 LiveStats 组件和它需要的 store
import { useEventDetailStore } from '@/stores/eventDetailStore'; 
import LiveStats from '@/components/vendor/LiveStats.vue';
import OrderCard from '@/components/order/OrderCard.vue';

const audioRef = ref(null);
const lastPendingCount = ref(0);


const props = defineProps({
  id: { type: String, required: true }
});

const store = useOrderStore();
const eventStore = useEventStore();
// 【步骤 2】实例化 eventDetailStore
const eventDetailStore = useEventDetailStore();

const isRefreshing = ref(false);
const currentTab = ref('pending');
const dialog = useDialog();
const message = useMessage();

const eventName = computed(() => {
  const event = eventStore.events.find(e => e.id === parseInt(props.id, 10));
  return event ? event.name : `展会 #${props.id}`;
});

async function manualRefresh() {
  isRefreshing.value = true;
  await Promise.all([
    store.pollPendingOrders(),
    eventDetailStore.fetchProductsForEvent(props.id),
    store.fetchCompletedOrders(),
  ]);
  isRefreshing.value = false;
}

async function completeOrder(orderId) {
  try {
    await store.markOrderAsCompleted(orderId);
    await eventDetailStore.fetchProductsForEvent(props.id);
    await store.fetchCompletedOrders();
    message.success('订单已完成配货');
  } catch (error) {
    message.error(error?.message || '操作失败');
  }
}

async function cancelOrder(orderId) {
  dialog.warning({
    title: '确认取消',
    content: '确定要取消这个订单吗？此操作无法撤销。',
    positiveText: '确认',
    negativeText: '返回',
    async onPositiveClick() {
      try {
        await store.cancelOrder(orderId);
        message.success('订单已取消');
      } catch (error) {
        message.error(error?.message || '取消失败');
      }
    }
  });
}

watch(currentTab, (val) => {
  if (val === 'completed') {
    store.fetchCompletedOrders();
  }
});

onMounted(() => {
  if (eventStore.events.length === 0) {
    eventStore.fetchEvents();
  }
  store.setActiveEvent(props.id);
  eventDetailStore.fetchProductsForEvent(props.id);
  lastPendingCount.value = store.pendingOrders.length;
});

watch(
  () => store.pendingOrders.length,
  (newCount, oldCount) => {
    if (newCount > oldCount && audioRef.value) {
      audioRef.value.currentTime = 0;
      audioRef.value.play();
    }
    lastPendingCount.value = newCount;
  }
);
onUnmounted(() => {
  store.stopPolling();
});
</script>

<style scoped>
.vendor-view {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}
.page-header h1 { margin: 0; color: var(--accent-color); }
.page-header p { margin: 0.25rem 0 0; color: #aaa; }

.order-tabs {
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
}

.no-orders-message {
  text-align: center;
  padding: 3rem;
  color: #888;
}

.revenue-summary {
  text-align: right;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

/* 列表过渡动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>