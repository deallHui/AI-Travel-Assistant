# 🧭 智能旅游攻略问答系统

基于 LangChain、FastAPI 和 React 的专业旅游助手，为您提供个性化的旅游攻略和建议。

## ✨ 核心功能

- 🗺️ **智能旅游问答**: 专业的旅游攻略问答，涵盖景点、美食、住宿、交通等
- 📍 **景点推荐**: 基于用户偏好推荐最佳旅游目的地和路线
- 🏨 **住宿建议**: 提供性价比最高的酒店和民宿推荐
- 🍜 **美食攻略**: 发现地道特色美食和必吃餐厅
- 🚗 **交通指南**: 规划最优出行路线和交通方案
- 💰 **预算规划**: 制定合理的旅游预算和省钱攻略
- 📅 **行程安排**: 定制个性化旅游行程和时间规划
- 🔍 **攻略搜索**: 快速搜索和管理旅游攻略内容

## 技术栈

### 后端
- **FastAPI** - 高性能Web框架
- **LangChain** - RAG框架
- **ChromaDB** - 向量数据库
- **DeepSeek API** - 大语言模型
- **Sentence Transformers** - 文本嵌入模型

### 前端
- **React 18** - 用户界面框架
- **Vite** - 构建工具
- **Ant Design** - UI组件库
- **Axios** - HTTP客户端

## 项目结构

```
rag_ai/
├── backend/              # FastAPI后端
│   ├── main.py          # 主应用文件
│   └── .env.example     # 环境变量示例
├── frontend/            # React前端
│   ├── src/
│   │   ├── App.jsx      # 主组件
│   │   ├── main.jsx     # 入口文件
│   │   └── index.css    # 样式文件
│   ├── package.json     # 前端依赖
│   └── vite.config.js   # Vite配置
├── vectorstores/        # 向量数据库（现有）
├── requirements.txt     # Python依赖
├── start_backend.py     # 后端启动脚本
├── start_frontend.bat   # 前端启动脚本
└── README.md           # 项目说明
```

## 快速开始

### 1. 环境准备

确保已安装以下软件：
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 2. 配置环境变量

复制环境变量示例文件：
```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 文件，配置DeepSeek API密钥：
```env
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

### 3. 安装依赖

#### 后端依赖
```bash
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 4. 启动服务

#### 方式一：使用启动脚本（推荐）

**启动后端：**
```bash
python start_backend.py
```

**启动前端：**
```bash
start_frontend.bat
```

#### 方式二：手动启动

**启动后端：**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端：**
```bash
cd frontend
npm run dev
```

### 5. 访问应用

- 前端界面：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 功能特性

### 核心功能
- ✅ 基于本地向量数据库的知识检索
- ✅ 智能问答对话界面
- ✅ 答案来源追溯
- ✅ 实时系统状态监控
- ✅ 响应式Web界面

### 技术特性
- ✅ 前后端分离架构
- ✅ RESTful API设计
- ✅ 向量相似度检索
- ✅ 大语言模型集成
- ✅ 跨域请求支持
- ✅ 错误处理和日志记录

## API接口

### 健康检查
```http
GET /health
```

### 查询知识库
```http
POST /query
Content-Type: application/json

{
  "question": "你的问题",
  "top_k": 3
}
```

### 获取向量数据库信息
```http
GET /vectorstore/info
```

## 使用说明

1. **提问技巧**：
   - 使用具体、明确的问题
   - 避免过于宽泛的询问
   - 可以进行多轮对话

2. **系统监控**：
   - 右侧面板显示系统状态
   - 包括文档数量、数据库状态等

3. **答案来源**：
   - 每个回答都会显示参考来源
   - 帮助验证答案的可靠性

## 开发指南

### 添加新功能

1. **后端API扩展**：
   - 在 `backend/main.py` 中添加新的路由
   - 遵循FastAPI的最佳实践

2. **前端组件开发**：
   - 在 `frontend/src/` 中添加新组件
   - 使用Ant Design组件库

### 自定义配置

1. **模型配置**：
   - 修改 `backend/main.py` 中的嵌入模型
   - 调整检索参数

2. **界面定制**：
   - 修改 `frontend/src/index.css` 样式
   - 调整Ant Design主题

## 故障排除

### 常见问题

1. **后端启动失败**：
   - 检查Python依赖是否完整安装
   - 确认向量数据库路径正确
   - 验证DeepSeek API密钥

2. **前端无法连接后端**：
   - 确认后端服务已启动（端口8000）
   - 检查CORS配置
   - 验证代理设置

3. **查询无结果**：
   - 检查向量数据库是否包含数据
   - 确认嵌入模型加载正常
   - 验证API密钥有效性

### 日志查看

- 后端日志：控制台输出
- 前端日志：浏览器开发者工具

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
