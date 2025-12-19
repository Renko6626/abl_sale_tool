<template>
  <!-- 【修改】根据侧边栏状态动态添加 class -->
  <div class="admin-layout" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    
    <!-- 【新增】遮罩层，用于在移动端打开侧边栏时覆盖主内容区 -->
    <div v-if="!isSidebarCollapsed && isMobile" class="overlay" @click="closeSidebar"></div>

    <aside class="sidebar">
      <!-- 【新增】侧边栏头部，包含 Logo 和切换按钮 -->
      <div class="sidebar-header">
        <h2 v-if="!isSidebarCollapsed">管理后台</h2>
        <n-button class="sidebar-toggle" circle size="small" @click="toggleSidebar" aria-label="切换侧边栏">
          <span v-if="isSidebarCollapsed">»</span>
          <span v-else>«</span>
        </n-button>
      </div>

      <n-scrollbar class="sidebar-content">
        <div>
          <nav>
            <RouterLink to="/admin">展会管理</RouterLink>
            <RouterLink to="/admin/master-products">全局商品库</RouterLink>
          </nav>

          <div v-if="event" class="context-nav">
            <hr>
            <h3 class="event-title">{{ event.name }}</h3>
            <nav>
              <RouterLink :to="`/admin/events/${event.id}/products`">商品管理</RouterLink>
              <RouterLink :to="`/admin/events/${event.id}/orders`">订单管理</RouterLink>
              <RouterLink :to="`/admin/events/${event.id}/stats`">销售统计</RouterLink>
            </nav>
          </div>
        </div>

        <div class="view-links">
          <hr>
          <h4>快捷视图</h4>
          <a href="/vendor" target="_blank" class="view-link-btn">
            <span>摊主视图</span>
            <svg><!-- ... icon ... --></svg>
          </a>
          <a href="/" target="_blank" class="view-link-btn">
            <span>顾客视图</span>
            <svg><!-- ... icon ... --></svg>
          </a>
        </div>
      </n-scrollbar>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
// 【修改】新增 ref, onMounted, onUnmounted
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { useEventStore } from '@/stores/eventStore'; 
import { NButton, NScrollbar } from 'naive-ui';

const route = useRoute();
const eventStore = useEventStore();

// =======================================================
// 【新增】侧边栏响应式逻辑
// =======================================================
const isSidebarCollapsed = ref(false);
const isMobile = ref(window.innerWidth < 992);

// 切换侧边栏状态的函数
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
}

// 在移动端点击遮罩层时关闭侧边栏
function closeSidebar() {
  if (isMobile.value) {
    isSidebarCollapsed.value = true;
  }
}

// 监听窗口大小变化的函数
const handleResize = () => {
  isMobile.value = window.innerWidth < 992;
  // 如果窗口变宽，且侧边栏是因移动端而收起的，则自动展开
  if (!isMobile.value && isSidebarCollapsed.value) {
    isSidebarCollapsed.value = false;
  }
  // 如果窗口变窄，自动收起侧边栏
  if (isMobile.value) {
    isSidebarCollapsed.value = true;
  }
};

// 在组件挂载时添加监听器，并设置初始状态
onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize(); // 立即执行一次以设置初始状态
});

// 在组件卸载时移除监听器，防止内存泄漏
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
// =======================================================

const event = computed(() => {
  const eventId = route.params.id;
  if (!eventId) return null;
  return eventStore.events.find(e => e.id === parseInt(eventId, 10)) || { name: '加载中...', id: eventId };
});
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  position: relative; /* 为移动端遮罩层定位 */
  transition: margin-left 0.3s ease; /* 为桌面端内容区添加过渡 */
}

