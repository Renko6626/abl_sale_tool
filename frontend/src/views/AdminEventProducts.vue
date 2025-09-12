<template>
  <div>
    <header class="page-header">
      <h1>商品管理</h1>
      <p>为当前展会添加、修改和移除上架商品。</p>
      <RouterLink to="/admin" class="btn btn-back">&larr; 返回展会列表</RouterLink>
    </header>

    <main>
      <!-- 上架商品表单 -->
      <div class="form-container">
        <h3>通过编号上架商品</h3>
        <form @submit.prevent="handleAddProduct" class="add-product-form">
          <input v-model="addProductData.product_code" type="text" placeholder="商品编号 (例如 A01)" required>
          <input v-model.number="addProductData.initial_stock" type="number" placeholder="初始库存" required>
          <input v-model.number="addProductData.price" type="number" step="0.01" placeholder="展会售价 (可选)">
          <button type="submit" class="btn" :disabled="isAdding">
            {{ isAdding ? '上架中...' : '上架' }}
          </button>
        </form>
        <p v-if="addError" class="error-message">{{ addError }}</p>
      </div>

      <!-- 当前展会的商品列表 -->
      <div v-if="store.isLoading" class="loading-message">正在加载商品列表...</div>
      <div v-else-if="store.error" class="error-message">{{ store.error }}</div>
      <table v-else-if="store.products.length" class="product-table">
        <thead>
          <tr>
            <th class="column-preview">预览</th>
            <th>编号</th>
            <th>名称</th>
            <th>展会售价</th>
            <th>初始库存</th>
            <th>当前库存</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in store.products" :key="product.id">
            <td>
              <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="preview-img">
              <span v-else class="no-img">无图</span>
            </td>
            <td>{{ product.product_code }}</td>
            <td>{{ product.name }}</td>
            <td>¥{{ product.price.toFixed(2) }}</td>
            <td>{{ product.initial_stock }}</td>
            <td>{{ product.current_stock }}</td>
            <td>
                <button class="action-btn" @click="openEditModal(product)">编辑</button>
                <!-- 【新增】删除按钮 -->
                <button class="action-btn btn-danger" @click="handleDelete(product)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>该展会还未上架任何商品。</p>
    </main>

    <!-- 编辑商品模态框 -->
    <AppModal :show="isEditModalVisible" @close="closeEditModal">
      <template #header><h3>编辑上架商品</h3></template>
      <template #body>
        <form v-if="editableProduct" class="edit-form" @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>展会售价 (¥):</label>
            <input v-model.number="editableProduct.price" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>初始库存:</label>
            <input v-model.number="editableProduct.initial_stock" type="number" required>
          </div>
          <p v-if="editError" class="error-message">{{ editError }}</p>
        </form>
      </template>
      <template #footer>
        <button type="button" class="btn" @click="closeEditModal">取消</button>
        <button type="button" class="btn btn-primary" @click="handleUpdate" :disabled="isUpdating">
            {{ isUpdating ? '保存中...' : '保存更改' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { RouterLink } from 'vue-router';
import { useEventDetailStore } from '@/stores/eventDetailStore';
import AppModal from '@/components/shared/AppModal.vue';

// 接收来自路由的 id 参数
const props = defineProps({
  id: {
    type: String,
    required: true,
  }
});

const store = useEventDetailStore();
// 定义后端 URL 以便正确加载图片, 请确保这里的地址和端口正确
const backendUrl = 'http://127.0.0.1:5000';

// --- 添加逻辑 ---
const isAdding = ref(false);
const addError = ref('');
const addProductData = ref({
  product_code: '',
  initial_stock: null,
  price: null,
});

async function handleAddProduct() {
  isAdding.value = true;
  addError.value = '';
  try {
    const dataToSend = { ...addProductData.value };
    if (dataToSend.price === null || dataToSend.price === '') {
      delete dataToSend.price;
    }
    await store.addProductToEvent(props.id, dataToSend);
    addProductData.value = { product_code: '', initial_stock: null, price: null };
  } catch (error) {
    addError.value = error.message;
  } finally {
    isAdding.value = false;
  }
}

// --- 编辑逻辑 ---
const isEditModalVisible = ref(false);
const isUpdating = ref(false);
const editError = ref('');
const editableProduct = ref(null);

function openEditModal(product) {
  editableProduct.value = { ...product }; // 创建副本
  isEditModalVisible.value = true;
}

function closeEditModal() {
  isEditModalVisible.value = false;
  editError.value = '';
}

async function handleUpdate() {
  if (!editableProduct.value) return;
  isUpdating.value = true;
  editError.value = '';
  try {
    const { id, price, initial_stock } = editableProduct.value;
    await store.updateEventProduct(id, { price, initial_stock });
    closeEditModal();
  } catch (error) {
    editError.value = error.message;
  } finally {
    isUpdating.value = false;
  }
}

// --- 删除逻辑 ---
async function handleDelete(product) {
  if (window.confirm(`确定要从该展会下架 "${product.name}" 吗？`)) {
    try {
      await store.deleteEventProduct(product.id);
    } catch (error) {
      alert(error.message);
    }
  }
}

// --- 生命周期钩子 ---
onMounted(() => {
  store.fetchProductsForEvent(props.id);
});

onUnmounted(() => {
  store.resetStore();
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
.product-table {
  width: 100%;
  margin-top: 2rem;
  border-collapse: collapse;
  border-spacing: 0;
  text-align: left;
  font-size: 0.95rem;
}
.product-table th {
  padding: 12px 16px;
  background-color: var(--card-bg-color);
  color: var(--primary-text-color);
  font-weight: 600;
  border-bottom: 2px solid var(--accent-color);
}
.product-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  color: #ccc;
  vertical-align: middle;
}
.product-table tbody tr:hover {
  background-color: rgba(3, 218, 198, 0.05);
}
.product-table th:first-child, .product-table td:first-child { padding-left: 0; }
.product-table th:last-child, .product-table td:last-child { text-align: right; padding-right: 0; }

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
</style>