<template>
  <div>
    <header class="page-header">
      <h1>订单管理</h1>
      <p>查看并管理当前展会的所有订单记录。</p>
    </header>

    <main>
      <div class="filters">
        <label for="status-filter">筛选状态:</label>
        <n-select
          id="status-filter"
          v-model:value="statusFilter"
          :options="statusOptions"
          size="small"
          style="min-width: 200px;"
        />
      </div>

      <div v-if="store.isLoading" class="loading-message">
        <n-spin size="large">
          <template #description>正在加载订单...</template>
        </n-spin>
      </div>
      <div v-else-if="store.error" class="error-message">
        <n-alert type="error" :bordered="false">{{ store.error }}</n-alert>
      </div>
      
      <n-card v-else-if="filteredOrders.length" size="small">
        <n-table class="order-table" size="small">
          <thead>
            <tr>
              <th>订单ID</th>
              <th>下单时间</th>
              <th>商品详情</th>
              <th>总金额</th>
              <th class="column-status">状态</th>
              <th class="column-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td><strong>#{{ order.id }}</strong></td>
              <td>{{ new Date(order.timestamp).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }) }}</td>
              <td>
                <ul class="item-list">
                  <li v-for="item in order.items" :key="item.id">
                    {{ item.product_name }} x {{ item.quantity }}
                  </li>
                </ul>
              </td>
              <td><strong>¥{{ order.total_amount.toFixed(2) }}</strong></td>
              <td>
                <n-tag :type="tagType(order.status)" size="large" round>{{ statusText(order.status) }}</n-tag>
              </td>
              <td>
                <n-dropdown :options="actionOptions(order.status)" @select="key => changeStatus(order.id, key)">
                  <n-button size="large">操作</n-button>
                </n-dropdown>
              </td>
            </tr>
          </tbody>
        </n-table>
      </n-card>
      <p v-else>没有找到符合条件的订单。</p>
    </main>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useEventDetailStore } from '@/stores/eventDetailStore';
import { NSelect, NSpin, NAlert, NTable, NCard, NTag, NDropdown, NButton, useDialog, useMessage } from 'naive-ui';
const props = defineProps({
  id: { type: String, required: true }
});