.sidebar {
  /* 基础样式 */
  position: fixed; /* 改为 fixed 定位，使其在移动端能覆盖内容 */
  left: 0;
  top: 0;
  height: 100%;
  width: 240px; /* 稍微加宽一点 */
  background-color: var(--card-bg-color);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 1000; /* 提高层级 */
  transition: transform 0.3s ease, width 0.3s ease; /* 添加过渡效果 */
}
/* 【新增】侧边栏头部 */
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  padding-bottom: 1rem;
}
.sidebar-header h2 {
  white-space: nowrap; /* 防止文字换行 */
  overflow: hidden;    /* 隐藏溢出内容 */
}

/* 【新增】侧边栏切换按钮 */
.sidebar-toggle {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  line-height: 1;
}
.sidebar-toggle:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

/* 【新增】让侧边栏内容可滚动 */
.sidebar-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: 0 1.5rem 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}


/* --- 收起状态的样式 --- */
.admin-layout.sidebar-collapsed .sidebar {
  /* 在桌面端收起为窄条 */
  width: 80px;
}
.admin-layout.sidebar-collapsed .sidebar-header h2,
.admin-layout.sidebar-collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none; /* 让隐藏的元素不可点击 */
}


.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  margin-left: 240px; /* 默认留出侧边栏的宽度 */
  transition: margin-left 0.3s ease;
}

/* 当侧边栏收起时，主内容区的左边距也随之变化 */
.admin-layout.sidebar-collapsed .content {
  margin-left: 80px;
}


/* 【新增】移动端遮罩层 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* ===================================================== */
/* 【核心】响应式布局: 当屏幕宽度小于 992px 时应用以下样式 */
/* ===================================================== */
@media (max-width: 992px) {
  .sidebar {
    /* 在移动端，侧边栏从屏幕外滑入 */
    transform: translateX(-100%);
  }
  
  .admin-layout:not(.sidebar-collapsed) .sidebar {
    /* 当不处于收起状态时，滑入屏幕 */
    transform: translateX(0);
  }

  .admin-layout.sidebar-collapsed .sidebar {
    /* 收起状态就是滑出屏幕 */
    transform: translateX(-100%);
  }
  
  .content {
    /* 在移动端，内容区始终占据全部宽度 */
    margin-left: 0;
  }

  /* 在移动端，切换按钮变为固定的汉堡菜单 */
  .sidebar-toggle {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 1001;
    background-color: var(--card-bg-color);
  }
  
  /* 当侧边栏收起时，按钮应该位于屏幕内；展开时，按钮位于侧边栏内 */
  .admin-layout:not(.sidebar-collapsed) .sidebar-toggle {
    left: calc(240px - 2rem - 16px); /* 动态计算位置 */
  }
}

.sidebar h2 {
  color: var(--accent-color);
  margin-top: 0;
}
.sidebar nav {
  display: flex;
  flex-direction: column;
}
.sidebar nav a {
  color: var(--primary-text-color);
  text-decoration: none;
  padding: 0.75rem 0;
  border-radius: 4px;
  transition: background-color 0.2s;
}
.sidebar nav a:hover {
  background-color: rgba(3, 218, 198, 0.1);
}
/* 当前激活路由的链接样式 */
.sidebar nav a.router-link-exact-active {
  color: var(--accent-color);
  font-weight: bold;
}
.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
.view-links hr {
  border-color: var(--border-color);
  margin: 1rem 0;
}

.view-links h4 {
  font-size: 0.9rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 0.75rem;
}

.view-link-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 48px;             /* 固定高度 */
  min-height: 48px;
  max-height: 48px;
  padding: 0 0.75rem;       /* 水平内边距，去掉上下内边距以固定高度 */
  margin-bottom: 0.5rem;
  border-radius: 4px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  text-decoration: none;
  transition: all 0.2s;
  overflow: hidden;         /* 防止内容撑高 */
}

/* 保持 hover 效果，但不要改变高度 */
.view-link-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* 图标尺寸和对齐，确保不影响按钮高度 */
.view-link-btn svg {
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  margin-left: 8px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

/* 文字区域超长时用省略号，不换行 */
.view-link-btn span {
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 48px;       /* 保持文字垂直居中 */
}
</style>