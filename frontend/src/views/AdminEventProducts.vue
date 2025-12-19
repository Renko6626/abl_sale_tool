<template>
  <div>
    <header class="page-header">
      <h1>商品管理</h1>
      <p>为当前展会添加、修改和移除上架商品。</p>
      <RouterLink to="/admin" class="btn-back">
        <n-button quaternary size="small">&larr; 返回展会列表</n-button>
      </RouterLink>
    </header>

    <main>
      <n-card class="form-container" title="上架新商品" size="small">
        <div class="search-filters">
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索名称或编号..."
            clearable
            size="large"
            round
            class="search-input"
          />
          <n-select
            v-model:value="selectedCategory"
            :options="categoryOptionsForSelect"
            class="category-select"
            clearable
            size="small"
            placeholder="全部分类"
          />
        </div>

        <div class="product-preview-container">
          <div v-if="productStore.isLoading" class="loading-message">加载制品列表中...</div>
          <div v-else-if="productStore.error" class="error-message">{{ productStore.error }}</div>
          <ul v-else-if="filteredProducts.length" class="product-preview-list">
            <li
              v-for="product in filteredProducts"
              :key="product.id"
              class="preview-item"
              :class="{ selected: addProductData.product_code === product.product_code }"
              @click="selectProduct(product)"
            >
              <n-image :src="product.image_url" :alt="product.name" class="preview-item-img" preview-disabled />
              <div class="preview-item-info">
                <span class="preview-item-name">{{ product.name }}</span>
                <span class="preview-item-code">{{ product.product_code }}</span>
                <span v-if="product.default_price != null" class="preview-item-price">¥{{ Number(product.default_price).toFixed(2) }}</span>
              </div>
            </li>
          </ul>
          <p v-else class="no-results-message">未找到匹配的制品。</p>
        </div>

        <form @submit.prevent="handleAddProduct" class="add-product-form">
          <n-input v-model:value="addProductData.product_code" placeholder="商品编号 (可点击上方预览填充)" clearable required />
          <n-input-number v-model:value="addProductData.initial_stock" placeholder="初始库存" :min="0" required ref="stockInputRef" />
          <n-input-number v-model:value="addProductData.price" placeholder="展会售价 (可选)" :min="0" :step="0.01" />
          <n-button type="primary" attr-type="submit" :disabled="isAdding">
            {{ isAdding ? '上架中...' : '上架' }}
          </n-button>
        </form>
        <p v-if="addError" class="error-message">{{ addError }}</p>
      </n-card>

      <div v-if="eventDetailStore.isLoading" class="loading-message">正在加载商品列表...</div>
      <n-card v-else-if="eventDetailStore.products.length" size="small">
        <table class="product-table">
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
            <tr v-for="product in eventDetailStore.products" :key="product.id">
              <td>
                <n-image v-if="product.image_url" :src="product.image_url" :alt="product.name" class="preview-img" preview-disabled />
                <span v-else class="no-img">无图</span>
              </td>
              <td>{{ product.product_code }}</td>
              <td>{{ product.name }}</td>
              <td>¥{{ product.price.toFixed(2) }}</td>
              <td>{{ product.initial_stock }}</td>
              <td>{{ product.current_stock }}</td>
              <td>
                <n-space size="small" justify="end">
                  <n-button size="small" @click="openEditModal(product)">编辑</n-button>
                  <n-button size="small" type="error" quaternary @click="handleDelete(product)">删除</n-button>
                </n-space>
              </td>
            </tr>
          </tbody>
        </table>
      </n-card>
      <p v-else>该展会还未上架任何商品。</p>
    </main>

    <AppModal :show="isEditModalVisible" @close="closeEditModal">
      <template #header><h3>编辑上架商品</h3></template>
      <template #body>
        <form v-if="editableProduct" class="edit-form" @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>展会售价 (¥):</label>
            <n-input-number v-model:value="editableProduct.price" :min="0" :step="0.01" required />
          </div>
          <div class="form-group">
            <label>初始库存:</label>
            <n-input-number v-model:value="editableProduct.initial_stock" :min="0" required />
          </div>
          <p v-if="editError" class="error-message">{{ editError }}</p>
        </form>
      </template>
      <template #footer>
        <n-space>
          <n-button @click="closeEditModal">取消</n-button>
          <n-button type="primary" @click="handleUpdate" :disabled="isUpdating">
            {{ isUpdating ? '保存中...' : '保存更改' }}
          </n-button>
        </n-space>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { useEventDetailStore } from '@/stores/eventDetailStore';
import { useProductStore } from '@/stores/productStore';
import AppModal from '@/components/shared/AppModal.vue';
import { NCard, NInput, NSelect, NImage, NInputNumber, NButton, NSpace } from 'naive-ui';