const store = useEventDetailStore();
const statusFilter = ref('all'); // 筛选器的状态
const dialog = useDialog();
const message = useMessage();
const statusOptions = [
  { label: '所有订单', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
];

// 计算属性，根据筛选器动态过滤订单
const filteredOrders = computed(() => {
  if (statusFilter.value === 'all') {
    return store.allOrders;
  }
  return store.allOrders.filter(order => order.status === statusFilter.value);
});

function changeStatus(orderId, newStatus) {
  if (!newStatus) return;
  dialog.warning({
    title: '确认操作',
    content: `确定要将订单 #${orderId} 的状态修改为 "${statusText(newStatus)}" 吗？`,
    positiveText: '确认',
    negativeText: '取消',
    async onPositiveClick() {
      try {
        await store.adminUpdateOrderStatus(props.id, orderId, newStatus);
        message.success('状态已更新');
      } catch (error) {
        message.error(error.message || '更新失败');
      }
    }
  });
}

// --- 辅助函数 ---
function statusText(status) {
  const map = { pending: '待处理', completed: '已完成', cancelled: '已取消' };
  return map[status] || status;
}
function tagType(status) {
  if (status === 'pending') return 'warning';
  if (status === 'completed') return 'success';
  if (status === 'cancelled') return 'default';
  return 'default';
}

function actionOptions(status) {
  const opts = [];
  if (status !== 'pending') opts.push({ label: '设为待处理', key: 'pending' });
  if (status !== 'completed') opts.push({ label: '设为已完成', key: 'completed' });
  if (status !== 'cancelled') opts.push({ label: '设为已取消', key: 'cancelled' });
  return opts;
}

// --- 生命周期 ---
onMounted(() => {
  store.fetchAllOrdersForEvent(props.id);
});
onUnmounted(() => {
  store.resetStore(); // 离开时重置store
});
</script>

<style scoped>
.page-header {
  position: relative;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}
.page-header h1 { color: var(--accent-color); margin: 0; }
.page-header p { color: #aaa; margin-top: 0.5rem; }
.btn-back {
  position: absolute;
  top: 0;
  right: 0;
}

.form-container {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.add-product-form {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.add-product-form input[type="text"],
.add-product-form input[type="number"] {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  padding: 10px;
  border-radius: 4px;
  box-sizing: border-box;
  height: 42px;
}

/* --- 表格样式 --- */
.order-table {
  width: 100%;
  margin-top: 2rem;
  border-collapse: collapse;
  border-spacing: 0;
  text-align: left;
  font-size: 0.95rem;
}
.order-table th {
  padding: 12px 16px;
  background-color: var(--card-bg-color);
  color: var(--primary-text-color);
  font-weight: 600;
  border-bottom: 2px solid var(--accent-color);
}
.order-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  color: #ccc;
  vertical-align: middle;
}
.order-table tbody tr:hover {
  background-color: rgba(3, 218, 198, 0.05);
}
.order-table th:first-child, .order-table td:first-child { padding-left: 0; }
.order-table th:last-child, .order-table td:last-child { text-align: right; padding-right: 0; }

.column-preview { width: 80px; }

.preview-img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  vertical-align: middle;
}
.no-img {
  display: inline-block;
  width: 50px;
  height: 50px;
  line-height: 50px;
  text-align: center;
  font-size: 0.8rem;
  color: #888;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  vertical-align: middle;
}

.loading-message, .error-message {
  padding: 1rem;
  text-align: center;
}
.error-message { color: var(--error-color); }

.edit-form .form-group { margin-bottom: 1rem; }
.edit-form label { display: block; margin-bottom: 0.5rem; }
.edit-form input {
  width: 100%;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  padding: 10px;
  border-radius: 4px;
  box-sizing: border-box;
}

.btn-primary {
  background-color: var(--accent-color);
  color: var(--bg-color);
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn {
  background: none;
  border: 1px solid transparent; /* 默认透明边框 */
  color: var(--primary-text-color);
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  display: inline-flex; /* 让图标和文字对齐 */
  align-items: center;
  gap: 0.4rem; /* 图标和文字的间距 */
  white-space: nowrap; /* 防止文字换行 */
}

.action-btn:hover {
  background-color: var(--card-bg-color);
  border-color: var(--border-color);
}

/* 危险操作按钮的特定样式 */
.action-btn.btn-danger {
  color: var(--error-color);
}

.action-btn.btn-danger:hover {
  background-color: rgba(244, 67, 54, 0.1); /* 淡红色背景 */
  border-color: rgba(244, 67, 54, 0.4);
}
.filters {
  margin-bottom: 1.5rem;
}

/* --- 筛选器样式 (复用 VendorView 的样式) --- */
.filters {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
/* 文字大小要保证能排开一行 */
.filters label {
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap; /* 防止中文自动换行 */
  flex-shrink: 0;      /* 在 flex 布局中不缩小导致换行 */
}
.custom-select-wrapper {
  position: relative;
  display: inline-block;
  min-width: 200px;
}
.custom-select-wrapper::after {
  content: '▼';
  font-size: 0.8rem;
  color: var(--accent-color);
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}
.custom-select-wrapper select {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  padding: 8px 30px 8px 12px;
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--primary-text-color);
  cursor: pointer;
}

/* --- 状态徽章的全新样式 --- */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
}
.status-badge.status-pending {
  background-color: rgba(251, 140, 0, 0.15); /* 橙色 */
  color: #FB8C00;
}
.status-badge.status-completed {
  background-color: rgba(3, 218, 198, 0.15); /* 青色/主题色 */
  color: var(--accent-color);
}
.status-badge.status-cancelled {
  background-color: rgba(158, 158, 158, 0.15); /* 灰色 */
  color: #9E9E9E;
}

/* --- 操作菜单的全新样式 --- */
.action-menu {
  position: relative;
  display: inline-block;
  text-align: left;
}
.action-btn { /* 这是触发按钮 */
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 6px 12px;
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  color: var(--primary-text-color);
}
.action-btn:hover {
  background-color: var(--bg-color);
  border-color: var(--accent-color);
}

.menu-items {
  position: absolute;
  right: 0;
  margin-top: 0.5rem;
  width: 150px;
  origin-top-right: 0; /* 动画基点 */
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  z-index: 10;
  overflow: hidden; /* 保证内部元素的圆角 */
}

.menu-items button {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  text-align: left;
  background: none;
  border: none;
  color: var(--primary-text-color);
  cursor: pointer;
}
.menu-items button.active,
.menu-items button:hover {
  background-color: var(--accent-color);
  color: var(--bg-color);
}

</style>