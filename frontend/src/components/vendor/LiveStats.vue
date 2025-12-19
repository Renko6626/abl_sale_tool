<template>
  <div class="stats-container">
    <div class="stats-header">
      <h3>实时销售统计</h3>
      <n-button tertiary size="small" class="collapse-btn" @click="collapsed=!collapsed">
        {{ collapsed ? '展开' : '收起' }}
      </n-button>
    </div>
    <div v-show="!collapsed">
      <n-space size="large">
        <n-card size="small" class="stat-card" :bordered="false">
          <span class="label">当前营业额</span>
          <span class="value revenue">¥{{ orderStore.totalRevenue.toFixed(2) }}</span>
        </n-card>
        <n-card size="small" class="stat-card" :bordered="false">
          <span class="label">待处理订单</span>
          <span class="value">{{ orderStore.pendingOrders.length }}</span>
        </n-card>
      </n-space>
      <h4>库存速览</h4>
      <div v-if="eventDetailStore.isLoading" class="loading">
        <n-spin size="small">
          <template #description>加载库存中...</template>
        </n-spin>
      </div>
      <div v-else class="stock-list">
        <div 
          v-for="product in eventDetailStore.products" 
          :key="product.id"
          class="stock-item"
        >
          <span class="product-name">{{ product.name }}</span>
          <n-progress type="line" :percentage="stockPercentage(product)" :show-indicator="false" />
          <span class="stock-value">
            {{ product.current_stock }} / {{ product.initial_stock }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useOrderStore } from '@/stores/orderStore';
import { onMounted, onUnmounted, ref } from 'vue';
import { NButton, NCard, NSpace, NSpin, NProgress } from 'naive-ui';
const props = defineProps({
  eventId: { type: String, required: true }
});
const collapsed = ref(false);
// 【重要】我们也需要 eventDetailStore 来获取商品列表和它们的 current_stock
import { useEventDetailStore } from '@/stores/eventDetailStore'; 

const orderStore = useOrderStore();
const eventDetailStore = useEventDetailStore();

function stockPercentage(product) {
  if (product.initial_stock === 0) return 0;
  return (product.current_stock / product.initial_stock) * 100;
}

let timer = null;
async function refreshStats() {
  await Promise.all([
    orderStore.fetchCompletedOrders?.(),
    eventDetailStore.fetchProductsForEvent?.(props.eventId)
  ]);
}
onMounted(() => {
  refreshStats();
  timer = setInterval(refreshStats, 5000); // 每5秒刷新一次
});
onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.stats-container {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}
.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}
.stats-summary {
  margin-bottom: 1.5rem;
}
.stat-card {
  background-color: var(--bg-color);
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}
.stat-card .label {
  display: block;
  font-size: 0.9rem;
  color: #aaa;
  margin-bottom: 0.5rem;
}
.stat-card .value {
  display: block;
  font-size: 1.8rem;
  font-weight: bold;
}
.stat-card .revenue {
  color: var(--accent-color);
}
h4 {
  margin-top: 2rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
}
.stock-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.stock-item {
  display: grid;
  grid-template-columns: 2.5fr 2fr 1fr; /* 加宽第一列 */
  align-items: center;
  gap: 1rem;
}

.product-name {
  white-space: normal;         /* 允许换行 */
  overflow: visible;           /* 不隐藏超出内容 */
  text-overflow: unset;        /* 不显示省略号 */
  word-break: break-all;       /* 必要时强制换行 */
}
.stock-value {
  text-align: right;
  font-family: monospace;
}
.collapse-btn {
  margin-left: 1rem;
  min-width: 56px;
}
</style>