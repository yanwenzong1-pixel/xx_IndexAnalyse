# 微盘股指数分析系统 - Web架构设计

## 技术栈选择

### 后端
- **语言**: Python 3
- **框架**: Flask（轻量级，适合API开发）
- **数据处理**: pandas, numpy
- **网络请求**: requests
- **邮件发送**: smtplib
- **定时任务**: APScheduler

### 前端
- **框架**: React
- **样式**: Tailwind CSS（响应式设计）
- **数据可视化**: ECharts
- **状态管理**: React Context API
- **HTTP客户端**: Axios

### 部署
- **开发环境**: Flask内置服务器
- **生产环境**: Gunicorn + Nginx（可选）

## 架构设计

### 目录结构
```
web/
├── backend/
│   ├── app.py             # Flask应用入口
│   ├── analyzer.py        # 微盘股分析核心逻辑
│   ├── routes.py          # API路由
│   ├── services/
│   │   ├── data_service.py    # 数据获取服务
│   │   ├── indicator_service.py  # 指标计算服务
│   │   ├── risk_service.py     # 风险评估服务
│   │   └── report_service.py   # 报告生成服务
│   └── utils/
│       ├── email_utils.py      # 邮件发送工具
│       └── scheduler_utils.py  # 定时任务工具
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── App.jsx           # 应用主组件
    │   ├── components/
    │   │   ├── RiskLevel.jsx     # 风险等级组件
    │   │   ├── IndicatorCards.jsx  # 指标卡片组件
    │   │   ├── PriceChart.jsx      # 价格走势图组件
    │   │   ├── TurnoverChart.jsx   # 换手率和成交额图组件
    │   │   └── AlertMessage.jsx    # 预警信息组件
    │   ├── services/
    │   │   └── api.js        # API调用服务
    │   ├── hooks/
    │   │   └── useData.js    # 数据获取Hook
    │   └── styles/
    │       └── tailwind.css   # Tailwind CSS配置
    ├── package.json
    └── vite.config.js        # Vite配置
```

## API设计

### 1. 获取微盘股指数数据
- **URL**: `/api/data`
- **Method**: GET
- **Response**: 
  ```json
  {
    "success": true,
    "data": {
      "latest": {
        "date": "2024-03-05",
        "close": 1500.0,
        "change_pct": 2.5,
        "amount": 1000000000,
        "turnover": 5.2
      },
      "history": [
        {
          "date": "2024-03-04",
          "close": 1463.5,
          "change_pct": -1.2,
          "amount": 950000000,
          "turnover": 4.8
        },
        // 更多历史数据...
      ]
    }
  }
  ```

### 2. 获取指标数据
- **URL**: `/api/indicators`
- **Method**: GET
- **Response**: 
  ```json
  {
    "success": true,
    "data": {
      "liquidity": {
        "amount_to_market_cap": 0.02,
        "avg_turnover_5d": 5.2,
        "bid_ask_spread": 0.03,
        "liquidity_coverage": 850000000
      },
      "fund_structure": {
        "amount_change_pct": 0.05,
        "financing_balance_change": 0.03
      },
      "valuation": {
        "volatility": 25.5,
        "ma5": 1480.0,
        "ma20": 1450.0,
        "ma5_ma20_diff": 30.0
      },
      "policy": {
        "ipo_activity": 0.5,
        "regulation_intensity": 0.3,
        "financial_report_window": false
      },
      "macro": {
        "excess_liquidity": 0.2,
        "pmi": 50.5,
        "risk_appetite": 0.6,
        "interest_rate_env": 0.4
      }
    }
  }
  ```

### 3. 获取风险评估
- **URL**: `/api/risk`
- **Method**: GET
- **Response**: 
  ```json
  {
    "success": true,
    "data": {
      "risk_level": 6,
      "downside_probability": 0.45,
      "alert": false,
      "alert_message": ""
    }
  }
  ```

### 4. 获取每日报告
- **URL**: `/api/report`
- **Method**: GET
- **Response**: 
  ```json
  {
    "success": true,
    "data": {
      "report": "微盘股指数每日监控报告..."
    }
  }
  ```

### 5. 手动刷新数据
- **URL**: `/api/refresh`
- **Method**: POST
- **Response**: 
  ```json
  {
    "success": true,
    "message": "数据刷新成功"
  }
  ```

## 前端设计

### 页面布局
1. **顶部导航栏**
   - 系统标题
   - 风险等级显示
   - 刷新按钮

2. **指标卡片区域**
   - 收盘价
   - 涨跌幅
   - 成交额
   - 换手率
   - 5日平均换手率
   - 20日波动率

3. **图表区域**
   - 价格走势图（含MA5、MA20）
   - 换手率和成交额图

4. **预警信息区域**
   - 风险警报
   - 买点信号

5. **报告区域**
   - 每日报告展示
   - 邮件发送状态

### 交互设计
- 实时数据更新（每3小时自动刷新）
- 手动刷新按钮
- 图表交互（缩放、时间范围选择）
- 预警信息弹窗
- 响应式布局（适配不同屏幕尺寸）

## 数据流

1. **后端**
   - 定时从东方财富API获取数据
   - 计算各项指标
   - 评估风险等级
   - 生成每日报告
   - 发送邮件

2. **前端**
   - 初始化时从API获取数据
   - 定期轮询更新数据
   - 展示数据和图表
   - 显示预警信息

## 性能优化

1. **后端**
   - 缓存数据，减少API调用
   - 异步处理定时任务
   - 优化数据计算

2. **前端**
   - 组件懒加载
   - 数据缓存
   - 图表性能优化
   - 响应式设计

## 安全考虑

1. **API安全**
   - 输入验证
   - 错误处理
   - CORS配置

2. **邮件安全**
   - 邮箱配置加密
   - 防止邮件发送滥用

3. **数据安全**
   - 数据验证
   - 错误处理
   - 日志记录
