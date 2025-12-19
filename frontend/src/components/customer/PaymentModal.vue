<template>
  <n-modal :show="show" :mask-closable="true" @update:show="val => { if (!val) $emit('close') }">
    <n-card
      :bordered="true"
      size="medium"
      class="payment-card"
      :segmented="{ content: true, footer: true }"
      :style="cardStyle"
    >
      <template #header>
        <div class="header-line">
          请扫码支付 <strong>¥{{ total.toFixed(2) }}</strong>
        </div>
      </template>

      <div class="content-area">
        <div v-if="qrCodeUrl" class="qr-code-container">
          <n-image :src="qrCodeUrl" alt="收款码" class="qr-code" preview-disabled />
        </div>
        <div v-else class="no-qr-code">
          <p>暂无收款码</p>
          <p>请联系摊主设置收款码</p>
        </div>
        <p class="scan-tip">
          手机浏览器用户请长按二维码图片保存后，<br />
          用微信/支付宝“扫一扫”识别付款
        </p>
        <p class="after-tip">支付完成后，请等待摊主为您配货</p>
      </div>

      <template #footer>
        <n-button block type="primary" @click="$emit('close')">关闭</n-button>
      </template>
    </n-card>
  </n-modal>
  
</template>
<script setup>
import { computed } from 'vue';
import { NModal, NCard, NImage, NButton } from 'naive-ui';

const props = defineProps({
  show: { type: Boolean, required: true },
  total: { type: Number, required: true },
  qrCodeUrl: { type: String, default: null }
});
defineEmits(['close']);

// 响应式卡片宽度：桌面 520px，移动端占 92vw
const cardStyle = computed(() => ({
  width: 'min(520px, 92vw)'
}));
</script>
<style scoped>
/* 标题和二维码样式 */
.header-line {
  font-size: 1.2rem;
}
.header-line strong {
  color: var(--accent-color);
}

.payment-card {
  text-align: center;
}

.content-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  /* 去掉内部高度限制，避免出现内滚动条 */
  max-height: none;
  overflow: visible;
}
.qr-code-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.qr-code {
  width: 100%;
  max-width: 420px; /* 桌面最大 420px */
  aspect-ratio: 1 / 1;
  border-radius: 8px;
}
:deep(.qr-code img) {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 保持完整显示且不溢出 */
}

.no-qr-code {
  padding: 2rem;
  color: #888;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  background-color: var(--bg-color);
}

.no-qr-code p {
  margin: 0.5rem 0;
}

.payment-card p {
  margin: 0;
  color: #aaa;
}

@media (max-width: 600px) {
  .payment-card {
    border-radius: 8px;
  }
  .qr-code-container { width: 100%; margin: 0.5rem 0 1rem 0; }
  /* 移动端：二维码宽度跟随卡片内容宽度，不再使用视口宽度，避免横向滚动 */
  .qr-code { width: 100%; max-width: 100%; }
}
.after-tip { margin-top: -0.25rem; }
.scan-tip {
  color: var(--accent-color);
  font-size: 1.1rem;
  margin: 0.5rem 0 0.5rem 0;
  font-weight: bold;
  line-height: 1.5;
}
</style>
