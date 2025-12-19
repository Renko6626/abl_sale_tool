<template>
  <div class="admin-event-stat">
    <header class="stat-header">
      <h1>{{ pageTitle }}</h1>
      <n-button
        v-if="statStore.stats && statStore.stats.summary.length > 0"
        tag="a"
        :href="statStore.downloadUrl"
        class="download-btn"
        type="primary"
        tertiary
        size="small"
        download
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        下载 Excel 报告
      </n-button>
    </header>

    <div v-if="statStore.isLoading" class="loading-indicator">
      <n-spin size="large">
        <template #description>正在从数据库中提取统计信息...</template>
      </n-spin>
    </div>

    <div v-else-if="statStore.error" class="error-message">
      <n-alert type="error" title="后端数据库寄了！" :bordered="false">
        {{ statStore.error }}
      </n-alert>
      <n-button @click="applyFilters" tertiary class="btn-secondary">重新建立连接</n-button>
    </div>

    <div v-else-if="statStore.stats" class="stats-content">
      <n-card size="small" embedded>
        <StatFilters
          :product-options="productOptions"
          :selected-product="selectedProduct"
          :start-date="startDate"
          :end-date="endDate"
          :interval-minutes="intervalMinutes"
          @update:selectedProduct="val => (selectedProduct = val)"
          @update:startDate="val => (startDate = val)"
          @update:endDate="val => (endDate = val)"
          @update:intervalMinutes="val => (intervalMinutes = val)"
          @change="applyFilters"
        />
      </n-card>

      <!-- 关键数据总览 -->
      <div class="summary-cards">
        <n-card class="card" size="small" embedded>
          <span class="label">总销售额</span>
          <span class="value">{{ formatCurrency(statStore.stats.total_revenue) }}</span>
        </n-card>
        <n-card class="card" size="small" embedded>
          <span class="label">总销售件数</span>
          <span class="value">{{ totalItemsSold }}</span>
        </n-card>
        <n-card class="card" size="small" embedded>
          <span class="label">销售品类数</span>
          <span class="value">{{ productVarietyCount }}</span>
        </n-card>
      </div>

      <!-- 销售趋势图 -->
      <n-card class="chart-card" size="small" embedded>
        <div class="chart-header">
          <h3>销售额趋势</h3>
          <span v-if="statStore.stats.timeseries?.length">{{ chartSubtitle }}</span>
        </div>
        <SalesLineChart
          v-if="statStore.stats.timeseries?.length"
          :series="statStore.stats.timeseries"
          :width="chartWidth"
          :height="chartHeight"
          :padding="padding"
        />
        <p v-else class="no-data">// 暂无趋势数据</p>
      </n-card>

      <!-- 销售详情表格 -->
      <n-card class="details-table-container" size="small" embedded>
        <h3>销售数据表</h3>
        <p v-if="!statStore.stats.summary.length" class="no-data">
          // 无有效销售数据记录...
        </p>
        <n-table v-else size="small">
          <thead>
            <tr>
              <th>制品编号</th>
              <th>制品名</th>
              <th class="text-right">单价</th>
              <th class="text-center">销售量</th>
              <th class="text-right">销售额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in statStore.stats.summary" :key="item.product_id">
              <td class="id-cell">#{{ item.product_code }}</td>
              <td>{{ item.product_name }}</td>
              <td class="text-right currency-cell">{{ formatCurrency(item.unit_price) }}</td>
              <td class="text-center quantity-cell">{{ item.total_quantity }}</td>
              <td class="text-right currency-cell">{{ formatCurrency(item.total_revenue_per_item) }}</td>
            </tr>
          </tbody>
        </n-table>
      </n-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch, computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useEventStatStore } from '@/stores/eventStatStore';
import SalesLineChart from '@/components/stats/SalesLineChart.vue';
import StatFilters from '@/components/stats/StatFilters.vue';
import { NButton, NSpin, NAlert, NCard, NTable } from 'naive-ui';

const route = useRoute();
const statStore = useEventStatStore();
const selectedProduct = ref('');
const startDate = ref('');
const endDate = ref('');
const intervalMinutes = ref(60);
const chartWidth = 800;
const chartHeight = 320;
const padding = 48;

const pageTitle = computed(() => statStore.stats?.event_name ? `${statStore.stats.event_name} - 数据统计` : '数据统计');
const totalItemsSold = computed(() => statStore.stats?.summary.reduce((sum, item) => sum + item.total_quantity, 0) || 0);
const productVarietyCount = computed(() => statStore.stats?.summary.length || 0);
const productOptions = computed(() => {
  const summary = statStore.stats?.summary || [];
  const unique = new Map();
  summary.forEach(item => {
    if (!unique.has(item.product_code)) {
      unique.set(item.product_code, { code: item.product_code, name: item.product_name });
    }
  });
  return Array.from(unique.values());
});


const chartSubtitle = computed(() => {
  const parts = [];
  if (selectedProduct.value) parts.push(`制品 ${selectedProduct.value}`);
  if (startDate.value) parts.push(`自 ${startDate.value}`);
  if (endDate.value) parts.push(`至 ${endDate.value}`);
  parts.push(intervalMinutes.value === 30 ? '每 30 分钟' : '每小时');
  return parts.join(' · ');
});


