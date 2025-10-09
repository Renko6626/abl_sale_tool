from flask import request, jsonify
from datetime import datetime
from . import sale_bp
from .. import db
from ..models import Event
import uuid
from werkzeug.utils import secure_filename
import os
from flask import current_app

VALID_STATUSES = ["未进行", "进行中", "已结束"]

# --- 辅助函数：安全地删除文件 ---
def delete_file(file_url):
    """根据文件的相对URL安全地删除服务器上的文件"""
    if not file_url:
        return
    try:
        # 将 URL (/static/uploads/...) 转换为文件系统路径 (app/static/uploads/...)
        # lstrip('/') 防止 os.path.join 行为异常
        file_path = os.path.join(current_app.static_folder, file_url.lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # 记录错误，但不中断主流程
        print(f"Error deleting file {file_url}: {e}")


# --- 展会管理 API ---

@sale_bp.route('/api/events', methods=['GET'])
def get_events():
    status_filter = request.args.get('status')
    query = Event.query

    if status_filter in VALID_STATUSES:
        query = query.filter(Event.status == status_filter)

    events = query.order_by(Event.date.desc()).all()
    return jsonify([event.to_dict() for event in events]), 200

@sale_bp.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """获取单个展会信息"""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict()), 200

@sale_bp.route('/api/events', methods=['POST'])
def create_event():
    data = request.form
    if not data or 'name' not in data or 'date' not in data:
        return jsonify(error="Missing required fields: name and date"), 400

    qr_code_url = None

    if 'payment_qr_code' in request.files:
        file = request.files['payment_qr_code']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            qr_code_url = f"/static/uploads/{unique_filename}"

    try:
        new_event = Event(
            name=data['name'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            location=data.get('location', ''),
            vendor_password=data.get('vendor_password'),
            # 【修正】确保这里的字段名与你的 Event 模型中的定义一致
            qrcode_url=qr_code_url 
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify(new_event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        if qr_code_url:
             # 如果数据库出错，删除已上传的文件
             delete_file(qr_code_url)
        return jsonify(error=str(e)), 500

@sale_bp.route('/api/events/<int:event_id>/status', methods=['PUT'])
def update_event_status(event_id):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status or new_status not in VALID_STATUSES:
        return jsonify(error=f"Invalid or missing status. Must be one of: {', '.join(VALID_STATUSES)}"), 400

    event = Event.query.get_or_404(event_id)
    event.status = new_status
    db.session.commit()
    
    return jsonify(event.to_dict()), 200


# 【已修改】API: 更新展会信息，现在支持图片上传
@sale_bp.route('/api/events/<int:event_id>', methods=['PUT', 'POST'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    # 【修改】从 request.form 获取文本数据
    data = request.form
    
    try:
        # 1. 更新文本字段
        event.name = data.get('name', event.name)
        if 'date' in data:
            event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        event.location = data.get('location', event.location)
        # 允许密码字段更新为空字符串
        if 'vendor_password' in data:
            event.vendor_password = data['vendor_password']

        # 2. 处理图片移除逻辑
        if data.get('remove_payment_qr_code') == 'true':
            # 删除旧文件并将数据库字段设为 null
            delete_file(event.payment_qr_code_url)
            event.qrcode_url = None

        # 3. 处理新图片上传逻辑
        if 'payment_qr_code' in request.files:
            file = request.files['payment_qr_code']
            if file and file.filename != '':
                # 如果有新图片，先删除旧的
                delete_file(event.qrcode_url)
                
                # 保存新图片
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(save_path)
                
                # 更新数据库中的 URL
                event.qrcode_url = f"/static/uploads/{unique_filename}"

        db.session.commit()
        return jsonify(event.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

#删除展会
@sale_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        # 删除相关的二维码图片文件
        delete_file(event.qrcode_url)
        
        db.session.delete(event)
        db.session.commit()
        return jsonify(message="Event deleted"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500