const props = defineProps({ id: { type: String, required: true } });

const eventDetailStore = useEventDetailStore();
const productStore = useProductStore();

const searchQuery = ref('');
const stockInputRef = ref(null);
const selectedCategory = ref(null);

const categoryOptions = computed(() => {
  const cats = (productStore.masterProducts || [])
    .map(p => p.category)
    .filter(cat => !!cat && cat.trim() !== '');
  return [...new Set(cats)];
});

const categoryOptionsForSelect = computed(() =>
  categoryOptions.value.map(cat => ({ label: cat, value: cat }))
);

const filteredProducts = computed(() => {
  const existingProductCodes = new Set(eventDetailStore.products.map(p => p.product_code));

  let availableProducts = productStore.masterProducts
    .filter(masterProduct => !existingProductCodes.has(masterProduct.product_code));

  if (selectedCategory.value) {
    availableProducts = availableProducts.filter(p => p.category === selectedCategory.value);
  }

  if (searchQuery.value.trim()) {
    const lowerCaseQuery = searchQuery.value.toLowerCase();
    availableProducts = availableProducts.filter(product =>
      product.name.toLowerCase().includes(lowerCaseQuery) ||
      product.product_code.toLowerCase().includes(lowerCaseQuery)
    );
  }

  return availableProducts;
});

const isAdding = ref(false);
const addError = ref('');
const addProductData = ref({ product_code: '', initial_stock: null, price: null });

function selectProduct(product) {
  addProductData.value.product_code = product.product_code;
  if (product.default_price) {
    addProductData.value.price = product.default_price;
  }
  stockInputRef.value?.focus();
}

async function handleAddProduct() {
  isAdding.value = true;
  addError.value = '';
  try {
    const dataToSend = { ...addProductData.value };
    if (dataToSend.price === null || dataToSend.price === '') {
      delete dataToSend.price;
    }
    await eventDetailStore.addProductToEvent(props.id, dataToSend);
    addProductData.value = { product_code: '', initial_stock: null, price: null };
    searchQuery.value = '';
  } catch (error) {
    addError.value = error.message;
  } finally {
    isAdding.value = false;
  }
}

const isEditModalVisible = ref(false);
const isUpdating = ref(false);
const editError = ref('');
const editableProduct = ref(null);

function openEditModal(product) {
  editableProduct.value = { ...product };
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
    await eventDetailStore.updateEventProduct(id, { price, initial_stock });
    closeEditModal();
  } catch (error) {
    editError.value = error.message;
  } finally {
    isUpdating.value = false;
  }
}

async function handleDelete(product) {
  if (window.confirm(`确定要从该展会下架 "${product.name}" 吗？`)) {
    try {
      await eventDetailStore.deleteEventProduct(product.id);
    } catch (error) {
      alert(error.message);
    }
  }
}

onMounted(() => {
  eventDetailStore.fetchProductsForEvent(props.id);
  productStore.fetchMasterProducts();
});

onUnmounted(() => {
  eventDetailStore.resetStore();
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
  padding: 1.0rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.add-product-form {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 1rem;
}

/* --- 表格样式 --- */
.product-table {
  width: 100%;
  margin-top: 0.5rem;
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

.action-btn {
  background: none;
  border: 1px solid transparent;
  color: var(--primary-text-color);
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.product-search-container {
  margin-bottom: 0.5rem;
}

.search-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex-grow: 1;
}

.product-preview-container {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.5rem;
  background-color: var(--bg-color);
}
.no-results-message {
  color: #888;
  padding: 1rem;
  text-align: center;
}

.product-preview-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.5rem;
}

.preview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.4rem;
  border: 1px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
  background-color: var(--card-bg-color);
}
.preview-item:hover {
  border-color: var(--accent-color);
  background-color: rgba(3, 218, 198, 0.1);
}
.preview-item.selected {
  border-color: var(--accent-color);
  background-color: rgba(3, 218, 198, 0.12);
}

.preview-item-img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.preview-item-img :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-item-info {
  display: flex;
  flex-direction: column;
}

.preview-item-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--primary-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 110px;
}

.preview-item-code {
  font-size: 0.75rem;
  color: #888;
}
.preview-item-price {
  font-size: 0.75rem;
  color: var(--accent-color);
}

.category-select {
  min-width: 140px;
}

/* 让搜索栏更显眼 */
.search-input :deep(.n-input) {
  border-width: 2px;
}
.search-input :deep(.n-input:not(.n-input--disabled):focus-within) {
  box-shadow: 0 0 0 2px rgba(3, 218, 198, 0.2);
  border-color: var(--accent-color);
}

/* 表格缩略图的适配，避免超出 */
.preview-img {
  width: 50px;
  height: 50px;
}
.preview-img :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
