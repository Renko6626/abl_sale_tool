import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
// 【修改】同时导入默认的 apiClient 和具名的 getApiBaseUrl
import api, { getApiBaseUrl } from '@/services/api'; 

export const useEventStatStore = defineStore('eventStat', () => {
  // --- State ---
  const stats = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const activeEventId = ref(null);

  // --- Getters (Computed Properties) ---

  // 【修改】使用 getApiBaseUrl 来动态构建下载链接
  const downloadUrl = computed(() => {
    if (activeEventId.value) {
      const baseUrl = getApiBaseUrl(); // <-- 从 api.js 获取基础路径
      // 拼接成一个完整的、在任何环境下都正确的绝对或相对URL
      return `${baseUrl}/events/${activeEventId.value}/sales_summary/download`;
    }
    return '#'; // 如果没有 eventId，返回一个无害的链接
  });

  // --- Actions ---
  // ... (您的 setActiveEvent 和 fetchStats 函数保持不变) ...

  async function setActiveEvent(eventId, filters = {}) {
    if (activeEventId.value === eventId && !filters.forceReload) return;
    activeEventId.value = eventId;
    stats.value = null;
    if (eventId) {
      await fetchStats(filters);
    }
  }

  async function fetchStats({ productCode, startDate, endDate, intervalMinutes } = {}) {
    if (!activeEventId.value) {
      error.value = "没有提供展会ID。";
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      // api.get 会自动使用正确的 baseURL，所以这里不用变
      const response = await api.get(`/events/${activeEventId.value}/sales_summary`, {
        params: {
          product_code: productCode || undefined,
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          interval_minutes: intervalMinutes || undefined,
        },
      });
      stats.value = response.data;
    } catch (err) {
      console.error("获取销售统计失败:", err);
      if (err.response && err.response.status === 404) {
          error.value = "无法找到该展会或该展会暂无销售数据。";
      } else {
          error.value = "加载销售统计时发生网络错误。";
      }
      stats.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    stats,
    isLoading,
    error,
    activeEventId,
    downloadUrl, // <-- getter
    setActiveEvent,
    fetchStats,
  };
});