<template>
  <div class="form-container">
    <h3>创建新展会</h3>
    <n-form @submit.prevent class="two-column-form">
      <div class="form-group">
        <label for="name">展会名称:</label>
        <n-input id="name" v-model:value="formData.name" placeholder="例如：COMICUP 31" />
      </div>
      <div class="form-group">
        <label for="date">日期:</label>
        <n-date-picker id="date" v-model:formatted-value="formData.date" type="date" value-format="yyyy-MM-dd" />
      </div>
      <div class="form-group">
        <label for="location">地点:</label>
        <n-input id="location" v-model:value="formData.location" placeholder="例如：上海" />
      </div>
      <div class="form-group">
        <label for="vendor_password">摊主密码 (可选):</label>
        <n-input id="vendor_password" v-model:value="formData.vendor_password" placeholder="留空则使用全局密码" />
      </div>

      <div class="form-group full-width">
        <ImageUploader 
          label="展会收款码图片 (可选)"
          v-model="paymentQrCodeFile"
        />
      </div>

      <div class="form-actions full-width">
        <n-button type="primary" :loading="isSubmitting" @click="handleSubmit">
          {{ isSubmitting ? '创建中...' : '创建' }}
        </n-button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </n-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEventStore } from '@/stores/eventStore';
import ImageUploader from '@/components/shared/ImageUploader.vue';
import { NForm, NInput, NDatePicker, NButton } from 'naive-ui';

const store = useEventStore();
const isSubmitting = ref(false);
const errorMessage = ref('');

const formData = ref({
  name: '',
  date: null,
  location: '',
  vendor_password: '' 
});

// 【修改】只保留 v-model 需要的 ref
const paymentQrCodeFile = ref(null);


async function handleSubmit() {
  // 简单必填校验，保持与原先 required 一致
  if (!formData.value.name || !formData.value.date) {
    errorMessage.value = '展会名称和日期不能为空。';
    return;
  }
  isSubmitting.value = true;
  errorMessage.value = '';

  const submissionData = new FormData();
  submissionData.append('name', formData.value.name);
  submissionData.append('date', formData.value.date);
  submissionData.append('location', formData.value.location);
  submissionData.append('vendor_password', formData.value.vendor_password);
  
  if (paymentQrCodeFile.value) {
    submissionData.append('payment_qr_code', paymentQrCodeFile.value);
  }

  try {
    await store.createEvent(submissionData);
    
    formData.value = { name: '', date: null, location: '', vendor_password: '' };
    paymentQrCodeFile.value = null; 
    
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.form-container {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.96rem;
}

/* 【新增】使用 CSS Grid 实现两列布局 */
.two-column-form {
  display: grid;
  /* 创建两列，每列占据相等的剩余空间 */
  grid-template-columns: 1fr 1fr;
  /* 定义列间距和行间距 */
  gap: 0.6rem 1rem; 
}

.full-width {
  /* 从第1条网格线跨越到最后1条 (-1) */
  grid-column: 1 / -1;
}

.form-group {
  margin-bottom: 0;
}

label {
  display: block; /* 确保 label 独占一行 */
  margin-bottom: 0.3rem;
  font-size: 0.95em;
}

input[type="text"],
input[type="date"] {
  width: 100%;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  padding: 6px 8px;
  border-radius: 3px;
  font-size: 0.96em;
  height: 32px;
  box-sizing: border-box;
}

/* 【新增】提交按钮和错误信息的容器 */
.form-actions {
  margin-top: 0.5rem; /* 与上方元素留出一些间距 */
}

button,
.btn {
  padding: 6px 14px;
  font-size: 0.96em;
  border-radius: 3px;
}

.error-message {
  margin-top: 0.5rem;
  font-size: 0.95em;
  /* 确保错误信息在按钮下方 */
  width: 100%; 
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ImageUploader 的内部样式由其自身 scoped CSS 控制，这里无需再写 */
</style>