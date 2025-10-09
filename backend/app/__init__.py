from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler

# 在全局作用域创建扩展实例
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    # 创建 Flask app 实例
    app = Flask(__name__, static_folder=config_class.STATIC_FOLDER)
    app.config.from_object(config_class)

    # --- 日志配置 ---
    # 只有在非调试模式下才启用文件日志记录
    if not app.debug:
        # 1. 确保日志文件夹存在
        log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # 2. 创建文件处理器
        log_file = os.path.join(log_directory, 'app.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024 * 5,
            backupCount=5,
            encoding='utf-8'
        )

        # 3. 创建日志格式
        log_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(log_formatter)

        # 4. ⬇️⬇️⬇️ 关键修正：将处理器添加到 app.logger ⬇️⬇️⬇️
        app.logger.addHandler(file_handler)
        
        # 5. ⬇️⬇️⬇️ 关键修正：设置 app.logger 的级别 ⬇️⬇️⬇️
        #    否则，只有 WARNING 及以上级别的日志才会被记录
        app.logger.setLevel(logging.INFO)
        app.logger.info('abl-booth-tool startup')

    # --- 文件夹创建 ---
    # 创建上传目录
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # 创建子目录
    for subdir in ['products', 'qrcodes', 'events', 'temp']:
        subdir_path = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

    # --- 静态文件路由 (主要用于本地开发) ---
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # --- 扩展初始化 ---
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # --- 数据库初始化（确保首次运行能创建 SQLite 文件和数据表） ---
    try:
        with app.app_context():
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')

            # 如果使用 SQLite，确保数据库文件目录存在
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '', 1)
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)

            # 优先使用 Alembic/Flask-Migrate 执行迁移（如果 migrations 目录存在），否则使用 create_all()
            try:
                migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'migrations')
                # 路径可能是相对的，归一化一下
                migrations_dir = os.path.abspath(migrations_dir)
                if os.path.isdir(migrations_dir):
                    app.logger.info('migrations found at %s, attempting to upgrade database...', migrations_dir)
                    from flask_migrate import upgrade as _upgrade
                    _upgrade()
                else:
                    app.logger.info('no migrations directory found, creating tables with db.create_all()')
                    db.create_all()
            except Exception as e:
                # 如果迁移失败，退回到 create_all 保证表至少被创建
                app.logger.exception('database migration/upgrade failed, falling back to create_all: %s', e)
                try:
                    db.create_all()
                except Exception:
                    app.logger.exception('db.create_all() also failed')
    except Exception:
        # 捕获任意初始化阶段的异常，避免阻塞应用启动
        app.logger.exception('unexpected error during database initialization')

    # --- 蓝图注册 ---
    from .sale_system import sale_bp
    app.register_blueprint(sale_bp, url_prefix='/sale')
    
    return app

# 模型导入放在文件末尾，防止循环依赖
from . import models