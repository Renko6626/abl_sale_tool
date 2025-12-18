from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from . import sale_bp
from .. import db
from ..models import Product, Event, MasterProduct
from werkzeug.utils import secure_filename
from ..auth_utils import jwt_required
# ... get_products_for_event 函数保持不变，但其内部 to_dict() 的行为已改变 ...
@sale_bp.route('/api/events/<int:event_id>/products', methods=['GET'])
def get_products_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    products = event.products
    return jsonify([product.to_dict() for product in products]), 200

# API: 通过编号为展会添加商品 (逻辑完全重写)
@sale_bp.route('/api/events/<int:event_id>/products', methods=['POST'])
@jwt_required(roles={'admin', 'vendor'}, require_event_match=True)
def add_product_to_event(event_id, jwt_payload=None):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()

    if not data or 'product_code' not in data or 'initial_stock' not in data:
        return jsonify(error="Missing required fields: product_code and initial_stock"), 400

    # 1. 通过编号在主商品库中查找商品
    master_product = MasterProduct.query.filter_by(product_code=data['product_code']).first()
    if not master_product:
        return jsonify(error=f"Product code '{data['product_code']}' not found."), 404
    # 【新增】检查
    if not master_product.is_active:
        return jsonify(error=f"Product '{master_product.name}' is inactive and cannot be added."), 400

    try:
        # 2. 创建展会商品 (库存) 实例
        new_product = Product(
            event_id=event.id,
            master_product_id=master_product.id,
            initial_stock=int(data['initial_stock']),
            # 3. 价格逻辑：如果请求中提供了价格，则使用它；否则，使用主商品的默认价格
            price=float(data.get('price', master_product.default_price))
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify(error=f"Product '{master_product.name}' has already been added to this event."), 409
    except (ValueError, TypeError):
        return jsonify(error="Invalid data type for price or initial_stock."), 400

# API: 更新展会商品的库存或价格 (逻辑简化)
@sale_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required(roles={'admin', 'vendor'})
def update_product(product_id, jwt_payload=None):
    product = Product.query.get_or_404(product_id)
    # Vendor只能更新自己的展会商品
    if jwt_payload and jwt_payload.get('role') == 'vendor' and jwt_payload.get('access') != 'all':
        if product.event_id != jwt_payload.get('event_id'):
            return jsonify(error="Forbidden: event not authorized"), 403
    data = request.get_json()
    try:
        if 'price' in data:
            product.price = float(data['price'])
        if 'initial_stock' in data:
            product.initial_stock = int(data['initial_stock'])
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except (ValueError, TypeError):
        return jsonify(error="Invalid data type for price or initial_stock."), 400

# ... delete_product 函数保持不变 ...
@sale_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@jwt_required(roles={'admin', 'vendor'})
def delete_product(product_id, jwt_payload=None):
    product = Product.query.get_or_404(product_id)
    if jwt_payload and jwt_payload.get('role') == 'vendor' and jwt_payload.get('access') != 'all':
        if product.event_id != jwt_payload.get('event_id'):
            return jsonify(error="Forbidden: event not authorized"), 403
    db.session.delete(product)
    db.session.commit()
    return '', 204