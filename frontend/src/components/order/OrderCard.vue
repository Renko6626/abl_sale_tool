<template>
  <div class="order-card">
    <div class="order-header">
      <h4>订单 #{{ order.id }}</h4>
      <span class="order-time">{{ formattedTime }} (UTC+8)</span>
    </div>
    
    <!-- 【核心改动】将 <ul> 改为 <div>，并修改内部结构 -->
    <div class="item-list">
      <div v-for="item in order.items" :key="item.id" class="order-item">
        <!-- 缩略图容器 -->
        <div class="item-thumbnail">
          <img v-if="item.product_image_url" :src="item.product_image_url" :alt="item.product_name" />
          <div v-else class="no-img-placeholder">?</div>
        </div>
        <!-- 商品信息 -->
        <div class="item-details">
          <span class="item-name">{{ item.product_name }}</span>
          <span class="item-price">¥{{ item.product_price.toFixed(2) }}</span>
        </div>
        <!-- 数量 -->
        <span class="item-quantity">x {{ item.quantity }}</span>
      </div>
    </div>

    <div class="order-footer">
      <span class="total-amount">总计: ¥{{ order.total_amount.toFixed(2) }}</span>
      <!-- 【修改】只有在待处理状态下才显示按钮 -->
      <div v-if="!isCompleted" class="button-group">
        <n-button tertiary type="error" size="small" @click="$emit('cancel', order.id)">取消</n-button>
        <n-button type="primary" size="small" @click="$emit('complete', order.id)">完成配货</n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { NButton } from 'naive-ui';

const props = defineProps({
  order: { type: Object, required: true },
  isCompleted: { type: Boolean, default: false }
});
defineEmits(['complete', 'cancel']);

// 【新增】定义后端 URL 以便正确加载图片
const backendUrl = 'http://127.0.0.1:5000';

const formattedTime = computed(() => {
  return new Date(props.order.timestamp).toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
});
</script>

<style scoped>
.order-card.is-completed {
  border-left-color: #555; /* 已完成的订单用灰色边框 */
  opacity: 0.8;
}
.button-group { display: flex; gap: 0.5rem; }
.btn-cancel { /* ... 危险操作的样式 ... */ }
/* --- 整体卡片样式 (保持或微调) --- */
.order-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent-color);
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

/* --- 订单头 --- */
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}
.order-header h4 { margin: 0; color: var(--primary-text-color); }
.order-header .order-time { font-size: 0.9rem; color: #aaa; }

/* --- 【新增/修改】商品列表样式 --- */
.item-list {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* 每个商品项之间的间距 */
  margin-bottom: 1rem;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 1rem; /* 图片、信息、数量之间的间距 */
}

.item-thumbnail {
  flex-shrink: 0; /* 防止图片被压缩 */
}

.item-thumbnail img, .no-img-placeholder {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.no-img-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #888;
  background-color: var(--bg-color);
}

.item-details {
  flex-grow: 1; /* 占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 600;
  color: #eee;
}

.item-price {
  font-size: 0.85rem;
  color: #aaa;
}

.item-quantity {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--accent-color);
}

/* --- 订单尾 --- */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}
.total-amount strong {
  font-size: 1.2rem;
  color: var(--accent-color);
}
/* 【新增】按钮组容器样式 */
.actions {
  display: flex;
  gap: 0.75rem; /* 按钮之间的间距 */
}

/* 【修改】通用按钮样式，确保 .btn 基础样式存在 */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  border: 1px solid;
  transition: background-color 0.2s, color 0.2s;
}

/* “完成”按钮样式 */
.btn-complete {
  background-color: var(--accent-color);
  color: var(--bg-color);
  border-color: var(--accent-color);
}

/* “取消”按钮样式 */
.btn-cancel {
  background-color: transparent;
  color: var(--error-color);
  border-color: var(--error-color);
}

.btn-cancel:hover {
  background-color: var(--error-color);
  color: white;
}
</style>