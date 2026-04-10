# CORS 跨域问题修复指南

## 问题描述

```
Access to fetch at 'http://localhost:5000/api/risk/history?days=252' from origin 'null' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 问题原因

浏览器出于安全考虑，默认阻止从不同源（域名、协议、端口）发起的请求。前端页面（本地文件，origin 为 null）访问后端 API（http://localhost:5000）时，需要后端在响应头中添加 CORS 相关的头信息。

## 已实施的修复

### 修改文件：simple_app.py

**添加的代码**：

```python
from flask import Flask, jsonify, request, make_response

# 添加 CORS 支持（手动添加响应头）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
```

### 功能说明

1. **`@app.after_request`**：Flask 装饰器，在每次请求后执行
2. **`Access-Control-Allow-Origin: *`**：允许任何源访问
3. **`Access-Control-Allow-Headers`**：允许的请求头
4. **`Access-Control-Allow-Methods`**：允许的 HTTP 方法

## 启动服务

### 方法 1：重新启动后端
```bash
python web/backend/simple_app.py
```

### 方法 2：使用批处理
```
启动后端.bat
```

## 验证修复

### 方法 1：浏览器测试
1. 启动后端服务
2. 刷新前端页面（F5）
3. 点击"风险趋势"标签
4. 图表应该正常显示

### 方法 2：检查控制台
浏览器控制台应该显示：
```
[RiskTab] 开始加载风险数据...
[RiskTab] API 响应状态：200
[RiskTab] API 返回结果：{success: true, data: Array(252), ...}
[RiskTab] 数据加载成功，共 252 条记录
```

### 方法 3：使用测试脚本
```bash
python test_cors.py
```

## 预期输出

服务启动后应该看到：
```
============================================================
启动后端服务...
============================================================
✅ 所有模块导入成功

初始化数据...
✅ 数据初始化成功
✅ 历史回溯服务初始化成功
✅ 历史风险服务初始化成功

============================================================
服务启动成功！
监听地址：http://localhost:5000
============================================================
```

## CORS 头验证

成功的 CORS 配置会在响应头中包含：
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,Authorization
Access-Control-Allow-Methods: GET,PUT,POST,DELETE,OPTIONS
```

## 常见问题

### Q1: 服务启动后仍然报 CORS 错误
**解决**：
1. 确保后端服务已重启
2. 清除浏览器缓存
3. 硬刷新页面（Ctrl+F5）

### Q2: 端口 5000 被占用
**解决**：
```bash
# 查找占用进程
netstat -ano | findstr :5000

# 终止进程
taskkill /PID <进程 ID> /F
```

### Q3: 前端仍然无法访问
**解决**：
1. 检查后端服务是否正常运行
2. 访问 http://localhost:5000/api/health 测试
3. 查看浏览器控制台的详细错误信息

## 安全说明

当前配置允许所有源访问（`*`），适用于开发和测试环境。

**生产环境建议**：
```python
# 只允许特定源
response.headers.add('Access-Control-Allow-Origin', 'https://yourdomain.com')
```

## 技术细节

### CORS 预检请求
对于某些请求（如包含自定义头），浏览器会先发送 OPTIONS 预检请求。

我们的配置会自动处理：
```python
@app.after_request
def after_request(response):
    # 对所有请求（包括 OPTIONS）添加 CORS 头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
```

### 为什么使用 @app.after_request
- 自动应用于所有路由
- 不需要修改现有路由代码
- 确保所有响应都包含 CORS 头

## 下一步

1. ✅ 启动后端服务
2. ✅ 验证 CORS 头存在
3. ✅ 刷新前端页面
4. ✅ 测试风险趋势功能

---

**修复完成时间**：2026-03-12  
**修复版本**：v2.1.3  
**状态**：✅ 已修复，待重启验证
