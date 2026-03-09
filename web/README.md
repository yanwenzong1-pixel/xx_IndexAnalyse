# 微盘股指数分析系统 - Web版本

## 项目结构

```
web/
├── backend/             # 后端代码
│   ├── app.py          # Flask应用入口
│   ├── analyzer.py     # 微盘股分析核心逻辑
│   ├── services/       # 服务层
│   ├── utils/          # 工具类
│   └── start.sh        # 启动脚本
└── frontend/           # 前端代码
    ├── public/         # 静态文件
    ├── src/            # 源代码
    │   ├── components/ # 组件
    │   ├── services/   # API服务
    │   ├── hooks/      # 自定义Hooks
    │   ├── App.jsx     # 应用主组件
    │   └── main.jsx    # 入口文件
    ├── package.json    # 项目配置
    └── vite.config.js  # Vite配置
```

## 技术栈

### 后端
- **语言**: Python 3
- **框架**: Flask
- **数据处理**: pandas, numpy
- **网络请求**: requests
- **邮件发送**: smtplib
- **定时任务**: APScheduler

### 前端
- **框架**: React
- **样式**: Tailwind CSS
- **数据可视化**: ECharts
- **HTTP客户端**: Axios
- **构建工具**: Vite

## 运行步骤

### 1. 启动后端

```bash
# 进入后端目录
cd web/backend

# 安装依赖
pip install flask flask-cors pandas numpy requests apscheduler

# 启动应用
python app.py
```

后端服务将在 `http://localhost:8080` 运行。

### 2. 启动前端

```bash
# 进入前端目录
cd web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:3000` 运行。

## API接口

### 1. 获取微盘股指数数据
- **URL**: `/api/data`
- **Method**: GET
- **Response**: 包含最新数据和历史数据

### 2. 获取指标数据
- **URL**: `/api/indicators`
- **Method**: GET
- **Response**: 包含五大维度的指标数据

### 3. 获取风险评估
- **URL**: `/api/risk`
- **Method**: GET
- **Response**: 包含风险等级、下跌概率和预警信息

### 4. 获取每日报告
- **URL**: `/api/report`
- **Method**: GET
- **Response**: 包含每日监控报告

### 5. 手动刷新数据
- **URL**: `/api/refresh`
- **Method**: POST
- **Response**: 刷新状态

## 功能特点

1. **实时数据更新**：每3小时自动刷新数据
2. **风险评估**：1-10级风险等级评估
3. **预警系统**：下跌风险警报和买点信号
4. **数据可视化**：价格走势图、换手率和成交额图
5. **响应式设计**：适配不同屏幕尺寸
6. **每日报告**：自动生成并发送邮件报告

## 注意事项

1. **邮件配置**：需要在 `backend/utils/email_utils.py` 中配置正确的邮箱信息
2. **数据来源**：使用东方财富API获取数据，可能存在数据延迟
3. **网络连接**：确保网络连接正常，以便获取数据和发送邮件
4. **依赖安装**：确保安装了所有必要的依赖包

## 开发说明

- 后端使用Flask框架，提供RESTful API
- 前端使用React + Tailwind CSS，构建响应式界面
- 使用ECharts实现数据可视化
- 使用APScheduler实现定时任务
- 使用Flask-CORS处理跨域请求

## 部署说明

### 生产环境部署

1. **后端**：使用Gunicorn + Nginx部署
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **前端**：构建生产版本
   ```bash
   npm run build
   ```
   然后将 `dist` 目录部署到静态文件服务器

3. **Nginx配置**：配置反向代理，将API请求转发到后端服务

## 故障排除

1. **后端启动失败**：检查依赖是否安装，端口是否被占用
2. **数据获取失败**：检查网络连接，东方财富API是否可访问
3. **邮件发送失败**：检查邮箱配置，SMTP服务是否开启
4. **前端无法连接后端**：检查CORS配置，API地址是否正确

## 联系方式

如有问题，请联系技术支持。
