<template>
  <div class="list-container">
    <h2>展会列表</h2>

    <!-- 搜索和过滤区域（Naive UI） -->
    <div class="search-container">
      <n-space wrap align="end" :size="16">
        <div class="search-group">
          <label for="search-name">按名称搜索:</label>
          <n-input
            id="search-name"
            v-model:value="searchName"
            clearable
            placeholder="输入展会名称关键字..."
          />
        </div>
        <div class="search-group">
          <label for="search-date-start">日期范围:</label>
          <div class="date-range-inputs">
            <n-date-picker
              id="search-date-start"
              v-model:value="dateRangeStart"
              type="date"
              clearable
              value-format="yyyy-MM-dd"
            />
            <span>至</span>
            <n-date-picker
              id="search-date-end"
              v-model:value="dateRangeEnd"
              type="date"
              clearable
              value-format="yyyy-MM-dd"
            />
          </div>
        </div>
        <n-button tertiary @click="clearFilters">清空筛选</n-button>
      </n-space>
    </div>

    <div v-if="store.isLoading" class="loading-message">正在加载展会数据...</div>
    <div v-else-if="store.error" class="error-message">{{ store.error }}</div>
    
    <!-- 【修改】v-for 循环现在使用 filteredEvents 计算属性 -->
    <ul v-else-if="filteredEvents.length" class="event-list">
      <RouterLink
      v-for="event in filteredEvents"
      :key="event.id"
      :to="`/admin/events/${event.id}/products`"
      custom
      v-slot="{ navigate }"
      >
      <li @click="navigate" class="event-card clickable" role="link">
        <n-card :title="event.name" :hoverable="true" embedded>
          <div class="event-info">
            <p>日期: {{ event.date }}</p>
            <p>地点: {{ event.location || '未指定' }}</p>
          </div>
          <template #header-extra>
            <n-tag :type="statusType(event.status)" size="small">{{ event.status }}</n-tag>
          </template>
          <template #footer>
            <div class="status-actions">
              <n-button v-if="event.status === '未进行'" size="small" @click.stop="changeStatus(event.id, '进行中')">► 开始</n-button>
              <n-button v-if="event.status === '进行中'" size="small" @click.stop="changeStatus(event.id, '已结束')">■ 结束</n-button>
              <n-button v-if="event.status === '已结束'" size="small" @click.stop="changeStatus(event.id,'未进行')">► 重新开始</n-button>
              <n-button size="small" type="primary" @click.stop="openEditModal(event)">编辑</n-button>
              <n-button size="small" type="error" @click.stop="confirmDelete(event.id)">删除</n-button>
            </div>
          </template>
        </n-card>
      </li>
      </RouterLink>
    </ul>

    <!-- 【修改】处理“无搜索结果”和“无任何展会”两种情况 -->
    <p v-else-if="store.events.length && !filteredEvents.length" class="no-results-message">
      没有找到符合筛选条件的展会。
    </p>
    <p v-else>
      还没有任何展会，请在上方创建一个。
    </p>


    <!-- 编辑模态框 (保持不变) -->
    <AppModal :show="isEditModalVisible" @close="closeEditModal">
      <template #header><h3>编辑展会</h3></template>
      <template #body><EditEventForm v-if="selectedEvent" ref="editForm" :event="selectedEvent" /></template>
      <template #footer>
        <button type="button" class="btn" @click="closeEditModal">取消</button>
        <button type="button" class="btn btn-primary" @click="handleUpdateEvent">保存更改</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import { useEventStore } from '@/stores/eventStore';
import AppModal from '@/components/shared/AppModal.vue';
import EditEventForm from '@/components/event/EditEventForm.vue';
import { RouterLink } from 'vue-router';
import { NInput, NDatePicker, NButton, NCard, NSpace, NTag } from 'naive-ui';

const store = useEventStore();
const updatingStatusId = ref(null);

// =======================================================
// 【新增】搜索和过滤相关的状态
// =======================================================
const searchName = ref('');
const dateRangeStart = ref(null);
const dateRangeEnd = ref(null);
const filteredEvents = computed(() => {
  // 从原始列表开始
  let events = store.events;

  // 1. 按名称过滤
  if (searchName.value.trim()) {
    const lowerCaseQuery = searchName.value.toLowerCase();
    events = events.filter(event =>
      event.name.toLowerCase().includes(lowerCaseQuery)
    );
  }

  // 2. 按开始日期过滤
  if (dateRangeStart.value) {
    events = events.filter(event => new Date(event.date) >= new Date(dateRangeStart.value));
  }

  // 3. 按结束日期过滤
  if (dateRangeEnd.value) {
    // 创建一个 Date 对象并设置到当天的最后一刻，以确保包含选定的结束日期
    const endDate = new Date(dateRangeEnd.value);
    endDate.setHours(23, 59, 59, 999);
    events = events.filter(event => new Date(event.date) <= endDate);
  }

  return events;
});

// 【新增】清空所有筛选条件的函数
function clearFilters() {
  searchName.value = '';
  dateRangeStart.value = null;
  dateRangeEnd.value = null;
}

// 【新增】编辑模态框相关的状态
const isEditModalVisible = ref(false);
const selectedEvent = ref(null);
const editForm = ref(null); // 用于获取 EditEventForm 组件的实例

onMounted(() => {
  store.fetchEvents();
});

