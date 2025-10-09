#!/bin/bash

# ==============================================================================
#                 一键部署脚本 for abl-booth-tool 
#
# 该脚本会自动完成以下任务:
# 1. 安装系统依赖 (Nginx, Python, Git, Curl)
# 2. 使用 Gitee 镜像安装并配置 NVM, Node.js, PM2
# 3. 创建 Python 虚拟环境并安装后端依赖
# 4. 使用 PM2 启动和守护后端服务 (使用项目内 Socket 文件避免权限问题)
# 5. 动态生成 Nginx 配置文件并启用 (指向项目内 Socket 文件)
# 6. 使用 Certbot 自动申请和配置 SSL 证书
#
# ==============================================================================

set -e
set -o pipefail

# --- 用户配置区 (您只需要修改这里) ---
PROJECT_NAME="abl-booth-tool"
DOMAIN_NAME="booth-tool.secret-sealing.club"
WWW_DOMAIN_NAME="www.booth-tool.secret-sealing.club"
EMAIL="2300011496@stu.pku.edu.cn"                # 用于申请 SSL 证书的邮箱
MAX_BODY_SIZE="16M"                          # Nginx 允许的最大上传体积，请和后端.env 中的设置保持一致
PYTHON_VERSION="3.12"                        

# --- 自动检测路径 (请勿修改) ---
PROJECT_BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
FRONTEND_DIR="${PROJECT_BASE_DIR}/frontend/dist"
BACKEND_DIR="${PROJECT_BASE_DIR}/backend"
VENV_PATH="${BACKEND_DIR}/venv"
RUN_DIR="${BACKEND_DIR}/run"
SOCKET_PATH="${RUN_DIR}/${PROJECT_NAME}.sock"
NGINX_CONF_PATH="/etc/nginx/sites-available/${PROJECT_NAME}"
NGINX_ENABLED_PATH="/etc/nginx/sites-enabled/${PROJECT_NAME}"


# ------------------------------------------------------------------------------
# 函数：安装系统依赖
# ------------------------------------------------------------------------------
install_system_deps() {
    echo "--> 正在安装系统基础依赖..."
    sudo apt-get update
    # 使用变量来安装指定的 Python 版本
    sudo apt-get install -y nginx "python${PYTHON_VERSION}" "python${PYTHON_VERSION}-venv" python3-pip git curl
}

# ------------------------------------------------------------------------------
# 函数：配置 Node.js 和 PM2
# ------------------------------------------------------------------------------
setup_nodejs() {
    echo "--> 正在配置 Node.js 和 PM2 环境..."
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    if ! command -v nvm &> /dev/null; then
        echo "--> 未找到 NVM，正在从 Gitee 镜像安装..."
        curl -o- https://gitee.com/mirrors/nvm/raw/master/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi
    if ! command -v node &> /dev/null; then
        echo "--> 未找到 Node.js，正在使用 NVM 安装 LTS 版本..."
        nvm install --lts
        nvm use --lts
    fi
    if ! command -v pm2 &> /dev/null; then
        echo "--> 正在全局安装 PM2..."
        npm install -g pm2
    fi
    echo "--> Node.js 和 PM2 环境已准备就绪。"
}

# ------------------------------------------------------------------------------
# 函数：构建前端
# ------------------------------------------------------------------------------
build_frontend() {
    echo "--> 正在构建前端项目..."
    cd "${PROJECT_BASE_DIR}/frontend"
    npm install
    npm run build
    # 增加一个检查，确保构建产物目录存在
    if [ ! -d "${FRONTEND_DIR}" ]; then
        echo "!! 错误: 前端构建失败，未找到 dist 目录！"
        exit 1
    fi
    echo "--> 前端构建完成。"
}

# ------------------------------------------------------------------------------
# 函数：设置后端环境
# ------------------------------------------------------------------------------
setup_backend() {
    echo "--> 正在设置 Python 后端环境..."
    cd "${BACKEND_DIR}"
    
    # <<< 改进 4: 检查 .env 文件
    if [ ! -f ".env" ]; then
        echo "!! 警告: 后端目录中未找到 .env 配置文件！"
        echo "!! 请务必根据 .env.example 创建并修改 .env 文件，否则应用可能无法启动。"
        # 你甚至可以做得更绝一点，如果不存在就直接退出: exit 1
    fi
    
    if [ ! -d "${VENV_PATH}" ]; then
        # 使用变量来创建虚拟环境
        "python${PYTHON_VERSION}" -m venv venv
        echo "--> Python 虚拟环境已创建。"
    fi
    
    source "${VENV_PATH}/bin/activate"
    pip install --upgrade pip
    
    if [ ! -f "requirements.txt" ]; then
        echo "!! 错误: 后端目录中未找到 requirements.txt 文件！"
        exit 1
    fi

    pip install -r requirements.txt
    # <<< 改进 3: 建议将 gunicorn 添加到 requirements.txt, 不再需要此行
    # pip install gunicorn 
    deactivate
    
    mkdir -p "${BACKEND_DIR}/logs"
    mkdir -p "${RUN_DIR}"
    
    echo "--> 正在修正项目文件所有权..."
    sudo chown -R "${USER}:${USER}" "${PROJECT_BASE_DIR}"
}

