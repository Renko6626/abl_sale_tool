<template>
  <div class="form-container">
    <h3>创建新展会</h3>
    <!-- 【修改】给 form 标签添加一个 class 用于设置网格布局 -->
    <form @submit.prevent="handleSubmit" class="two-column-form">
      <!-- .prevent 修饰符可以阻止表单提交时的默认页面刷新行为 -->
      
      <!-- 以下四个 form-group 会自动排列成 2x2 的网格 -->
      <div class="form-group">
        <label for="name">展会名称:</label>
        <input id="name" v-model="formData.name" type="text" placeholder="例如：COMICUP 31" required />
      </div>
      <div class="form-group">
        <label for="date">日期:</label>
        <input id="date" v-model="formData.date" type="date" required />
      </div>
      <div class="form-group">
        <label for="location">地点:</label>
        <input id="location" v-model="formData.location" type="text" placeholder="例如：上海" />
      </div>
      <div class="form-group">
        <label for="vendor_password">摊主密码 (可选):</label>
        <input id="vendor_password" v-model="formData.vendor_password" type="text" placeholder="留空则使用全局密码" />
      </div>

      <!-- 【修改】这个 group 添加 'full-width' class，使其横跨两列 -->
      <div class="form-group full-width">
        <ImageUploader 
          label="展会收款码图片 (可选)"
          v-model="paymentQrCodeFile"
        />
      </div>
      
      <!-- 【修改】将按钮和错误信息也放入一个横跨两列的容器中 -->
      <div class="form-actions full-width">
        <button type="submit" class="btn" :disabled="isSubmitting">
          {{ isSubmitting ? '创建中...' : '创建' }}
        </button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEventStore } from '@/stores/eventStore';
import ImageUploader from '@/components/shared/ImageUploader.vue';

const store = useEventStore();
const isSubmitting = ref(false);
const errorMessage = ref('');

const formData = ref({
  name: '',
  date: '',
  location: '',
  vendor_password: '' 
});

// 【修改】只保留 v-model 需要的 ref
const paymentQrCodeFile = ref(null);

// 【清理】以下与图片预览和文件输入相关的逻辑都已封装在 ImageUploader 组件中，
// 在这里不再需要，已安全移除。
// const qrCodePreviewUrl = ref(null);
// const fileInput = ref(null);
// function triggerFileInput() { ... }
// function handleFileChange(event) { ... }
// function removeImage() { ... }

async function handleSubmit() {
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
    
    formData.value = { name: '', date: '', location: '', vendor_password: '' };
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

/* 【新增】让标有 .full-width 的元素横跨所有列 */
.full-width {
  /* 从第1条网格线跨越到最后1条 (-1) */
  grid-column: 1 / -1;
}

.form-group {
  /* 【修改】移除 margin-bottom，因为 'gap' 属性已经处理了间距 */
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