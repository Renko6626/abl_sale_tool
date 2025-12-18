<template>
  <div class="filters">
    <div class="filter-group">
      <label for="product">制品过滤</label>
      <select id="product" :value="selectedProduct" @change="onProduct">
        <option value="">全部制品</option>
        <option v-for="product in productOptions" :key="product.code" :value="product.code">
          {{ product.name }} ({{ product.code }})
        </option>
      </select>
    </div>

    <div class="filter-group">
      <label for="start">开始日期</label>
      <input id="start" type="date" :value="startDate" @change="onStart" />
    </div>

    <div class="filter-group">
      <label for="end">结束日期</label>
      <input id="end" type="date" :value="endDate" @change="onEnd" />
    </div>

    <div class="filter-group">
      <label for="interval">时间粒度</label>
      <select id="interval" :value="intervalMinutes" @change="onInterval">
        <option :value="60">按小时</option>
        <option :value="30">按 30 分钟</option>
      </select>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  productOptions: { type: Array, default: () => [] },
  selectedProduct: { type: String, default: '' },
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
  intervalMinutes: { type: Number, default: 60 },
});

const emit = defineEmits([
  'update:selectedProduct',
  'update:startDate',
  'update:endDate',
  'update:intervalMinutes',
  'change',
]);

function onProduct(e) { emit('update:selectedProduct', e.target.value); emit('change'); }
function onStart(e) { emit('update:startDate', e.target.value); emit('change'); }
function onEnd(e) { emit('update:endDate', e.target.value); emit('change'); }
function onInterval(e) { emit('update:intervalMinutes', Number(e.target.value)); emit('change'); }
</script>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group label { color: var(--secondary-text-color); font-size: 0.9rem; }
.filter-group select,
.filter-group input[type="date"] {
  background: var(--card-bg-color);
  color: var(--primary-text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.65rem 0.75rem;
}
</style>