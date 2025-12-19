import os
import time
from flask import request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from PIL import Image
from . import sale_bp
from .. import db
from ..models import MasterProduct
from ..auth_utils import jwt_required

# --- 配置 ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """检查文件名是否具有允许的扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 辅助函数 ---

def delete_file(file_url):
    """【新增】根据文件的相对URL安全地删除服务器上的文件"""
    if not file_url:
        return
    try:
        # 将 URL (/static/uploads/...) 转换为文件系统路径 (app/static/uploads/...)
        # 使用 file_url[1:] 或 lstrip('/') 来移除开头的斜杠
        file_path = os.path.join(current_app.root_path, 'static', file_url.split('/static/')[-1])
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Successfully deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_url}: {e}")

def process_and_save_image(file_stream, file_type='product'):
    """处理图片：压缩、转换为 WebP 并保存到对应目录"""
    try:
        img = Image.open(file_stream).convert("RGB")
        timestamp = int(time.time() * 1000)
        output_filename = f"{timestamp}.webp"
        
        # 根据文件类型选择保存目录
        if file_type == 'product':
            save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        elif file_type == 'qrcode':
            save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'qrcodes')
        elif file_type == 'event':
            save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events')
        else:
            save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
        
        # 确保目录存在
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, output_filename)
        
        # 保存图片
        img.save(save_path, 'webp', quality=60)
        
        # 返回相对路径
        relative_path = os.path.relpath(save_path, current_app.config['STATIC_FOLDER'])
        return f"/static/{relative_path}"
        
    except Exception as e:
        print(f"Image processing error: {e}")
        return None

# --- API 路由 ---

@sale_bp.route('/api/master-products', methods=['GET'])
def get_master_products():
    show_all = request.args.get('all', 'false').lower() == 'true'
    query = MasterProduct.query
    if not show_all:
        query = query.filter_by(is_active=True)
    products = query.order_by(MasterProduct.product_code).all()
    return jsonify([p.to_dict() for p in products])

@sale_bp.route('/api/master-products/<int:mp_id>/status', methods=['PUT'])
@jwt_required(roles={'admin'})
def update_master_product_status(mp_id, jwt_payload=None):
    mp = MasterProduct.query.get_or_404(mp_id)
    data = request.get_json()
    if 'is_active' not in data or not isinstance(data['is_active'], bool):
        return jsonify(error="Invalid request: 'is_active' (boolean) is required."), 400
    mp.is_active = data['is_active']
    db.session.commit()
    return jsonify(mp.to_dict()), 200

@sale_bp.route('/api/master-products', methods=['POST'])
@jwt_required(roles={'admin'})
def create_master_product(jwt_payload=None):
    data = request.form
    # 裁剪并校验必填字段，避免空字符串进入数据库
    product_code = (data.get('product_code') or '').strip()
    name = (data.get('name') or '').strip()
    default_price_raw = data.get('default_price')
    default_price_str = (str(default_price_raw).strip() if default_price_raw is not None else '')

    if not product_code or not name or not default_price_str:
        return jsonify(error="Missing required fields: product_code, name, default_price"), 400

    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            image_url = process_and_save_image(file.stream)
            if not image_url:
                return jsonify(error="Image processing failed."), 500
    try:
        new_mp = MasterProduct(
            product_code=product_code,
            name=name,
            default_price=float(default_price_str),
            image_url=image_url,
            category=data.get('category', None) # 【新增】分类字段
        )
        db.session.add(new_mp)
        db.session.commit()
        return jsonify(new_mp.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify(error=f"Product code '{product_code}' already exists."), 409
    except Exception as e:
        db.session.rollback()
        # 【新增】如果数据库出错，删除已上传的文件
        delete_file(image_url)
        return jsonify(error=str(e)), 500

# 【已修改】API: 更新一个主商品，支持图片移除和替换
@sale_bp.route('/api/master-products/<int:mp_id>', methods=['POST', 'PUT'])
@jwt_required(roles={'admin'})
def update_master_product(mp_id, jwt_payload=None):
    mp = MasterProduct.query.get_or_404(mp_id)
    data = request.form

    try:
        # 1. 更新文本字段
        mp.product_code = data.get('product_code', mp.product_code)
        mp.name = data.get('name', mp.name)
        mp.category = data.get('category', mp.category)

        print("DEBUG: Received data for update:", data)
        if 'default_price' in data:
            mp.default_price = float(data['default_price'])


        # 2. 处理图片移除逻辑
        if data.get('remove_image') == 'true':
            delete_file(mp.image_url)
            mp.image_url = None
        
        # 3. 处理新图片上传逻辑 (替换)
        if 'image' in request.files:
            print("DEBUG: Received image file for update")
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # 先删除旧图片
                delete_file(mp.image_url)
                # 保存新图片并更新 URL
                mp.image_url = process_and_save_image(file.stream)
                if not mp.image_url:
                    return jsonify(error="Image processing failed during update."), 500
        
        db.session.commit()
        return jsonify(mp.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify(error=f"Product code '{data.get('product_code')}' already exists."), 409
    except (ValueError, TypeError):
        return jsonify(error="Invalid data type for price."), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500