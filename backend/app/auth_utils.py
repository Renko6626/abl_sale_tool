import datetime as dt
from functools import wraps
from typing import Iterable, Optional

try:
    import jwt as pyjwt  # Prefer PyJWT
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyJWT is required. Please install PyJWT>=2.x") from exc
from flask import current_app, jsonify, request


def _get_secret() -> str:
    return current_app.config['JWT_SECRET']


def generate_access_token(role: str, access: str = 'all', event_id: Optional[int] = None) -> str:
    """Create a short-lived access token with role and scope claims."""
    now = dt.datetime.utcnow()
    payload = {
        'role': role,
        'access': access,  # 'all' or 'event'
        'event_id': event_id,
        'iat': now,
        'exp': now + dt.timedelta(minutes=current_app.config['JWT_ACCESS_EXPIRES_MIN']),
        'iss': 'abl-booth-tool'
    }
    if not hasattr(pyjwt, 'encode'):
        raise RuntimeError("PyJWT not available or wrong jwt package installed. Please install 'PyJWT>=2'.")
    return pyjwt.encode(payload, _get_secret(), algorithm=current_app.config['JWT_ALGORITHM'])


def _extract_token_from_header() -> Optional[str]:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        # 回退到 HttpOnly cookie
        return request.cookies.get(current_app.config.get('JWT_COOKIE_NAME', 'access_token'))
    return auth_header.replace('Bearer ', '', 1).strip()


def decode_token(token: str) -> Optional[dict]:
    try:
        return pyjwt.decode(token, _get_secret(), algorithms=[current_app.config['JWT_ALGORITHM']], issuer='abl-booth-tool')
    except pyjwt.ExpiredSignatureError:
        return None
    except pyjwt.InvalidTokenError:
        return None


def jwt_required(roles: Optional[Iterable[str]] = None, require_event_match: bool = False):
    """Decorator enforcing JWT auth and optional role/event checks."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _extract_token_from_header()
            if not token:
                return jsonify(error='Missing or invalid Authorization header'), 401

            payload = decode_token(token)
            if not payload:
                return jsonify(error='Invalid or expired token'), 401

            # Role enforcement
            if roles and payload.get('role') not in roles:
                return jsonify(error='Forbidden: insufficient role'), 403

            # Optional event binding for vendor
            if require_event_match and payload.get('role') == 'vendor' and payload.get('access') != 'all':
                requested_event_id = kwargs.get('event_id')
                if requested_event_id is None:
                    return jsonify(error='Missing event context'), 400
                try:
                    if int(requested_event_id) != int(payload.get('event_id')):
                        return jsonify(error='Forbidden: event not authorized'), 403
                except (TypeError, ValueError):
                    return jsonify(error='Invalid event id'), 400

            # 将 payload 透传给被包装函数，如有需要可使用 kwargs
            kwargs['jwt_payload'] = payload
            return fn(*args, **kwargs)

        return wrapper

    return decorator
