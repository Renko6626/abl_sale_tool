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

# --- 用户配置区 (您只需要修改这里) ---
PROJECT_NAME="abl-booth-tool"
DOMAIN_NAME="booth-tool.secret-sealing.club"
WWW_DOMAIN_NAME="www.booth-tool.secret-sealing.club"
# 请务必替换成您自己的有效邮箱
EMAIL="your_email@xx.xx"

# --- 自动检测路径 (请勿修改) ---
# 获取脚本所在的绝对路径，作为项目根目录
PROJECT_BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# 根据项目根目录自动生成其他路径
FRONTEND_DIR="${PROJECT_BASE_DIR}/frontend/dist"
BACKEND_DIR="${PROJECT_BASE_DIR}/backend"
VENV_PATH="${BACKEND_DIR}/venv"
# 【核心修正 1】将 Socket 相关目录定义在项目内部，避免 /run 目录的权限问题
RUN_DIR="${BACKEND_DIR}/run"
SOCKET_PATH="${RUN_DIR}/${PROJECT_NAME}.sock"
NGINX_CONF_PATH="/etc/nginx/sites-available/${PROJECT_NAME}"
NGINX_ENABLED_PATH="/etc/nginx/sites-enabled/${PROJECT_NAME}"


# --- 脚本执行区 ---
echo "--- 开始部署项目: ${PROJECT_NAME} ---"
echo "--- 项目根目录: ${PROJECT_BASE_DIR} ---"

# 1. 安装系统基础依赖
echo "--> 正在安装系统基础依赖 (Nginx, Python, Git, Curl)..."
sudo apt-get update
sudo apt-get install -y nginx python3-pip python3-venv git curl

# 2. 设置 Node.js 和 PM2 环境 (使用 NVM 和 Gitee 镜像)
echo "--> 正在配置 Node.js 和 PM2 环境..."

# 加载 NVM (如果已安装)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 检查 nvm 命令是否存在，如果不存在则安装
if ! command -v nvm &> /dev/null
then
    echo "--> 未找到 NVM，正在从 Gitee 镜像安装..."
    # 使用 Gitee 镜像源来安装 NVM，解决 raw.githubusercontent.com 无法访问的问题
    curl -o- https://gitee.com/mirrors/nvm/raw/master/install.sh | bash
    # 立即加载 NVM 使其在当前会话生效
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# 检查 Node.js 是否已安装，如果没有则安装 LTS 版本
if ! command -v node &> /dev/null
then
    echo "--> 未找到 Node.js，正在使用 NVM 安装 LTS 版本..."
    nvm install --lts
    nvm use --lts
fi

# 检查 pm2 是否已安装，如果没有则安装 (无需 sudo)
if ! command -v pm2 &> /dev/null
then
    echo "--> 正在全局安装 PM2..."
    npm install -g pm2
fi
echo "--> Node.js 和 PM2 环境已准备就绪。"

# 3. 前端构建 (可选)
echo "--> 正在构建前端项目..."
cd "${PROJECT_BASE_DIR}/frontend"
npm install
npm run build
echo "--> 前端构建完成，产物位于 ${FRONTEND_DIR} 。"

# 4. 后端环境设置
echo "--> 正在设置 Python 后端环境..."
cd "${BACKEND_DIR}"

# 创建 Python 虚拟环境
if [ ! -d "${VENV_PATH}" ]; then
    python3 -m venv venv
    echo "Python 虚拟环境已创建。"
fi

# 在虚拟环境中安装依赖
source "${VENV_PATH}/bin/activate"
pip install -r requirements.txt
pip install gunicorn # 确保 gunicorn 在虚拟环境中
deactivate

# 【核心修正 2】为 PM2 创建日志目录和新的 run 目录
mkdir -p "${BACKEND_DIR}/logs"
mkdir -p "${RUN_DIR}"

# 确保项目内所有文件和目录都属于当前运行脚本的用户。
echo "--> 正在修正项目文件所有权，确保当前用户 (${USER}) 拥有权限..."
sudo chown -R "${USER}:${USER}" "${PROJECT_BASE_DIR}"
sudo chown -R "${USER}:${USER}" "${RUN_DIR}"
sudo chown -R "${USER}:${USER}" "${BACKEND_DIR}/logs"
# 5. 使用 PM2 启动/重启后端应用
echo "--> 正在使用 PM2 部署后端应用..."
cd "${BACKEND_DIR}"

# NVM 环境下的 PM2 路径可能不在标准 PATH 中, 先找到它
PM2_PATH=$(command -v pm2)

# 使用 startOrRestart 来更新应用，如果已存在则重启，不存在则启动
# 确保你的 ecosystem.config.js 已经修正，不再包含 --env-file 参数，并且 bind 的路径是动态生成的
PM2_APP_NAME=${PROJECT_NAME} $PM2_PATH startOrRestart ecosystem.config.js --env production

# 设置 PM2 开机自启
# 使用 `sudo env PATH=$PATH...` 的技巧让 root 用户能找到当前用户的 pm2
sudo env PATH=$PATH:$NVM_DIR/versions/node/$(nvm version)/bin $PM2_PATH startup systemd -u $(whoami) --hp ~
$PM2_PATH save

echo "--> 后端应用已由 PM2 管理。"

# 6. 配置并重载 Nginx
echo "--> 正在生成并配置 Nginx..."

# 【核心修正 3】动态生成的 Nginx 配置文件现在指向项目内部正确的 Socket 路径
sudo tee "${NGINX_CONF_PATH}" > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME} ${WWW_DOMAIN_NAME};

    # 根路径指向前端构建产物
    location / {
        root ${FRONTEND_DIR};
        try_files \$uri \$uri/ /index.html;
    }

    # API 接口代理到 Gunicorn
    location /sale {
        proxy_pass http://unix:${SOCKET_PATH}; # <-- 使用了修正后的 SOCKET_PATH
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 后端静态文件服务 (如果需要)
    location /static {
        alias ${BACKEND_DIR}/static;
        expires 7d;
    }
}
EOF

# 创建符号链接以启用站点
if [ ! -L "${NGINX_ENABLED_PATH}" ]; then
    sudo ln -s "${NGINX_CONF_PATH}" "${NGINX_ENABLED_PATH}"
fi

# 测试 Nginx 配置并平滑重载
sudo nginx -t
if [ $? -eq 0 ]; then
    sudo systemctl reload nginx
    echo "--> Nginx 配置已成功加载。"
else
    echo "!! Nginx 配置错误，请检查！部署中断。"
    exit 1
fi

# 7. 配置 SSL 证书 (使用 Certbot)
echo "--> 正在检查并配置 SSL 证书..."
# 检查是否安装了 certbot 和 nginx 插件
if ! command -v certbot &> /dev/null
then
    echo "--> 正在安装 Certbot..."
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# 申请或续订证书。--nginx 插件会自动修改 Nginx 配置并重载
sudo certbot --nginx -d ${DOMAIN_NAME} -d ${WWW_DOMAIN_NAME} --non-interactive --agree-tos -m ${EMAIL} --redirect

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