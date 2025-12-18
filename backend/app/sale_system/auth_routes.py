from flask import request, jsonify, current_app, make_response
from . import sale_bp
from ..models import Event
from ..auth_utils import generate_access_token

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
        if password != admin_pass:
            return jsonify(error="Invalid admin password"), 401
        token = generate_access_token(role='admin', access='all')
        resp = make_response(jsonify(message="Admin login successful", role="admin", access="all"), 200)
        resp.set_cookie(
            current_app.config['JWT_COOKIE_NAME'],
            token,
            httponly=True,
            secure=current_app.config['JWT_COOKIE_SECURE'],
            samesite=current_app.config['JWT_COOKIE_SAMESITE'],
            max_age=current_app.config['JWT_ACCESS_EXPIRES_MIN'] * 60,
        )
        return resp

    # --- 2. 摊主登录 ---
    if role == 'vendor':
        # 摊主可以用管理员密码或全局密码登录任何展会
        if password in (admin_pass, global_vendor_pass):
            token = generate_access_token(role='vendor', access='all')
            resp = make_response(jsonify(message="Vendor login successful", role="vendor", access="all"), 200)
            resp.set_cookie(
                current_app.config['JWT_COOKIE_NAME'],
                token,
                httponly=True,
                secure=current_app.config['JWT_COOKIE_SECURE'],
                samesite=current_app.config['JWT_COOKIE_SAMESITE'],
                max_age=current_app.config['JWT_ACCESS_EXPIRES_MIN'] * 60,
            )
            return resp

        # 如果提供了 eventId，尝试用展会专属密码登录
        if event_id:
            event = Event.query.get(event_id)
            if event and event.vendor_password and password == event.vendor_password:
                token = generate_access_token(role='vendor', access='event', event_id=int(event_id))
                resp = make_response(jsonify(message="Vendor login successful", role="vendor", access="event", eventId=event_id), 200)
                resp.set_cookie(
                    current_app.config['JWT_COOKIE_NAME'],
                    token,
                    httponly=True,
                    secure=current_app.config['JWT_COOKIE_SECURE'],
                    samesite=current_app.config['JWT_COOKIE_SAMESITE'],
                    max_age=current_app.config['JWT_ACCESS_EXPIRES_MIN'] * 60,
                )
                return resp

        # 如果所有摊主密码验证都失败
        return jsonify(error="Invalid vendor password"), 401

    return jsonify(error="Invalid role specified"), 400