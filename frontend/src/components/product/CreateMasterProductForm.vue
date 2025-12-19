<template>
  <div class="form-container">
    <h3>添加新商品</h3>
    <n-form @submit.prevent label-placement="top">
      <div class="form-group">
        <label>商品编号:</label>
        <n-input v-model:value="formData.product_code" placeholder="A01" />
      </div>
      <div class="form-group">
        <label>商品名称:</label>
        <n-input v-model:value="formData.name" placeholder="灵梦亚克力立牌" />
      </div>
      <div class="form-group">
        <label>默认价格:</label>
        <n-input-number v-model:value="formData.default_price" :precision="2" :step="0.01" placeholder="45.00" style="width: 100%;" />
      </div>
      <n-button type="primary" :loading="isSubmitting" @click="handleSubmit">{{ isSubmitting ? '添加中...' : '添加' }}</n-button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </n-form>
  </div>
  
</template>

<script setup>
// (这部分代码与 CreateEventForm 非常类似, 只是字段不同)
import { ref } from 'vue';
import { useProductStore } from '@/stores/productStore';
import { NForm, NInput, NInputNumber, NButton } from 'naive-ui';

const store = useProductStore();
const errorMessage = ref('');
const isSubmitting = ref(false);
const formData = ref({
  product_code: '',
  name: '',
  default_price: null,
});

async function handleSubmit() {
  errorMessage.value = '';
  // 先做标准化，防止只输入空格导致提交空字符串
  const trimmedCode = String(formData.value.product_code || '').trim();
  const trimmedName = String(formData.value.name || '').trim();
  if (import.meta.env.DEV) {
    console.log('[CreateMasterProduct] submit payload preview', {
      product_code: trimmedCode,
      name: trimmedName,
      default_price: formData.value.default_price,
    });
  }
  // 简单校验（基于去空格后的值）
  if (!trimmedCode || !trimmedName || formData.value.default_price == null) {
    errorMessage.value = '请填写商品编号、名称和默认价格。';
    return;
  }
  isSubmitting.value = true;
  try {
    const fd = new FormData();
    fd.append('product_code', trimmedCode);
    fd.append('name', trimmedName);
    fd.append('default_price', String(formData.value.default_price));
    await store.createMasterProduct(fd);
    formData.value = { product_code: '', name: '', default_price: null };
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
/* 样式与 CreateEventForm.vue 完全可以共享 */
</style>