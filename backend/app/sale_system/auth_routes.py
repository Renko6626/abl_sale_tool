from flask import request, jsonify, current_app
from . import sale_bp
from ..models import Event

@sale_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')
    role = data.get('role') # 'admin' or 'vendor'
    event_id = data.get('eventId') # 可选的 eventId

    if not password or not role:
        return jsonify(error="Missing password or role"), 400

    admin_pass = current_app.config['ADMIN_PASSWORD']
    global_vendor_pass = current_app.config['VENDOR_PASSWORD']

    # --- 1. 管理员登录 ---
    if role == 'admin':
        if password == admin_pass:
            # 管理员登录成功，赋予 admin 角色
            return jsonify(message="Admin login successful", role="admin"), 200
        else:
            return jsonify(error=f"Invalid admin password :("), 401

    # --- 2. 摊主登录 ---
    if role == 'vendor':
        # 摊主可以用管理员密码登录任何展会
        if password == admin_pass:
            return jsonify(message="Admin login as vendor successful", role="vendor", eventId=event_id), 200
        
        # 或者用全局摊主密码登录
        if password == global_vendor_pass:
            return jsonify(message="Global vendor login successful", role="vendor", eventId=event_id), 200

        # 如果提供了 eventId，尝试用展会专属密码登录
        if event_id:
            event = Event.query.get(event_id)
            if event and event.vendor_password and password == event.vendor_password:
                return jsonify(message="Event-specific vendor login successful", role="vendor", eventId=event_id), 200

        # 如果所有摊主密码验证都失败
        return jsonify(error="Invalid vendor password"), 401

    return jsonify(error="Invalid role specified"), 400