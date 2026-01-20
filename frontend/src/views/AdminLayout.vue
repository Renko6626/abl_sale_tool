<template>
  <!-- 使用 Naive UI 的布局组件 -->
  <n-layout has-sider position="absolute">
    
    <!-- 侧边栏：使用 n-layout-sider，自带折叠和过渡动画 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="isMobile ? 0 : 80"
      :width="240"
      :collapsed="isSidebarCollapsed"
      :show-trigger="false"
      @collapse="isSidebarCollapsed = true"
      @expand="isSidebarCollapsed = false"
      class="sidebar-container"
    >
      <!-- 侧边栏头部 -->
      <div class="sidebar-header" :style="{ padding: isSidebarCollapsed ? '1rem 0' : '1.5rem' }">
        <h2 v-if="!isSidebarCollapsed" class="logo-text">管理后台</h2>
        <!-- 切换按钮采用 n-button -->
        <n-button 
          v-if="!isMobile"
          circle 
          size="small" 
          @click="toggleSidebar"
          class="toggle-btn"
        >
          <template #icon>
            <span v-if="isSidebarCollapsed">»</span>
            <span v-else>«</span>
          </template>
        </n-button>
      </div>

      <!-- 导航内容：使用 n-menu 能够自动处理选中状态和样式 -->
      <div class="sidebar-content">
        <n-menu
          :collapsed="isSidebarCollapsed"
          :collapsed-width="80"
          :collapsed-icon-size="22"
          :options="menuOptions"
          :value="activeKey"
        />

        <!-- 当没有选中展会且有正在进行的展会时，显示快捷入口 -->
        <div v-if="!event && ongoingEvents.length > 0 && !isSidebarCollapsed" class="ongoing-events-section">
          <n-divider />
          <p class="section-title">正在进行的展会</p>
          <n-space vertical :size="8">
            <n-button
              v-for="evt in ongoingEvents"
              :key="evt.id"
              block
              secondary
              size="small"
              @click="$router.push(`/admin/events/${evt.id}/products`)"
              class="ongoing-event-btn"
            >
              <template #icon>
                <span class="event-status-dot">●</span>
              </template>
              <span class="event-name-text">{{ evt.name }}</span>
            </n-button>
          </n-space>
        </div>

        <div v-if="!isSidebarCollapsed" class="footer-section">
          <n-divider />
          <p class="section-title">快捷视图</p>
          <n-space vertical>
            <n-button block secondary type="primary" @click="$router.push('/vendor')">
              <template #icon>
                <n-icon><ExternalIcon /></n-icon>
              </template>
              摊主视图
            </n-button>
            <n-button block secondary @click="$router.push('/')">
              <template #icon>
                <n-icon><ExternalIcon /></n-icon>
              </template>
              顾客视图
            </n-button>
          </n-space>
        </div>
      </div>
    </n-layout-sider>

    <!-- 主内容区 -->
    <n-layout-content content-style="padding: 24px;" :native-scrollbar="false">
      <!-- 移动端汉堡菜单按钮 -->
      <n-button
        v-if="isMobile"
        circle
        type="primary"
        class="mobile-fab"
        @click="toggleSidebar"
      >
        <template #icon>{{ isSidebarCollapsed ? '☰' : '✕' }}</template>
      </n-button>

      <router-view />
      
      <!-- 移动端遮罩层 -->
      <div 
        v-if="!isSidebarCollapsed && isMobile" 
        class="mobile-overlay" 
        @click="closeSidebar"
      ></div>
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, h } from 'vue';
import { RouterLink, useRouter, useRoute } from 'vue-router';
import { 
  NLayout, NLayoutSider, NLayoutContent, NButton, 
  NMenu, NDivider, NSpace, NIcon 
} from 'naive-ui';
import { useEventStore } from '@/stores/eventStore';

const route = useRoute();
const router = useRouter();
const eventStore = useEventStore();

