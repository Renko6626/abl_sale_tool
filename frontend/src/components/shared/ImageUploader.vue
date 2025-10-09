<!-- src/components/shared/ImageUploader.vue -->
<template>
  <div class="image-uploader-container">
    <label v-if="label" class="form-label">{{ label }}</label>
    
    <!-- 隐藏的文件输入框 -->
    <input 
      type="file" 
      ref="fileInputRef" 
      @change="handleFileChange" 
      accept="image/*" 
      style="display: none;"
    />

    <!-- 图片预览区 -->
    <div class="image-preview-wrapper">
      <!-- 1. 新图片预览 -->
      <div v-if="previewUrl" class="image-preview-box">
        <img :src="previewUrl" alt="新图片预览" class="image-preview" />
        <span class="preview-tag">新图片</span>
      </div>
      <!-- 2. 初始图片显示 (如果没有选择新图片) -->
      <div v-else-if="initialImageUrl" class="image-preview-box">
        <img :src="initialImageUrl" alt="当前图片" class="image-preview" />
        <span class="preview-tag">当前图片</span>
      </div>
      <!-- 3. 无图提示 -->
      <div v-else class="no-image-placeholder">
        无图片
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="image-actions">
      <button type="button" class="btn btn-secondary" @click="triggerFileInput">
        {{ initialImageUrl || previewUrl ? '更换图片' : '选择图片' }}
      </button>
      <button 
        type="button" 
        class="btn btn-danger" 
        v-if="initialImageUrl || previewUrl" 
        @click="removeImage"
      >
        移除图片
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// =================================================================
// 组件 API 定义 (Props & Emits)
// =================================================================

const props = defineProps({
  // 用于 v-model，接收父组件传来的 File 对象
  modelValue: {
    type: File,
    default: null,
  },
  // 用于显示已存在的图片
  initialImageUrl: {
    type: String,
    default: '',
  },
  // 组件的标签
  label: {
    type: String,
    default: '图片上传'
  }
});

const emit = defineEmits(['update:modelValue', 'image-removed']);

// =================================================================
// 内部状态和逻辑
// =================================================================

const backendUrl = import.meta.env.VITE_API_BASE_URL;
const fileInputRef = ref(null);
const previewUrl = ref(null); // 仅用于新选择文件的本地预览

// 当 initialImageUrl 改变时 (例如父组件的模态框用于编辑不同项)
// 我们需要重置内部状态，以防显示上一个项目的预览
watch(() => props.initialImageUrl, () => {
  resetState();
});

function triggerFileInput() {
  fileInputRef.value.click();
}

function handleFileChange(event) {
  const file = event.target.files[0];
  if (!file) return;

  // 清理之前的预览 URL，防止内存泄漏
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  previewUrl.value = URL.createObjectURL(file);
  emit('update:modelValue', file); // 更新 v-model
}

function removeImage() {
  resetState();
  emit('update:modelValue', null); // 清空 v-model
  emit('image-removed'); // 发送一个明确的移除信号
}

// 重置状态的辅助函数
function resetState() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
  previewUrl.value = null;
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
}
</script>

<style scoped>
.image-uploader-container {
  margin-bottom: 1rem;
}
.form-label {
  display: block;
  margin-bottom: 0.5rem;
}
.image-preview-wrapper {
  margin-bottom: 1rem;
}
.image-preview-box {
  position: relative;
  display: inline-block;
  border: 1px solid var(--border-color);
  padding: 5px;
  border-radius: 4px;
  background-color: var(--bg-color);
}
.image-preview {
  max-width: 200px;
  max-height: 200px;
  display: block;
}
.preview-tag {
  position: absolute;
  top: 5px;
  left: 5px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 6px;
  font-size: 0.8rem;
  border-radius: 3px;
}
.no-image-placeholder {
  display: inline-block;
  padding: 2rem 3rem;
  border: 2px dashed var(--border-color);
  border-radius: 4px;
  color: #888;
}
.image-actions {
  display: flex;
  gap: 1rem;
}
.btn-secondary {
  background-color: #555;
  border-color: #555;
  color: white; /* 确保文字可见 */
  border: 1px solid transparent;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
}
.btn-secondary:hover { background-color: #666; }
.btn-danger {
  background-color: var(--error-color);
  color: white;
  border: 1px solid transparent;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
}
</style>