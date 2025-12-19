<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <RouterView />
        <GlobalAlert />
        <!-- 将测试组件放在这里，它会悬浮在所有页面之上 -->
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { RouterView } from 'vue-router';
import GlobalAlert from '@/components/GlobalAlert.vue';
// 导入测试组件
import WebSocketTester from './components/WebSocketTester.vue';
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme } from 'naive-ui';

// 结合现有全局样式变量，设置 Naive UI 的主题覆盖
const themeOverrides = {
  common: {
    primaryColor: '#03DAC6',
    primaryColorHover: '#04e2cd',
    primaryColorPressed: '#02c7b5',
    primaryColorSuppl: '#03DAC6',
    textColorBase: '#E0E0E0',
    textColor1: '#E0E0E0',
    textColor2: '#C8C8C8',
    bodyColor: '#121212',
    cardColor: '#101010',
    modalColor: '#101010',
    popoverColor: '#101010',
    tableColor: '#101010',
    inputColor: '#121212',
    borderColor: '#2c2c2c',
    borderColorHover: '#3a3a3a',
    borderColorPressed: '#3a3a3a',
    dividerColor: '#2c2c2c',
    successColor: '#4CAF50',
    errorColor: '#F44336',
  }
};

</script>