# AI Travel Assistant

一个面向旅游场景的智能问答与行程规划系统，融合 RAG 检索、模型推理与多端展示能力，提供景点推荐、行程规划、交通与预算建议等服务。

## 亮点功能

- 智能旅游问答与攻略检索
- 行程规划与路线建议
- 目的地与景点推荐
- 住宿、美食、交通与预算指导
- 前后端分离部署，支持 Web 与小程序

## 技术栈

- 后端：FastAPI + LangChain + ChromaDB
- 前端：React + Vite + Ant Design
- 小程序端：微信小程序（WCDS）
- 模型能力：支持 DeepSeek 等模型接入

## 项目结构

```
AICD2/
├── rag_ai/                 # RAG 智能问答系统
│   ├── backend/            # 后端服务
│   ├── frontend/           # Web 前端
│   ├── vectorstores/       # 向量数据库
│   └── requirements.txt    # Python 依赖
├── WCDS/                   # 微信小程序端
├── src/                    # 其他服务代码（Java）
├── README.md
└── README.en.md
```

## 快速开始（RAG 模块）

### 1. 环境准备

- Python 3.8+
- Node.js 16+

### 2. 配置环境变量

复制示例并填写密钥：

```bash
copy rag_ai\backend\.env.example rag_ai\backend\.env
```

编辑 `rag_ai/backend/.env`：

```env
DEEPSEEK_API_KEY=your-api-key-here
```

### 3. 安装依赖

```bash
pip install -r rag_ai/requirements.txt
cd rag_ai/frontend
npm install
```

### 4. 启动服务

```bash
python rag_ai/start_backend.py
rag_ai\start_frontend.bat
```

访问地址：

- Web 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 小程序端（WCDS）

使用微信开发者工具打开 `WCDS/` 目录即可运行。云函数配置与部署说明可参考 `WCDS/` 目录内的相关文档。

## 贡献

欢迎提交 Issue 或 Pull Request。
