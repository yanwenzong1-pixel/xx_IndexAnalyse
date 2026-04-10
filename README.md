# 微盘股指数分析系统

> 基于多因子模型的微盘股风险评估与下跌概率预测系统
> 版本：2.0（重构版）

## 🚀 快速启动

### 静态前端（无本地后端）

若环境不允许常驻后端，构建 `src/frontend`（`npm run build`）或将 `dist/` 部署到静态站点；预测数据由预生成 JSON（`public/data`）提供。遗留目录 `web/frontend/` 仅作参考。

```bash
pip install -r requirements.txt
python tools/export_static_predict_history.py
```

说明见 [docs/static-frontend-deploy.md](docs/static-frontend-deploy.md)。

### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

访问健康检查：http://127.0.0.1:5000/api/health

### 前端启动

```bash
# 进入前端目录（待迁移完成后）
cd src/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 📁 项目结构

```
xx_IndexAnalyse/
├── src/                      # 核心业务代码
│   ├── backend/              # 后端代码
│   │   ├── api/              # 接口层
│   │   ├── service/          # 业务逻辑层
│   │   ├── model/            # 数据模型层
│   │   ├── dao/              # 数据访问层
│   │   └── core/             # 核心配置层
│   └── frontend/             # React + Vite 单入口
│       ├── src/              # 页面/组件/hooks/API 客户端
│       ├── public/data/      # 静态预测 JSON / static-data.js（export 脚本生成）
│       ├── package.json
│       └── vite.config.js
├── tests/                    # 测试用例
│   ├── backend/              # 后端测试
│   └── frontend/             # 前端测试
├── config/                   # 配置文件
├── data/                     # 数据文件
├── docs/                     # 文档
├── logs/                     # 日志文件
├── .env                      # 环境变量
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略配置
├── requirements.txt          # Python 依赖
├── pytest.ini                # Pytest 配置
├── main.py                   # 主启动入口
└── README.md                 # 项目说明
```

---

## 🛠️ 技术栈

### 后端
- **框架**: Flask 2.0+
- **数据处理**: Pandas, NumPy
- **HTTP 请求**: Requests
- **测试**: Pytest

### 前端
- **框架**: React 18
- **构建工具**: Vite 5.0
- **样式**: Tailwind CSS 3.3
- **图表**: ECharts 5.4.3
- **HTTP 客户端**: Axios 1.6

---

## 📋 核心功能

### 下跌概率预测
- T+1 下跌概率预测
- T+5 下跌概率预测
- 预期跌幅计算

### 风险评估
- 风险打分（1-10 分）
- 风险等级划分
- 多维度风险分析

### 指标计算
- 流动性维度
- 资金结构维度
- 估值与业绩维度
- 政策与制度维度
- 宏观环境维度

---

## 🔧 配置说明

### 环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
BACKEND_HOST=127.0.0.1
BACKEND_PORT=5000
LOG_LEVEL=INFO
```

### 后端配置

配置文件：`src/backend/core/config.py`

- `BACKEND_PORT`: 后端端口（默认 5000）
- `DEBUG`: 调试模式
- `CACHE_TTL_*`: 缓存过期时间

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/backend/dao/test_cache_dao.py -v

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

---

## 📖 API 文档

### 数据接口
- `GET /api/data` - 获取股票数据
- `POST /api/refresh` - 刷新数据

### 指标接口
- `GET /api/indicators` - 获取指标数据

### 风险接口
- `GET /api/risk` - 获取风险评估

### 报告接口
- `GET /api/report` - 获取每日报告

### 健康检查
- `GET /api/health` - 服务健康检查

---

## 📝 开发规范

### 代码规范
- 遵循 PEP 8（Python）
- 遵循 ESLint（JavaScript）
- 单一职责原则
- 分离关注点

### 提交规范
- 功能新增：`feat: 功能描述`
- Bug 修复：`fix: 修复描述`
- 文档更新：`docs: 文档描述`
- 重构：`refactor: 重构描述`

---

## 📄 许可证

本项目仅供学习研究使用

---

**最后更新**: 2026-03-19  
**版本**: 2.0（重构版）
