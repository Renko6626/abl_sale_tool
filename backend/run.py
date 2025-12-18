from app import create_app

from dotenv import load_dotenv
import os

# 这行代码会查找当前目录下的 .env 文件并加载其中的变量
# 它必须在你的应用代码（如 Flask app）使用这些环境变量之前被调用
load_dotenv() 
app = create_app()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)