# 🚀 微信小程序RAG AI集成配置指南

## 📋 当前配置状态

### ✅ 已完成配置
- **RAG API服务**: Docker容器运行正常
- **公网访问**: cpolar隧道已建立
- **API地址**: https://47c24b5e.r38.cpolar.top
- **小程序配置**: 已更新API地址
- **云函数**: 已更新连接配置

## 🔧 配置步骤

### 1. 微信开发者工具配置

#### 1.1 打开项目
```
文件 → 打开 → 选择 WCDS 文件夹
```

#### 1.2 配置域名白名单
```
详情 → 本地设置 → 勾选 "不校验合法域名、web-view、TLS版本..."
```

或在微信小程序后台配置合法域名：
- **request合法域名**: `47c24b5e.r38.cpolar.top`

#### 1.3 云函数部署
```
1. 右键点击 cloudfunctions/getQASystem
2. 选择 "上传并部署: 云端安装依赖"
3. 等待部署完成（约1-2分钟）
```

### 2. 测试集成功能

#### 2.1 运行部署脚本
```bash
cd WCDS
deploy_miniprogram.bat
```

#### 2.2 手动测试API
```bash
# 健康检查
curl https://47c24b5e.r38.cpolar.top/health

# 微信API测试
curl -X POST "https://47c24b5e.r38.cpolar.top/wechat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "openid": "test_user",
    "question": "推荐一些北京的景点",
    "location": {"city": "北京"}
  }'
```

#### 2.3 小程序内测试
1. 进入 "智能助手" 页面
2. 发送测试消息: "推荐一些北京的景点"
3. 检查是否正常回复

#### 2.4 运行测试脚本
在微信开发者工具控制台中：
```javascript
// 复制 test_rag_integration.js 内容到控制台
// 然后运行
runAllTests()
```

## 📱 小程序功能说明

### 主要功能
- **智能问答**: 基于RAG AI的旅游咨询
- **位置感知**: 结合用户位置提供精准建议
- **多模式回答**: 知识库 + AI搜索增强
- **实时健康检查**: 监控后端服务状态

### API接口
- **查询接口**: `/wechat/query`
- **健康检查**: `/wechat/health`
- **通用查询**: `/query`
- **网络搜索**: `/search`

## 🔄 URL更新流程

当cpolar URL发生变化时，需要更新以下文件：

### 1. 更新配置文件
```javascript
// WCDS/config/api.js
ragApiBaseUrl: 'https://NEW_CPOLAR_URL'
```

### 2. 更新云函数
```javascript
// WCDS/cloudfunctions/getQASystem/index.js
ragApiBaseUrl: 'https://NEW_CPOLAR_URL'
```

### 3. 重新部署云函数
```
右键 getQASystem → 上传并部署: 云端安装依赖
```

## 🛠️ 故障排除

### 常见问题

#### 1. 云函数调用失败
**症状**: 小程序显示"网络连接失败"
**解决方案**:
- 检查云函数是否正确部署
- 确认cpolar隧道正常运行
- 查看云函数日志排查错误

#### 2. API连接超时
**症状**: 请求超时或404错误
**解决方案**:
- 确认Docker容器运行状态
- 检查cpolar URL是否有效
- 测试API健康检查接口

#### 3. 回答质量不佳
**症状**: AI回答不准确或不相关
**解决方案**:
- 检查向量数据库是否正确初始化
- 确认DeepSeek API密钥有效
- 查看后端日志分析问题

### 调试命令

```bash
# 检查Docker状态
docker ps
docker logs rag-travel-api-fast

# 检查cpolar状态
curl https://47c24b5e.r38.cpolar.top/health

# 测试API功能
curl -X POST "https://47c24b5e.r38.cpolar.top/wechat/query" \
  -H "Content-Type: application/json" \
  -d '{"openid":"test","question":"你好"}'
```

## 📊 性能优化

### 1. 云函数优化
- 设置合理的超时时间（15-30秒）
- 使用连接池减少建立连接时间
- 实现智能降级机制

### 2. API优化
- 启用响应缓存
- 优化向量搜索参数
- 使用异步处理长时间查询

### 3. 用户体验优化
- 添加加载动画
- 实现消息重发功能
- 提供离线提示

## 🎯 部署检查清单

- [ ] Docker容器运行正常
- [ ] cpolar隧道建立成功
- [ ] API健康检查通过
- [ ] 小程序配置更新
- [ ] 云函数部署成功
- [ ] 功能测试通过
- [ ] 性能测试达标

## 📞 技术支持

如遇问题，请提供以下信息：
1. 错误截图或日志
2. 当前cpolar URL
3. Docker容器状态
4. 云函数部署状态
5. 具体复现步骤

---

**🎉 配置完成后，您的微信小程序就可以使用强大的RAG AI功能了！**
