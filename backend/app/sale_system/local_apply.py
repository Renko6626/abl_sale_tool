import socket
from flask import request, jsonify
from . import sale_bp


def get_local_ip():
    """获取本机在局域网中的 IP 地址。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 诱导系统选择当前可用网卡，不会真正发包
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


@sale_bp.route('/api/server-info', methods=['GET'])
def get_server_info():
    """返回局域网访问信息，便于手机/平板扫码连接。"""
    ip = get_local_ip()

    # 从请求推断协议与端口，使二维码与当前访问一致
    scheme = request.scheme or 'http'
    host = request.host or ''
    port = None
    if ':' in host:
        try:
            port = int(host.rsplit(':', 1)[1])
        except ValueError:
            port = None
    if not port:
        port = 5000

    base_url = f"{scheme}://{ip}:{port}"

    return jsonify({
        "ip": ip,
        "port": port,
        "base_url": base_url,
        # 前端入口/摊主入口路径可按需调整
        "order_url": f"{base_url}/",
        "vendor_url": f"{base_url}/login/vendor",
        "admin_url": f"{base_url}/login/admin",
    })