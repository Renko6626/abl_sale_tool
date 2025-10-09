const path = require('path');

const projectName = process.env.PM2_APP_NAME || 'abl-booth-tool';
const backendDir = __dirname;
// 确保 Socket 路径在项目内部
const runDir = path.join(backendDir, 'run'); 
const socketPath = `unix:${path.join(runDir, projectName + '.sock')}`;

module.exports = {
  apps: [
    {
      name: projectName,
      script: path.join(backendDir, 'venv', 'bin', 'gunicorn'),
      
      // Gunicorn 参数 (我们之前已经修正过)
      args: `--workers 3 --bind ${socketPath} run:app`,

      // 工作目录
      cwd: backendDir,
      
      interpreter: 'none',

      instances: 1,
      autorestart: true,
      watch: false, // 生产环境建议关闭 watch
      max_memory_restart: '1G',
      
      // 日志文件路径
      out_file: path.join(backendDir, 'logs', 'out.log'),
      error_file: path.join(backendDir, 'logs', 'error.log'),

      // 环境变量
      env_production: {
        NODE_ENV: 'production',
      },
    },
  ],
}