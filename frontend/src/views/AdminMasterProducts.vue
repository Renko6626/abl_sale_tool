<template>
  <div>
    <header class="page-header">
      <h1>全局商品库</h1>
      <p>在这里管理所有可复用的商品模板。添加后,即可在展会中通过编号上架。</p>
    </header>

    <main>
      <!-- 创建表单 -->
      <n-card class="form-container" title="添加新商品到仓库" size="small">
        <form @submit.prevent="handleCreate">
          <div class="form-grid">
            <div class="form-group">
              <label for="create-code">商品编号:</label>
              <n-input id="create-code" v-model:value="createFormData.product_code" placeholder="A01" clearable required />
            </div>
            <div class="form-group">
              <label for="create-name">商品名称:</label>
              <n-input id="create-name" v-model:value="createFormData.name" placeholder="灵梦亚克力立牌" clearable required />
            </div>
            <div class="form-group">
              <label for="create-price">默认价格 (¥):</label>
              <n-input-number id="create-price" v-model:value="createFormData.default_price" :step="0.01" :min="0" placeholder="45.00" required />
            </div>
            <div class="form-group">
              <label for="create-category">商品分类:</label>
            <n-input id="create-category" v-model:value="createFormData.category" placeholder="漫画、亚克力、毛绒玩具等" clearable />
            </div>
          </div>
          
          <!-- 【核心修改】使用可复用的 ImageUploader 组件 -->
          <ImageUploader
            label="预览图"
            v-model="createFormFile"
          />

          <n-button type="primary" attr-type="submit" :disabled="isCreating">
            {{ isCreating ? '添加中...' : '添加到仓库' }}
          </n-button>
          <p v-if="createError" class="error-message">{{ createError }}</p>
        </form>
      </n-card>
      
      <div class="filters">
        <n-checkbox v-model:checked="store.showInactive" @update:checked="store.fetchMasterProducts()">显示已停用的商品</n-checkbox>
      </div>
      
      <!-- 商品列表 -->
      <MasterProductList @edit="openEditModal" @toggleStatus="handleToggleStatus" />
    </main>

    <!-- 编辑模态框 -->
    <AppModal :show="isEditModalVisible" @close="closeEditModal">
      <template #header><h3>编辑商品</h3></template>
      <template #body>
        <form v-if="editableProduct" class="edit-form" @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>商品编号:</label>
            <n-input v-model:value="editableProduct.product_code" clearable required />
          </div>
          <div class="form-group">
            <label>商品名称:</label>
            <n-input v-model:value="editableProduct.name" clearable required />
          </div>
          <div class="form-group">
            <label>默认价格 (¥):</label>
            <n-input-number v-model:value="editableProduct.default_price" :step="0.01" :min="0" required />
          </div>
          <div class="form-group">
            <label>商品分类:</label>
            <n-input v-model:value="editableProduct.category" placeholder="漫画、亚克力、毛绒玩具等" clearable />
          </div>

          <!-- 【核心修改】再次使用 ImageUploader 组件 -->
          <ImageUploader
            label="更换预览图"
            :initial-image-url="editableProduct.image_url"
            v-model="editFormFile"
            @image-removed="handleEditImageRemoval"
          />

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
import { ref } from 'vue';
import { useProductStore } from '@/stores/productStore';
import MasterProductList from '@/components/product/MasterProductList.vue';
import AppModal from '@/components/shared/AppModal.vue';
// 【新增】导入可复用的图片上传组件
import ImageUploader from '@/components/shared/ImageUploader.vue';
import { NCard, NInput, NInputNumber, NButton, NCheckbox, NSpace } from 'naive-ui';

const store = useProductStore();
// 【移除】不再需要硬编码的 backendUrl

// --- 创建逻辑的状态 ---
const isCreating = ref(false);

const createError = ref('');
const createFormData = ref({ product_code: '', name: '', default_price: null });
const createFormFile = ref(null); // ImageUploader 会通过 v-model 更新这个
// 【移除】不再需要 createPreviewUrl 和 handleCreateFileChange

