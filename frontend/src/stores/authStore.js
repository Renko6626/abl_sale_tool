import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';
// 【重要】确保导入了 router 实例
import router from '@/router';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(sessionStorage.getItem('user')) || null);

  const isAdmin = computed(() => user.value?.role === 'admin');

  const canAccessVendorPage = (eventId) => {
    // 确保 eventId 是数字类型以便比较
    const numericEventId = eventId ? parseInt(eventId, 10) : null;

    if (!user.value || user.value.role !== 'vendor') return false;
    
    // 管理员密码或全局密码登录时，可以访问所有展会
    if (user.value.access === 'all') return true;
    
    // 展会专属密码登录时，检查 ID 是否匹配
    return user.value.authorizedEventId === numericEventId;
  };

  async function login(password, role, eventId, redirectPath) {
    try {
        // 1. 【核心改动】将 eventId 包含在发送给后端的数据中
        const response = await api.post('/auth/login', { password, role, eventId });
        const responseData = response.data;
        
        // 2. 根据后端返回的数据，构建并更新前端的用户状态对象
        const userData = {
          role: responseData.role,
          access: responseData.access || 'all',
        };

        if (responseData.role === 'vendor' && responseData.access === 'event') {
          userData.authorizedEventId = responseData.eventId ? parseInt(responseData.eventId, 10) : null;
        }
        if (responseData.role === 'vendor' && responseData.access === 'all') {
          userData.authorizedEventId = null;
        }

        user.value = userData;
        sessionStorage.setItem('user', JSON.stringify(userData));

        // 3. 执行跳转
        const finalRedirectPath = redirectPath || (userData.role === 'admin' ? '/admin' : '/');
        await router.push(finalRedirectPath);
        
        return true;

    } catch (error) {
        console.error("Login failed:", error);
        user.value = null;
        sessionStorage.removeItem('user');
        throw new Error(error.response?.data?.error || '登录失败，请检查密码。');
    }
  }
  function logout() {
    user.value = null;
    sessionStorage.removeItem('user');
    router.push('/');
  }

  // 确保返回了所有需要的方法和状态
  return { user, isAdmin, login, logout, canAccessVendorPage };
});