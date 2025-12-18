from flask import jsonify
from . import sale_bp
from .. import db
from ..models import Event, Order, OrderItem, Product
from ..auth_utils import jwt_required

# --- 数据统计 API ---

# API: 获取指定展会的销售统计数据
# 路径: GET /sale/api/events/<int:event_id>/stats
@sale_bp.route('/api/events/<int:event_id>/stats', methods=['GET'])
@jwt_required(roles={'admin', 'vendor'}, require_event_match=True)
def get_event_stats(event_id, jwt_payload=None):
    # 确认展会存在
    event = Event.query.get_or_404(event_id)

    # 1. --- 计算展会总体摘要 (Summary) ---
    
    # 构建一个只包含 "已完成" 订单的基础查询
    completed_orders_query = Order.query.filter_by(event_id=event_id, status='completed')

    # 计算总营业额
    total_revenue = completed_orders_query.with_entities(db.func.sum(Order.total_amount)).scalar() or 0.0

    # 计算已完成订单总数
    completed_orders_count = completed_orders_query.count()

    # 计算总售出件数
    total_items_sold = db.session.query(db.func.sum(OrderItem.quantity)).join(Order).filter(
        Order.event_id == event_id,
        Order.status == 'completed'
    ).scalar() or 0
    
    summary = {
        "total_revenue": round(total_revenue, 2), # 保留两位小数
        "completed_orders_count": completed_orders_count,
        "total_items_sold": total_items_sold
    }

    # 2. --- 计算各商品的详细销售情况 ---
    
    product_details = []
    # 获取该展会的所有商品
    products_for_event = Product.query.filter_by(event_id=event_id).all()

    for product in products_for_event:
        # 我们之前在 models.py 中定义的 sold_count 和 current_stock 属性在这里派上了大用场！
        sold_count = product.sold_count
        
        details = {
            "product_id": product.id,
            "product_code": product.master_product.product_code,
            "name": product.master_product.name,
            "price": product.price,
            "initial_stock": product.initial_stock,
            "sold_count": sold_count,
            "current_stock": product.current_stock,
            "revenue": round(sold_count * product.price, 2) # 该商品产生的收入
        }
        product_details.append(details)

    # 3. --- 组合成最终的响应 ---
    
    return jsonify({
        "event_info": event.to_dict(),
        "summary": summary,
        "product_details": product_details
    })