async function handleCreate() {
  isCreating.value = true;
  createError.value = '';
  try {
    // 【修改】构建 FormData
    const formData = new FormData();
    const code = String(createFormData.value.product_code || '').trim();
    const name = String(createFormData.value.name || '').trim();
    const price = createFormData.value.default_price;
    const category = String(createFormData.value.category ?? '').trim();
    formData.append('product_code', code);
    formData.append('name', name);
    formData.append('default_price', String(price));
    if (category) formData.append('category', category);
    if (createFormFile.value) {
      formData.append('image', createFormFile.value);
    }
    
    // 假设 store action 已被修改为接收 FormData
    await store.createMasterProduct(formData);
    
    // 成功后重置表单
    createFormData.value = { product_code: '', name: '', default_price: null };
    createFormFile.value = null; // ImageUploader 会自动清空预览
  } catch (error) {
    createError.value = error.message;
  } finally {
    isCreating.value = false;
  }
}

// --- 编辑逻辑的状态 ---
const isEditModalVisible = ref(false);
const isUpdating = ref(false);
const editError = ref('');
const editableProduct = ref({});
const editFormFile = ref(null); // ImageUploader 会通过 v-model 更新这个
const isImageRemovedForEdit = ref(false); // 标记用户是否点击了移除
// 【移除】不再需要 editPreviewUrl 和 handleEditFileChange

function openEditModal(product) {
  editableProduct.value = { ...product };
  editFormFile.value = null; // 清空上次选择的文件
  isImageRemovedForEdit.value = false; // 重置移除标记
  isEditModalVisible.value = true;
}

function closeEditModal() {
  isEditModalVisible.value = false;
  editError.value = '';
}

// 【新增】处理来自 ImageUploader 的移除事件
function handleEditImageRemoval() {
  isImageRemovedForEdit.value = true;
}

async function handleUpdate() {
  isUpdating.value = true;
  editError.value = '';
  try {
    // 【修改】构建 FormData
    const formData = new FormData();
    const eCode = String(editableProduct.value.product_code || '').trim();
    const eName = String(editableProduct.value.name || '').trim();
    const ePrice = editableProduct.value.default_price;
    const eCategory = String(editableProduct.value.category ?? '').trim();
    formData.append('product_code', eCode);
    formData.append('name', eName);
    formData.append('default_price', String(ePrice));
    if (eCategory) formData.append('category', eCategory);
    if (editFormFile.value) {
      formData.append('image', editFormFile.value);
    } else if (isImageRemovedForEdit.value) {
      formData.append('remove_image', 'true');
    }
    
    // 假设 store action 已被修改为接收 ID 和 FormData
    await store.updateMasterProduct(editableProduct.value.id, formData);
    closeEditModal();
  } catch (error) {
    editError.value = error.message;
  } finally {
    isUpdating.value = false;
  }
}

async function handleToggleStatus(product) {
  const actionText = product.is_active ? '停用' : '启用';
  if (window.confirm(`确定要"${actionText}"商品 "${product.name}" 吗？`)) {
    try {
      await store.toggleProductStatus(product);
    } catch (error) {
      alert(error.message);
    }
  }
}
</script>

<style scoped>
/* ... 原有样式基本保持不变 ... */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}
.page-header h1 { color: var(--accent-color); margin: 0; }
.page-header p { color: #aaa; margin-top: 0.5rem; }

.form-container {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem; /* 稍微增加间距 */
  margin-bottom: 1.5rem;
}
.form-group { display: flex; flex-direction: column; }
label { margin-bottom: 0.5rem; }
.error-message { color: var(--error-color); margin-top: 1rem; }

.btn-primary {
  background-color: var(--accent-color);
  color: var(--bg-color);
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* 增加间距以容纳ImageUploader */
}
.filters {
  margin-top: 2rem;
  margin-bottom: 1rem;
}
/* 【移除】不再需要 .preview-img-form 样式 */
</style>