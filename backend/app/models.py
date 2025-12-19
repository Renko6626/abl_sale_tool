from datetime import datetime, timedelta
from . import db
from sqlalchemy import UniqueConstraint

# Event (展会) 模型
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(128))
    # 新增的 status 列，有默认值和索引
    status = db.Column(db.String(64), default='未进行', index=True, nullable=False)
    
    products = db.relationship('Product', backref='event', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='event', lazy=True, cascade="all, delete-orphan")
    vendor_password = db.Column(db.String(128), nullable=True) # nullable=True 表示可以为空 

    qrcode_url=db.Column(db.String(256),nullable=True)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat(),
            'location': self.location,
            'status': self.status,  # 直接从数据库字段读取 status
            'qrcode_url':self.qrcode_url
        }

# 【新增】MasterProduct (主商品) 模型
# 这是您的全局商品库
class MasterProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    default_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    # 反向关系，可以找到所有使用此模板的展会商品
    products = db.relationship('Product', backref='master_product', lazy=True, cascade="all, delete-orphan")

    category = db.Column(db.String(64), nullable=True, index=True)  # 新增分类字段
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_code': self.product_code,
            'name': self.name,
            'default_price': self.default_price,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'category': self.category
        }

# 【重大修改】Product (展会商品) 模型
# 现在它更像是一个“库存”记录，链接了“哪个展会”和“哪个主商品”
class Product(db.Model):
    # ... id, price, initial_stock, event_id, master_product_id, __table_args__ 保持不变 ...
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    initial_stock = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    master_product_id = db.Column(db.Integer, db.ForeignKey('master_product.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('event_id', 'master_product_id', name='_event_master_product_uc'),
    )

    # 【新增】计算属性：已售出数量
    @property
    def sold_count(self):
        """只计算已完成订单中的销量"""
        from .models import Order, OrderItem 
        count = db.session.query(db.func.sum(OrderItem.quantity)).join(Order).filter(
            OrderItem.product_id == self.id,
            Order.status == 'completed'
        ).scalar()
        return count or 0

    # 【新增】计算属性：当前库存
    @property
    def current_stock(self):
        """当前库存 = 初始库存 - 已售出数量"""
        return self.initial_stock - self.sold_count
    @property
    def name(self):
        return self.master_product.name if self.master_product else "未知商品"

    def to_dict(self):
        # 通过关系，将主商品的信息和本次展会的信息组合在一起返回
        return {
            'id': self.id,
            'master_product_id': self.master_product_id,
            'product_code': self.master_product.product_code,
            'name': self.master_product.name,
            'price': self.price,
            'initial_stock': self.initial_stock,
            'current_stock': self.current_stock, # 【新增】在 API 响应中加入当前库存
            'image_url': self.master_product.image_url,
            'event_id': self.event_id,
            'category': self.master_product.category
        }

# Order (订单) 模型
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 记录为北京时间 (UTC+8)
    def _beijing_now():
        return datetime.utcnow() + timedelta(hours=8)

    timestamp = db.Column(db.DateTime, index=True, default=_beijing_now)
    status = db.Column(db.String(64), default='pending') # pending, completed, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'total_amount': self.total_amount,
            'event_id': self.event_id,
            'items': [item.to_dict() for item in self.items]
        }


# OrderItem (订单项) 模型
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    # 建立与 Product 的关系，以便轻松获取商品信息
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'product_id': self.product_id,
            'product_name': self.product.master_product.name, 
            'product_price': self.product.price,
            'product_image_url': self.product.master_product.image_url 
        }