# ------------------------------------------------------------------------------
# 函数：使用 PM2 部署后端
# ------------------------------------------------------------------------------
deploy_backend_with_pm2() {
    echo "--> 正在使用 PM2 部署后端应用..."
    cd "${BACKEND_DIR}"
    
    local PM2_PATH=$(command -v pm2)
    
    echo "--> 正在清理旧的 PM2 进程..."
    $PM2_PATH delete ecosystem.config.js || true
    
    echo "--> 正在启动新的 PM2 进程..."
    PM2_APP_NAME=${PROJECT_NAME} $PM2_PATH start ecosystem.config.js --env production
    
    sudo env PATH=$PATH:$NVM_DIR/versions/node/$(nvm version)/bin $PM2_PATH startup systemd -u $(whoami) --hp ~
    $PM2_PATH save
    
    echo "--> 后端应用已由 PM2 管理。"
}

# ------------------------------------------------------------------------------
# 函数：配置 Nginx
# ------------------------------------------------------------------------------
configure_nginx() {
    echo "--> 正在生成并配置 Nginx..."
    sudo tee "${NGINX_CONF_PATH}" > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME} ${WWW_DOMAIN_NAME};
    client_max_body_size ${MAX_BODY_SIZE};

    location / {
        root ${FRONTEND_DIR};
        try_files \$uri \$uri/ /index.html;
    }

    location /sale {
        proxy_pass http://unix:${SOCKET_PATH};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias ${BACKEND_DIR}/static;
        expires 7d;
    }
}
EOF
    
    # 使用 -f 选项强制创建链接，可以覆盖旧的错误链接
    sudo ln -sf "${NGINX_CONF_PATH}" "${NGINX_ENABLED_PATH}"
    
    sudo nginx -t
    sudo systemctl reload nginx
    echo "--> Nginx 配置已成功加载。"
}

# ------------------------------------------------------------------------------
# 函数：配置 SSL
# ------------------------------------------------------------------------------
configure_ssl() {
    echo "--> 正在检查并配置 SSL 证书..."
    if ! command -v certbot &> /dev/null; then
        echo "--> 正在安装 Certbot..."
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    sudo certbot --nginx -d ${DOMAIN_NAME} -d ${WWW_DOMAIN_NAME} --non-interactive --agree-tos -m ${EMAIL} --redirect
}


# --- 主执行逻辑 ---
# <<< 改进 2: 检查是否为 root 用户
if [ "$(id -u)" -eq 0 ]; then
   echo "!! 警告：请不要使用 root 用户直接运行此脚本。"
   echo "!! 请使用具有 sudo 权限的普通用户执行。"
   echo "如果你确实需要以 root 身份运行，请输入Y。代表你已经了解风险。"
    read -r response
   if [ "$response" != "Y" ]; then
       exit 1
   fi
fi

main() {
    echo "--- 开始部署项目: ${PROJECT_NAME} ---"
    echo "--- 项目根目录: ${PROJECT_BASE_DIR} ---"
    
    install_system_deps
    setup_nodejs
    build_frontend
    setup_backend
    deploy_backend_with_pm2
    configure_nginx
    configure_ssl
    
    echo ""
    echo "========================================================"
    echo "          ✅  部署完成！"
    echo "========================================================"
    echo "您的网站现在应该可以通过以下地址访问："
    echo "https://${DOMAIN_NAME}"
    echo ""
    echo "您可以使用 'pm2 status' 命令查看后端服务状态。"
    echo "======================================================="
    echo "注意,请你在部署后尽快修改backend/.env文件中的管理员密码和摊主密码！"
    echo "默认管理员密码: 1919810"
    echo "默认摊主密码: 114514"
    echo "========================================================"
}

# --- 运行主函数 ---
main