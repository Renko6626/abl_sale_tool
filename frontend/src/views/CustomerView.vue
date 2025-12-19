<template>
  <div class="customer-view">
    <div class="sidebar">
      <n-scrollbar style="max-height: 100vh;">
        <n-space vertical class="category-list">
          <n-button
            class="category-btn"
            :type="selectedCategory === '' ? 'primary' : 'default'"
            :tertiary="selectedCategory !== ''"
            block
            @click="selectedCategory = ''"
          >全部分类</n-button>
          <n-button
            v-for="cat in categoryOptions"
            :key="cat"
            class="category-btn"
            :type="selectedCategory === cat ? 'primary' : 'default'"
            :tertiary="selectedCategory !== cat"
            block
            @click="selectedCategory = cat"
          >{{ cat }}</n-button>
        </n-space>
      </n-scrollbar>
    </div>
    <div class="product-panel">
      <div class="card-size-toolbar">
        <n-button-group>
          <n-button :type="cardSize === 'small' ? 'primary' : 'default'" quaternary @click="cardSize = 'small'">小</n-button>
          <n-button :type="cardSize === 'medium' ? 'primary' : 'default'" quaternary @click="cardSize = 'medium'">中</n-button>
          <n-button :type="cardSize === 'large' ? 'primary' : 'default'" quaternary @click="cardSize = 'large'">大</n-button>
        </n-button-group>
      </div>
      <n-spin :show="store.isLoading">
        <ProductGrid 
          v-if="!store.isLoading"
          :products="filteredProducts" 
          :card-size="cardSize"
          @add-to-cart="store.addToCart"
        />
      </n-spin>
    </div>
    <div class="cart-panel" v-if="!isMobile">
      <n-card size="small" embedded>
        <ShoppingCart 
          :cart="store.cart"
          :total="store.cartTotal"
          :is-checking-out="isCheckingOut"
          @add-to-cart="store.addToCart"
          @remove-from-cart="store.removeFromCart"
          @checkout="handleCheckout"
        />
      </n-card>
    </div>
    <!-- 手机端底部悬浮购物车 -->
    <ShoppingCart 
      v-if="isMobile"
      :cart="store.cart"
      :total="store.cartTotal"
      :is-checking-out="isCheckingOut"
      @add-to-cart="store.addToCart"
      @remove-from-cart="store.removeFromCart"
      @checkout="handleCheckout"
    />
    <PaymentModal 
      :show="showPaymentModal" 
      :total="orderTotal"
      :qr-code-url="store.qrCodeUrl"
      @close="closePaymentModal"
    />
  </div>
</template>

<script setup>
import { useAlert } from '@/services/useAlert';

// 获取弹窗函数


import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useCustomerStore } from '@/stores/customerStore';
import { socket } from '@/services/socketService';
import ProductGrid from '@/components/customer/ProductGrid.vue';
import ShoppingCart from '@/components/customer/ShoppingCart.vue';
import PaymentModal from '@/components/customer/PaymentModal.vue';
import { NButton, NButtonGroup, NSpace, NScrollbar, NCard, NSpin } from 'naive-ui';

// 【核心改动】通过 props 接收来自路由的展会 ID
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
});

const store = useCustomerStore();
const showPaymentModal = ref(false);
const orderTotal = ref(0);
const isCheckingOut = ref(false); 
const selectedCategory = ref('');
const cardSize = ref('medium'); // 默认中等大小
const categoryOptions = computed(() => {
  const cats = (store.products || [])
    .map(p => p.category)
    .filter(cat => !!cat && cat.trim() !== '');
  return [...new Set(cats)];
});
const filteredProducts = computed(() => {
  let list = store.products || [];
  if (selectedCategory.value) {
    list = list.filter(p => p.category === selectedCategory.value);
  }
  // 你可以在这里加搜索过滤
  return list;
});
async function handleCheckout() {
  const { showAlert, showSuccess, showError } = useAlert();
  if (isCheckingOut.value) return; // 防止重复提交

  isCheckingOut.value = true;
  try {
    const newOrder = await store.submitOrder();
    if (newOrder) {
      orderTotal.value = store.cartTotal;
      showPaymentModal.value = true;
      showSuccess('订单已成功提交！');
      store.clearCart();
    }
  } catch (error) {
    console.log(error)
    
    showError(error.message);;
  } finally {
    isCheckingOut.value = false; // 无论成功失败，都解除禁用
  }
}
function closePaymentModal() {
  showPaymentModal.value = false;
}

