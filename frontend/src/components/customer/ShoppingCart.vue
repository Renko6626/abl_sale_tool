<template>
  <div 
    class="shopping-cart"
    :class="{ 'mobile-collapsed': isMobile && !expanded, 'mobile-expanded': isMobile && expanded }"
  >
    <!-- 手机端底部栏 -->
    <div v-if="isMobile" class="cart-mobile-bar" @click="toggleCart">
      <span>🛒 我的订单</span>
      <span class="cart-mobile-total">¥{{ total.toFixed(2) }}</span>
      <span class="cart-mobile-arrow">{{ expanded ? '▼' : '▲' }}</span>
    </div>
    <!-- 只有展开时才显示详细内容 -->
    <div v-show="!isMobile || expanded" class="cart-content">
      <h3 class="cart-title">我的订单</h3>
      <div class="cart-list-wrapper">
        <ul v-if="cart.length" class="cart-list">
          <li v-for="item in cart" :key="item.id" class="cart-item">
            <div class="item-info">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-price">¥{{ item.price.toFixed(2) }}</span>
            </div>
            <div class="item-controls">
              <n-button circle tertiary @click="$emit('removeFromCart', item.id)">-</n-button>
              <span class="item-quantity">{{ item.quantity }}</span>
              <n-button circle tertiary @click="$emit('addToCart', item)">+</n-button>
            </div>
          </li>
        </ul>
        <p v-else class="empty-cart">
          <span>🛒</span>
          请点击左侧商品添加到这里
        </p>
      </div>
      <div class="cart-summary">
        <div class="total">
          <span>总计:</span>
          <strong class="total-amount">¥{{ total.toFixed(2) }}</strong>
        </div>
        <n-button 
          type="primary"
          block
          :disabled="!cart.length || isCheckingOut"
          :loading="isCheckingOut"
          @click="$emit('checkout')"
        >
          {{ isCheckingOut ? '下单中...' : '确认下单' }}
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { NButton } from 'naive-ui';

const props = defineProps({
  cart: { type: Array, required: true },
  total: { type: Number, required: true },
  isCheckingOut: { type: Boolean, default: false }
});
defineEmits(['addToCart', 'removeFromCart', 'checkout']);

const isMobile = ref(false);
const expanded = ref(false);

function checkMobile() {
  isMobile.value = window.innerWidth <= 600;
  if (!isMobile.value) expanded.value = false;
}
function toggleCart() {
  expanded.value = !expanded.value;
}

onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});
</script>

<style scoped>
.shopping-cart {
  display: flex;
  flex-direction: column;
  height: 100%; /* 占满父容器 cart-panel 的高度 */
}

.cart-title {
  font-size: 2rem;
  color: var(--accent-color);
  text-align: center;
  margin-top: 0;
  margin-bottom: 2rem;
  flex-shrink: 0; /* 防止标题被压缩 */
}

.cart-list-wrapper {
  flex-grow: 1; /* 占据所有可用垂直空间 */
  overflow-y: auto; /* 当列表过长时，允许独立滚动 */
}

.cart-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-name {
  font-size: 1.2rem;
  font-weight: 600;
}

.item-price {
  font-size: 1rem;
  color: #aaa;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.control-btn {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--accent-color);
  width: 40px;
  height: 40px;
  border-radius: 50%; /* 圆形按钮 */
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.item-quantity {
  font-size: 1.5rem;
  font-weight: bold;
  min-width: 30px; /* 保证宽度，防止数字变化时布局跳动 */
  text-align: center;
}

.empty-cart {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
  font-size: 1.2rem;
}
.empty-cart span {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.cart-summary {
  flex-shrink: 0; /* 防止总结部分被压缩 */
  margin-top: auto; /* 将其推到底部 */
  padding-top: 2rem;
  border-top: 2px solid var(--border-color);
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.total-amount {
  font-size: 2.2rem;
  font-weight: bold;
  color: var(--accent-color);
}

/* checkout 按钮改为 n-button，移除原样式 */
.shopping-cart {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--card-bg-color);
  transition: box-shadow 0.2s, transform 0.2s;
}

/* 手机端底部悬浮栏 */
.cart-mobile-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.2rem;
  background: var(--accent-color);
  color: #fff;
  font-size: 1.2rem;
  font-weight: bold;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.12);
  position: relative;
  z-index: 10;
}
.cart-mobile-total {
  margin-left: auto;
  margin-right: 1rem;
}
.cart-mobile-arrow {
  font-size: 1.2rem;
}

.cart-content {
  background: var(--card-bg-color);
}

/* 响应式：手机端底部抽屉效果 */
@media (max-width: 600px) {
  .shopping-cart {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    max-width: 100vw;
    z-index: 1201;
    box-shadow: 0 -2px 16px rgba(0,0,0,0.18);
    border-radius: 12px 12px 0 0;
    transition: transform 0.25s cubic-bezier(.4,2,.6,1), box-shadow 0.2s;
    height: auto;
  }
  .shopping-cart.mobile-collapsed .cart-content {
    display: none;
  }
  .shopping-cart.mobile-expanded {
    /* 展开时高度自适应内容 */
    max-height: 80vh;
    overflow-y: auto;
  }
  .shopping-cart.mobile-collapsed {
    max-height: 64px; /* 只显示底部栏 */
    overflow: hidden;
  }
  .cart-title {
    display: none; /* 手机端不显示大标题 */
  }
  .cart-summary {
    padding-bottom: 1rem;
  }
  .cart-panel {
    display: none ;
    width: 0 ;
    min-width: 0 ;
    max-width: 0 ;
    padding: 0 ;
    margin: 0 ;
  }
}
</style>