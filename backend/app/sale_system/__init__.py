# --- backend/app/sale_system/__init__.py ---
from flask import Blueprint

# 1. 创建蓝图实例
sale_bp = Blueprint('sale_system', __name__)

# 2. 【关键】导入该蓝图下的所有路由和事件文件
#    这一步告诉 sale_bp：“你的功能都在这些文件里”。
#    Python 在执行这几行时，会加载这些文件，
#    从而让 @sale_bp.route() 和 @socketio.on() 装饰器得以执行和注册。

from . import event_routes
from . import master_product_routes
from . import product_routes
from . import order_routes
from . import stats_routes
from . import auth_routes
# 局域网连接信息
from . import local_apply