// 状态管理
const isSidebarCollapsed = ref(false);
const isMobile = ref(window.innerWidth < 992);

// 提取当前激活的菜单项
const activeKey = computed(() => route.path);

// 图标组件：这里用简单的 SVG 包装，你也可以使用 @vicons/ionicons5
const ExternalIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: '2' }, [
  h('path', { d: 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6' }),
  h('polyline', { points: '15 3 21 3 21 9' }),
  h('line', { x1: '10', y1: '14', x2: '21', y2: '3' })
]);

const event = computed(() => {
  const eventId = route.params.id;
  if (!eventId) return null;
  return eventStore.events.find(e => e.id === parseInt(eventId, 10)) || { name: '加载中...', id: eventId };
});

// 获取正在进行中的展会（最多3个）
const ongoingEvents = computed(() => {
  return eventStore.events
    .filter(e => e.status === '进行中')
    .slice(0, 3);
});

// 构建 Naive UI Menu 选项
const menuOptions = computed(() => {
  const baseOptions = [
    { label: () => h(RouterLink, { to: '/admin' }, { default: () => '展会管理' }), key: '/admin' },
    { label: () => h(RouterLink, { to: '/admin/master-products' }, { default: () => '全局商品库' }), key: '/admin/master-products' },
  ];

  if (event.value) {
    baseOptions.push(
      { type: 'divider', key: 'd1' },
      { 
        label: event.value.name, 
        key: 'event-group', 
        type: 'group',
        children: [
          { label: () => h(RouterLink, { to: `/admin/events/${event.value.id}/products` }, { default: () => '商品管理' }), key: `/admin/events/${event.value.id}/products` },
          { label: () => h(RouterLink, { to: `/admin/events/${event.value.id}/orders` }, { default: () => '订单管理' }), key: `/admin/events/${event.value.id}/orders` },
          { label: () => h(RouterLink, { to: `/admin/events/${event.value.id}/stats` }, { default: () => '销售统计' }), key: `/admin/events/${event.value.id}/stats` },
        ]
      }
    );
  }
  return baseOptions;
});

// 逻辑函数
function toggleSidebar() { isSidebarCollapsed.value = !isSidebarCollapsed.value; }
function closeSidebar() { if (isMobile.value) isSidebarCollapsed.value = true; }

const handleResize = () => {
  isMobile.value = window.innerWidth < 992;
  if (isMobile.value) isSidebarCollapsed.value = true;
  else isSidebarCollapsed.value = false;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* 侧边栏内部排版 */
.sidebar-container {
  height: 100vh;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: padding 0.3s;
}

.logo-text {
  margin: 0;
  font-size: 1.25rem;
  color: var(--n-text-color);
  white-space: nowrap;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: calc(100% - 80px);
}

.footer-section {
  margin-top: auto;
  padding: 0 1rem 1.5rem 1rem;
}

.section-title {
  font-size: 0.75rem;
  color: #888;
  margin-bottom: 0.75rem;
  padding-left: 4px;
}

/* 正在进行的展会区域 */
.ongoing-events-section {
  padding: 0 1rem;
  margin-top: 1rem;
}

.ongoing-event-btn {
  text-align: left;
  justify-content: flex-start;
  height: auto;
  min-height: 36px;
  padding: 8px 12px;
}

.event-status-dot {
  color: #ffdf57;
  font-size: 12px;
  margin-right: 4px;
}

.event-name-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: left;
}

.ongoing-event-btn:hover .event-status-dot {
  color: var(--n-color-hover);
}

/* 移动端汉堡按钮 */
.mobile-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1001;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* 移动端遮罩 */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 999;
}

/* 适配侧边栏在移动端的悬浮效果 */
@media (max-width: 992px) {
  :deep(.n-layout-sider) {
    position: fixed !important;
    height: 100% !important;
    z-index: 1000;
  }
}
</style>