const statusClass = (status) => {
  return {
    'status-ongoing': status === '进行中',
    'status-finished': status === '已结束',
    'status-upcoming': status === '未进行',
  };
};
const statusType = (status) => {
  if (status === '进行中') return 'warning';
  if (status === '已结束') return 'default';
  return 'success'; // 未进行
};
async function confirmDelete(eventId) {
  // 弹出浏览器原生确认框
  if (window.confirm('您确定要删除这个展会吗？此操作无法撤销。')) {
    try {
      // 调用 store 中的 deleteEvent 方法执行删除操作
      // 您需要在 eventStore.js 中实现 deleteEvent 方法，
      // 该方法会向后端发送 DELETE 请求。
      await store.deleteEvent(eventId);
      // 可选：删除成功后显示提示
      // alert('展会已删除');
    } catch (error) {
      // 显示错误信息
      alert(error.message || '删除失败，请稍后再试。');
    }
  }
}
// 【新增】处理状态变更的函数
async function changeStatus(eventId, newStatus) {
  // 防止重复点击
  if (updatingStatusId.value) return;

  updatingStatusId.value = eventId;
  try {
    await store.updateEventStatus(eventId, newStatus);
  } catch (error) {
    // 如果 store 抛出错误，在这里通知用户
    alert(error.message);
  } finally {
    // 无论成功或失败，最后都清除更新中的状态
    updatingStatusId.value = null;
  }
}
function openEditModal(event) {
  selectedEvent.value = event;
  isEditModalVisible.value = true;
}

// 【新增】关闭编辑模态框的函数
function closeEditModal() {
  isEditModalVisible.value = false;
  selectedEvent.value = null;
}

// 【新增】处理更新提交的函数
async function handleUpdateEvent() {
  // 增加对 selectedEvent 的检查，更安全
  if (editForm.value && selectedEvent.value) { 
    const formData = editForm.value.submit();
    if (formData) {
      try {
        // 【核心修正】
        // 第一个参数传入 event ID
        // 第二个参数传入 FormData
        console.log('尝试进行更新')
        await store.updateEvent(selectedEvent.value.id, formData);
        console.log('更新成功');
        closeEditModal(); // 成功后关闭模态框
      } catch (error) {
        alert(error.message); // 显示错误
      }
    }
  }
}
</script>

<style scoped>
.event-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* 每个卡片为独立长条 */
.event-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 16px;     /* 卡片之间的间距 */
  box-shadow: 0 6px 10px rgba(0,0,0,0.04);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
  cursor: default;         /* clickable 类会改为 pointer */
  min-height: 72px;     /* 保持卡片高度一致 */
}

/* 保持原有 clickable 行为（整行可点击） */
.event-card.clickable {
  cursor: pointer;
}
.event-card.clickable:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(16,24,40,0.10);
}
/* 左侧信息区域占满剩余空间 */
.event-info {
  flex: 1 1 auto;
  min-width: 0;            /* 保证文本可以正确换行 */
}
.event-info h3 {
  margin: 0 0 6px 0;
  font-size: 1.2rem;
  line-height: 1.25;
  font-weight: 700;
}
.event-info p {
  margin: 0;
  color: var(--secondary-text-color, #888);
  font-size: 1rem;
  line-height: 1.3;
}

/* 右侧状态与操作区固定宽度，垂直居中 */
.event-status {
  flex: 0 0 240px;         /* 根据需要调整宽度 */
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  text-align: right;
}

/* 状态徽章样式 */
.status-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--primary-text-color);
  border: 1px solid transparent;
}

/* 状态颜色类（保留现有类名） */
.status-ongoing { background: rgba(255, 223, 87, 0.12); border-color: rgba(255, 223, 87, 0.25); }
.status-finished { background: rgba(108, 117, 125, 0.08); border-color: rgba(108, 117, 125, 0.18); }
.status-upcoming { background: rgba(3,218,198,0.08); border-color: rgba(3,218,198,0.18); }

.status-actions {
  margin-top: 0.5rem;
  /* 【新增】让按钮之间有一点间距 */
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.action-btn {
  background: none;
  border: 1px solid var(--primary-text-color);
  color: var(--primary-text-color);
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}
.action-btn:hover {
  background-color: var(--primary-text-color);
  color: var(--bg-color);
}
.event-card.clickable {
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}
.event-card.clickable:hover {
  background-color: rgba(3, 218, 198, 0.05);
  border-color: rgba(3, 218, 198, 0.3);
}
.delete-btn {
  border-color: #dc3545; /* 红色边框 */
  color: #dc3545;       /* 红色文字 */
}

.delete-btn:hover {
  background-color: #dc3545; /* 悬停时红色背景 */
  color: white;              /* 悬停时白色文字 */
}
.search-container {
  background-color: var(--card-bg-color);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-color);
  display: flex;
  flex-wrap: wrap; /* 在小屏幕上换行 */
  gap: 1rem;
  align-items: flex-end; /* 让元素底部对齐 */
}

.search-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-grow: 1; /* 让组占据可用空间 */
}

.search-group label {
  font-size: 0.9rem;
  color: #aaa;
}

.search-group input[type="text"],
.search-group input[type="date"] {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  padding: 8px;
  border-radius: 4px;
  font-size: 1rem;
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-range-inputs span {
  color: #aaa;
}

.btn-secondary {
  background-color: #555;
  border-color: #555;
  color: white;
  padding: 8px 12px;
  height: fit-content; /* 让按钮高度与输入框匹配 */
}
.btn-secondary:hover {
  background-color: #666;
}
.no-results-message {
  text-align: center;
  padding: 2rem;
  color: #888;
}
</style>