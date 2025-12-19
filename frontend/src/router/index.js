import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'; // 导入 auth store
// 导入所有需要的布局和视图
import AdminLayout from '../views/AdminLayout.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminMasterProducts from '../views/AdminMasterProducts.vue'
import AdminEventProducts from '../views/AdminEventProducts.vue'
import VendorEventSelection from '../views/VendorEventSelection.vue'; // 【新增】导入新视图
import VendorView from '../views/VendorView.vue'; // 这个现在是详情页
import CustomerView from '../views/CustomerView.vue'
import EventPortalView from '../views/EventPortalView.vue'
import AdminEventOrders from '../views/AdminEventOrders.vue'
import LoginView from '../views/LoginView.vue'
import AdminEventStat from '../views/AdminEventStat.vue';
import NotFound from '../views/NotFound.vue';
import ServerError from '../views/ServerError.vue';
const routes = [
    // --- 路由组 1: 管理后台 ---
    // 所有 /admin 开头的路径都会使用 AdminLayout 布局
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, role: 'admin' },
      // 管理后台的所有子页面
      children: [
        {
          path: '', // 默认 /admin 路径
          name: 'admin-dashboard',
          component: AdminDashboard,
        },
        {
          path: 'master-products',
          name: 'admin-master-products',
          component: AdminMasterProducts,
        },
        {
          path: 'events/:id/products',
          name: 'admin-event-products',
          component: AdminEventProducts,
          props: true,
        },
        // 【新增】订单管理路由
        {
          path: 'events/:id/orders',
          name: 'admin-event-orders',
          component: AdminEventOrders,
          props: true
        },
        // 【新增】销售统计路由
        {
        path: '/admin/events/:id/stats',
        name: 'AdminEventStats',
        component: AdminEventStat,
        }
      ],
    },

    // --- 路由组 2: 摊主页面 ---
    // 这是一个独立的顶层路由，不使用 AdminLayout
    {
      path: '/vendor',
      name: 'vendor-select',
      component: VendorEventSelection,
    },

    // 【修改】摊主的操作页面现在是一个动态路径
    {
      path: '/vendor/:id', // :id 是展会 ID
      name: 'vendor-detail',
      component: VendorView,
      props: true, // 将 id 作为 prop 传入 VendorView
      meta: { requiresAuth: true, role: 'vendor' },
    },


    // --- 路由组 3: 顾客点单页面 ---
    // 这也是一个独立的顶层路由，同样不使用 AdminLayout
    {
      path: '/events/:id/order', // 例如 /events/2/order
      name: 'customer-order',
      component: CustomerView,
      props: true // 将 :id 作为 prop 传递给 CustomerView
    },
    {
      path: '/',
      name: 'customer',
      component: EventPortalView,
    },
    {
    path: '/login/:role', // 动态角色：/login/admin 或 /login/vendor
    name: 'login',
    component: LoginView,
    props: true, // 将 :role 作为 prop 传给 LoginView
    },
    // --- 错误页 ---
    {
      path: '/error/500',
      name: 'server-error',
      component: ServerError,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFound,
    }
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  const requiresAuth = to.meta.requiresAuth;
  const requiredRole = to.meta.role;

  // 【临时调试】在守卫的入口打印状态
  console.log(`--- Router Guard: Navigating to ${to.path}. Requires auth? ${!!requiresAuth}. Current user role:`, authStore.user?.role);

  if (requiresAuth) {
    let hasPermission = false;
    if (requiredRole === 'admin' && authStore.isAdmin) {
      hasPermission = true;
    }
    
    if (requiredRole === 'vendor') {
      const eventId = to.params.id;
      if (authStore.canAccessVendorPage(eventId)) {
        hasPermission = true;
      }
    }

    if (hasPermission) {
      console.log('--- Router Guard: Permission GRANTED. Calling next().');
      next(); // 权限通过，放行
    } else {
      console.log('--- Router Guard: Permission DENIED. Redirecting to login.');
      next({ 
        name: 'login', 
        params: { role: requiredRole || 'vendor' }, // 提供一个默认角色
        query: { redirect: to.fullPath, eventId: to.params.id }
      });
    }
  } else {
    next(); // 页面不需要认证，直接放行
  }
});
export default router