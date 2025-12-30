# Builder - AI 驱动的 ORM 实体生成器

基于智谱 AI 的 ORM 实体代码生成服务，通过 AI 模型自动生成高质量的 ORM 代码。

## 📋 项目简介

Builder 是一个基于 AI 的 ORM 实体代码生成服务，通过智谱 AI 模型自动生成高质量的 ORM 代码。

**技术栈：**
- Python 3.11+
- FastAPI 0.128+
- 智谱 AI (GLM-4.7)
- Uvicorn ASGI 服务器
- uv 包管理器

---

## 🔧 环境要求

### 必需环境
- **Python**: >= 3.11
- **包管理器**: uv (推荐)
- **操作系统**: Windows / Linux / macOS

---

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone git@github.com:Protagonistss/auto-backend.git
cd auto-backend
```

### 2. 安装 uv（如果尚未安装）

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 同步依赖

```bash
uv sync
```

---

## ⚙️ 配置说明

### 1. 创建环境配置文件

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 ZHIPU_API_KEY
# Windows: notepad .env
# Linux/Mac: vim .env
```

### 2. 环境变量配置

```env
# ===================
# AI 配置（必填）
# ===================
ZHIPU_API_KEY=your_api_key_here  # 替换为你的智谱 API Key

# ===================
# AI 配置（可选）
# ===================
AI_MODEL=glm-4.7      # AI 模型版本
AI_PROVIDER=zhipu     # AI 提供商

# ===================
# 服务配置（可选）
# ===================
PORT=8000            # 服务端口
HOST=0.0.0.0         # 监听地址
```

### 3. 获取智谱 API Key

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入「API Keys」页面
4. 创建新的 API Key 并复制到 `.env` 文件中

---

## 🚀 启动方式

### 方式一：使用 uv（推荐）

#### Windows 系统

```bash
# 开发模式（带热重载）
uv run -m uvicorn builder.main:app --reload
```

#### Linux / macOS 系统

```bash
# 开发模式（带热重载）
uv run -m uvicorn builder.main:app --reload --host 0.0.0.0 --port 8000
```

### 方式二：生产模式

```bash
# 多进程部署（推荐用于生产环境）
uv run -m uvicorn builder.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**启动成功输出：**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     🚀 Auto-Builder Python 启动
INFO:     📦 AI Provider: zhipu
INFO:     🧠 Model: glm-4.7
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 📡 API 接口说明

### 基础接口

#### 1. 健康检查
```http
GET /health
```
**响应：**
```json
{
  "status": "healthy"
}
```

#### 2. 服务信息
```http
GET /
```
**响应：**
```json
{
  "message": "Auto-Builder API is running",
  "version": "2.0.0"
}
```

### 核心接口

#### 3. 上传配置文件
```http
POST /api/upload
Content-Type: multipart/form-data
```

**请求参数：**
- `file`: JSON 格式配置文件（必填）

**响应：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**示例（curl）：**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@config.json"
```

**示例（Python）：**
```python
import requests

with open("config.json", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/upload",
        files={"file": f}
    )
    task_id = response.json()["task_id"]
```

#### 4. 查询任务状态
```http
GET /api/tasks/{task_id}
```

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "created_at": "2025-12-30T23:14:00"
}
```

**状态枚举：**
- `pending`: 等待处理
- `processing`: 处理中
- `success`: 成功
- `failed`: 失败

#### 5. 获取生成结果
```http
GET /api/tasks/{task_id}/result
```

**成功响应：**
```json
{
  "entity_code": "// 生成的 ORM 代码...",
  "metadata": {
    "language": "java",
    "framework": "mybatis"
  }
}
```

---

## 🧪 测试接口

### 使用 Swagger UI（推荐）

启动服务后，可以通过以下地址访问交互式 API 文档：

| 文档类型 | 地址 | 说明 |
|---------|------|------|
| **Swagger UI** | http://localhost:8000/docs | 交互式 API 文档，支持在线测试 |
| **ReDoc** | http://localhost:8000/redoc | 另一种风格的 API 文档 |
| **OpenAPI Schema** | http://localhost:8000/openapi.json | OpenAPI 3.0 JSON 规范 |

在 Swagger UI 中可以：
- 查看所有 API 接口和详细说明
- 在线测试接口（无需额外工具）
- 查看请求/响应示例和数据模型
- 下载 OpenAPI 规范文件

### 使用示例配置

创建测试配置文件 `test_config.json`：
```json
{
  "database": "mysql",
  "tables": [
    {
      "name": "user",
      "columns": [
        {"name": "id", "type": "bigint", "primary": true},
        {"name": "username", "type": "varchar", "length": 50},
        {"name": "email", "type": "varchar", "length": 100}
      ]
    }
  ]
}
```

---

## 🛠️ 常用 uv 命令

### 依赖管理

```bash
# 同步依赖（安装所有依赖）
uv sync

# 添加新依赖
uv add requests

# 添加开发依赖
uv add --dev pytest

# 移除依赖
uv remove requests

# 更新所有依赖
uv lock --upgrade
```

### 运行命令

```bash
# 运行 Python 模块
uv run python -m builder.main

# 运行测试
uv run pytest

# 代码格式化
uv run ruff format .

# 类型检查
uv run mypy builder/
```

---

## 🔍 常见问题

### Q1: 启动时报错 `KeyError: zhipu_api_key`
**解决方案：** 确保已创建 `.env` 文件并正确配置 `ZHIPU_API_KEY`

### Q2: 端口被占用
**解决方案：**
```bash
# 修改 .env 中的 PORT 配置
# 或使用命令行参数指定端口
uv run uvicorn builder.main:app --port 8001
```

### Q3: 依赖安装失败
**解决方案：**
```bash
# 清除缓存重新安装
uv cache clean
uv sync
```

### Q4: uv 命令不存在
**解决方案：** 安装 uv
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 📂 项目结构

```
auto-backend/
├── builder/              # 主项目目录
│   ├── api/             # API 路由层
│   │   ├── __init__.py
│   │   └── upload.py    # 文件上传接口
│   ├── services/        # 业务逻辑层
│   │   ├── ai_service.py   # AI 服务
│   │   ├── parser.py       # 配置解析
│   │   └── task_service.py # 任务管理
│   ├── models/          # 数据模型
│   │   └── task.py
│   ├── storage/         # 数据存储
│   │   └── task_store.py
│   ├── prompts/         # AI 提示词
│   │   └── orm.md
│   ├── config.py        # 配置管理
│   └── main.py          # 应用入口
├── .env.example         # 环境变量模板
├── pyproject.toml       # 项目配置
├── uv.lock              # 依赖锁定文件
├── README.md            # 项目说明（本文件）
└── .python-version      # Python 版本
```

## 项目特点

- ⚡ 基于 FastAPI 的高性能异步 API
- 🤖 集成智谱 AI (GLM-4.7) 模型
- 📦 使用 uv 进行极速依赖管理
- 🔒 支持异步任务处理
- 📝 自动生成 Swagger/OpenAPI 3.0 文档
- 🎯 简单易用的 RESTful API 设计
- 📖 完整的 API 文档和在线测试界面

## 开发指南

### 代码格式化
```bash
uv run ruff format .
```

### 类型检查
```bash
uv run mypy builder/
```

### 运行测试
```bash
uv run pytest
```

## 📞 联系与支持

- **GitHub**: https://github.com/Protagonistss/auto-backend
- **Issue**: 提交问题请使用 GitHub Issues

## License

MIT

---

**祝你使用愉快！** 🎉