onMounted(() => {
  store.setupStoreForEvent(props.id);;
});


function checkMobileCardSize() {
  if (window.innerWidth <= 600) {
    cardSize.value = 'small';
  }
}
const isMobile = ref(window.innerWidth <= 600);
function checkMobile() {
  isMobile.value = window.innerWidth <= 600;
}
onMounted(() => {
  checkMobile();
  checkMobileCardSize();
  window.addEventListener('resize', checkMobileCardSize);
});
onUnmounted(() => {
  window.removeEventListener('resize', checkMobileCardSize);
});
</script>

<style scoped>
.sidebar {
  flex: 0 0 100px; /* 固定宽度 */
  padding: 1rem 1rem 1rem 1rem;
  background: var(--card-bg-color);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
}
.category-select {
  margin-bottom: 1rem;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--card-bg-color);
  color: var(--primary-text-color);
  min-width: 120px;
}
.customer-view {
  display: flex;
  height: 100vh;
  background-color: var(--bg-color); /* 确保背景色统一 */
}

.product-panel {
  flex: 3; /* 占据约 3/4 宽度 */
  padding: 2rem;
  overflow-y: auto; /* 当商品过多时，允许此区域独立滚动 */
}

.cart-panel {
  flex: 1; /* 占据约 1/4 宽度 */
  padding: 2rem;
  background-color: var(--card-bg-color);
  border-left: 1px solid var(--border-color);
  display: flex; /* 让购物车内容能更好地布局 */
  flex-direction: column;
  height: 100vh; /* 确保侧边栏与视口等高 */
  box-sizing: border-box; /* 防止 padding 导致溢出 */
  overflow-x:hidden; /* 防止横向滚动 */
  overflow-y: auto;
}
.category-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.75rem 1rem;
  color: var(--primary-text-color);
  text-align: left;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  font-size: 1rem;
}

.category-btn.active,
.category-btn:hover {
  background: var(--accent-color);
  color: #fff;
  border-color: var(--accent-color);
}
.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto; /* 当分类过多时，允许滚动 */
}
.card-size-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.card-size-toolbar button {
  background: none;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  padding: 0.5rem 1.2rem;
  color: var(--primary-text-color);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: 
    background 0.2s, 
    color 0.2s, 
    border-color 0.2s, 
    box-shadow 0.2s;
  outline: none;
}

.card-size-toolbar button.active,
.card-size-toolbar button:focus {
  background: var(--accent-color);
  color: #fff;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(3,218,198,0.2);
}

.card-size-toolbar button:hover:not(.active) {
  background: var(--card-bg-color);
  border-color: var(--accent-color);
  color: var(--accent-color);
}
/* 保持桌面端原样 */

@media (max-width: 600px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 48px;              /* 更窄，只占很小空间 */
    max-width: 64px;
    min-width: 44px;
    height: 100vh;
    z-index: 1200;
    background: var(--card-bg-color);
    border-right: 1px solid var(--border-color);
    box-shadow: 2px 0 12px rgba(0,0,0,0.08);
    padding: 0.5rem 0.2rem 0.5rem 0.2rem;
    overflow-y: auto;
    flex: none;
    align-items: center;
  }
  .category-list {
    gap: 0.1rem;
    align-items: center;
    padding: 0;
  }
  .category-btn {
    width: 48px;
    min-width: 40px;
    max-width: 48px;
    padding: 0.2rem 0;
    margin: 0;
    font-size: 0.75rem;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    border-radius: 6px;
  }
  .product-panel {
    padding: 0 !important;
    margin-left: 48px; /* 与.sidebar宽度一致，避免被遮挡 */
    width: calc(100vw - 48px);
    min-width: 0;
    max-width: 100vw;
    box-sizing: border-box;
  }
  .cart-panel {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  .product-panel {
    flex: 1 1 0%;
    width: 100vw !important;
    max-width: 100vw !important;
    margin-right: 0 !important;
    padding-right: 0 !important;
  }
}
</style>