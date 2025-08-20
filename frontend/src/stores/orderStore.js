import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';

export const useOrderStore = defineStore('order', () => {
  const pendingOrders = ref([]);
  // 【新增】存储已完成订单列表
  const completedOrders = ref([]); 
  const activeEventId = ref(null);
  let pollingInterval = null;
  // 【新增】设置当前活动的展会
  function setActiveEvent(eventId) {
    stopPolling(); // 切换展会时，先停止旧的轮询
    activeEventId.value = eventId;
    pendingOrders.value = []; // 清空旧的订单列表
    if (eventId) {
      startPolling(); // 如果设置了新的 eventId，则开始新的轮询
    }
  }

  async function pollPendingOrders() {
    if (!activeEventId.value) return; // 如果没有活动展会，则不执行

    try {
      const response = await api.get(`/events/${activeEventId.value}/orders?status=pending`);
      
      const oldOrderCount = pendingOrders.value.length;
      if (JSON.stringify(pendingOrders.value) !== JSON.stringify(response.data)) {
        pendingOrders.value = response.data;
        if (response.data.length > oldOrderCount) {
          const audio = new Audio('/notification.mp3');
          audio.play();
        }
      }
    } catch (err) {
      console.error("Polling failed:", err);
      // 如果获取失败（比如展会不存在），停止轮询避免无限报错
      stopPolling();
    }
  }

  function startPolling() {
    if (pollingInterval) stopPolling(); // 防止重复启动
    pollPendingOrders();
    pollingInterval = setInterval(pollPendingOrders, 3000);
  }

  function stopPolling() {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }

  async function markOrderAsCompleted(orderId) {
    if (!activeEventId.value) return;
    try {
      const response = await api.put(`/events/${activeEventId.value}/orders/${orderId}/status`, { status: 'completed' });
      // 更新成功后，将该订单从 pending 移到 completed
      const completedOrder = pendingOrders.value.find(order => order.id === orderId);
      if (completedOrder) {
          completedOrders.value.unshift(completedOrder);
      }
      pendingOrders.value = pendingOrders.value.filter(order => order.id !== orderId);
      
      // 注意：为了实时更新库存，我们可能需要重新获取商品列表
      // (这个逻辑放在组件里更合适)

    } catch (err) {
      console.error(err);
      throw new Error("更新订单状态失败。");
    }
  }
  async function fetchCompletedOrders() {
    if (!activeEventId.value) return;
    try {
      const response = await api.get(`/events/${activeEventId.value}/orders?status=completed`);
      completedOrders.value = response.data;
    } catch (err) {
      console.error("Failed to fetch completed orders:", err);
    }
  }
  async function cancelOrder(orderId) {
    if (!activeEventId.value) return;
    try {
      // 调用同一个 API 端点，但传入不同的状态
      await api.put(`/events/${activeEventId.value}/orders/${orderId}/status`, { status: 'cancelled' });
      
      // 取消成功后，同样从待处理列表中移除该订单
      // 我们不需要把它加入已完成列表，所以它就直接消失了
      pendingOrders.value = pendingOrders.value.filter(order => order.id !== orderId);

    } catch (err) {
      console.error(err);
      throw new Error("取消订单失败。");
    }
  }
  const totalRevenue = computed(() => {
    return completedOrders.value.reduce((total, order) => total + order.total_amount, 0);
  });

  return { 
    pendingOrders,
    completedOrders,
    totalRevenue,
    activeEventId,
    setActiveEvent,
    markOrderAsCompleted,
    fetchCompletedOrders,
    cancelOrder,
    pollPendingOrders,
    startPolling,
    stopPolling
  };
});