function formatCurrency(value) {
  if (typeof value !== 'number') return '¥ 0.00';
  return `¥ ${value.toFixed(2)}`;
}

// Chart implementation moved to SalesLineChart component

async function applyFilters() {
  await statStore.fetchStats({
    productCode: selectedProduct.value,
    startDate: startDate.value,
    endDate: endDate.value,
    intervalMinutes: intervalMinutes.value,
  });
}

onMounted(() => {
  const eventId = route.params.id;
  if (eventId) statStore.setActiveEvent(eventId, { productCode: selectedProduct.value, startDate: startDate.value, endDate: endDate.value, intervalMinutes: intervalMinutes.value });
});

watch(() => route.params.id, (newEventId) => {
  if (newEventId) statStore.setActiveEvent(newEventId, { productCode: selectedProduct.value, startDate: startDate.value, endDate: endDate.value, intervalMinutes: intervalMinutes.value });
});
</script>

<style scoped>
/* 假设你的主题色定义在 :root 或其他全局样式中 */
/* :root {
  --bg-color: #1a1a1a;
  --card-bg-color: #242424;
  --border-color: #3a3a3a;
  --primary-text-color: #e0e0e0;
  --secondary-text-color: #a0a0a0;
  --accent-color: #03dac6;
  --accent-color-dark: #018786;
} */

.admin-event-stat {
  padding: 2rem;
  color: var(--primary-text-color);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

h1 {
  font-size: 2rem;
  font-weight: 300; /* 更纤细的字体 */
  color: var(--accent-color);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin: 0;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease-in-out;
}

.download-btn {
  background-color: transparent;
  border-color: var(--accent-color);
  color: var(--accent-color);
}
.download-btn:hover {
  background-color: rgba(3, 218, 198, 0.1);
  box-shadow: 0 0 15px rgba(3, 218, 198, 0.3);
  transform: translateY(-2px);
}

.loading-indicator, .error-message {
  text-align: center;
  padding: 5rem 2rem;
  color: var(--secondary-text-color);
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  background-color: rgba(0,0,0,0.1);
}
.error-message p { margin: 0.5rem 0; }
.error-message strong { color: #ff5555; }
.btn-secondary { background-color: var(--card-bg-color); color: var(--primary-text-color); margin-top: 1rem;}
.btn-secondary:hover { border-color: var(--primary-text-color); }

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  color: var(--secondary-text-color);
  font-size: 0.9rem;
}

.filter-group select,
.filter-group input[type="date"] {
  background: var(--card-bg-color);
  color: var(--primary-text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.65rem 0.75rem;
}

.chart-card {
  background-color: var(--card-bg-color);
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 2rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
  color: var(--primary-text-color);
}

.chart-wrapper {
  width: 100%;
  overflow: hidden;
  position: relative;
}

svg {
  width: 100%;
  height: auto;
}

.line {
  fill: none;
  stroke: var(--accent-color);
  stroke-width: 2.5;
}

.area {
  fill: url(#revenueGradient);
  stroke: none;
}

.points circle {
  fill: var(--accent-color);
  stroke: var(--card-bg-color);
  stroke-width: 2;
}

.points text {
  fill: var(--primary-text-color);
  font-size: 0.75rem;
}

.grid-lines line {
  stroke: rgba(255,255,255,0.15);
  stroke-dasharray: 4 4;
  stroke-width: 1;
}

.y-ticks text {
  fill: var(--primary-text-color);
  font-size: 0.75rem;
}

.chart-tooltip {
  position: absolute;
  transform: translate(-50%, -120%);
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  pointer-events: none;
  white-space: nowrap;
  box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}

.tooltip-date {
  font-size: 0.8rem;
  margin-bottom: 0.2rem;
  color: var(--secondary-text-color);
}

.tooltip-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary-text-color);
}

.card {
  background-color: var(--card-bg-color);
  padding: 2rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--accent-color);
  opacity: 0.7;
}

.card .label {
  font-size: 1rem;
  color: var(--secondary-text-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
  display: block;
}

.card .value {
  font-size: 2.5rem;
  font-weight: 500;
  color: var(--primary-text-color);
  line-height: 1;
}

.details-table-container {
  background-color: var(--card-bg-color);
  padding: 2rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}
.details-table-container h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-weight: 400;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

thead th {
  color: var(--secondary-text-color);
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1px;
}

tbody tr {
  transition: background-color 0.2s;
}
tbody tr:hover {
  background-color: rgba(3, 218, 198, 0.05);
}
tbody td {
  color: var(--primary-text-color);
}
.id-cell {
  color: var(--secondary-text-color);
  font-family: 'Courier New', Courier, monospace;
}
.quantity-cell {
  font-weight: bold;
  font-size: 1.1rem;
}
.currency-cell {
  color: var(--accent-color);
  font-weight: 500;
}
.text-right { text-align: right; }
.text-center { text-align: center; }

.no-data {
  color: var(--secondary-text-color);
  padding: 3rem;
  text-align: center;
  font-family: 'Courier New', Courier, monospace;
}
</style>