// 云函数入口文件 - RAG AI集成版本
const cloud = require('wx-server-sdk')
const axios = require('axios')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

// 配置
const config = {
  development: {
    // 使用最新的cpolar公网地址
    ragApiBaseUrl: 'http://47c24b5e.r38.cpolar.top',  // 当前活跃的cpolar地址
    fallbackUrls: [
      'https://47c24b5e.r38.cpolar.top', // HTTPS版本作为备用
      'http://localhost:8000',           // 本地地址
      'http://127.0.0.1:8000',
      'http://172.18.2.53:8000'          // Docker地址作为备用
    ],
    timeout: 25000  // 25秒超时（给工作链足够时间）
  },
  production: {
    ragApiBaseUrl: 'http://47c24b5e.r38.cpolar.top',  // 生产环境使用当前cpolar地址
    timeout: 45000  // 45秒超时（生产环境更长时间）
  },
  // 临时测试配置 - 使用固定回答模式
  test: {
    ragApiBaseUrl: null,  // 不调用外部API
    timeout: 5000
  }
}

// 获取当前环境配置
// 使用development模式，连接真正的RAG AI后端
const currentEnv = 'development'  // 可以改为 'development' 或 'production' 或 'test'
const apiConfig = config[currentEnv]

exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext()

  console.log('RAG AI集成版本 - 收到请求:', event)

  try {
    const { question, location, action } = event

    // 健康检查
    if (action === 'health') {
      if (currentEnv === 'test') {
        return {
          success: true,
          message: '测试模式运行正常',
          data: {
            status: 'healthy',
            mode: 'test',
            vectorstore_ready: true,
            qa_chain_ready: true,
            document_count: 24
          },
          timestamp: new Date().toISOString()
        }
      }

      try {
        const healthResponse = await axios.get(`${apiConfig.ragApiBaseUrl}/wechat/health`, {
          timeout: 10000
        })
        return {
          success: true,
          message: 'RAG AI系统运行正常',
          data: healthResponse.data.data,
          timestamp: new Date().toISOString()
        }
      } catch (healthError) {
        console.error('健康检查失败:', healthError)
        return {
          success: false,
          message: 'RAG AI系统连接失败',
          error: healthError.message,
          timestamp: new Date().toISOString()
        }
      }
    }

    // 参数验证
    if (!question || typeof question !== 'string' || question.trim().length === 0) {
      return {
        success: false,
        message: '请输入有效的问题',
        timestamp: new Date().toISOString()
      }
    }

    // 构建请求数据
    const requestData = {
      question: question.trim(),
      openid: wxContext.OPENID,
      location: location || null,
      top_k: 3
    }

    console.log('调用RAG AI接口:', requestData)

    // 测试模式 - 使用智能回答逻辑
    if (currentEnv === 'test') {
      const testAnswer = generateTestAnswer(question.trim())
      return {
        success: true,
        message: '查询成功（测试模式）',
        data: testAnswer,
        openid: wxContext.OPENID,
        timestamp: new Date().toISOString()
      }
    }

    // 先进行快速健康检查
    try {
      console.log('执行快速健康检查...')
      await axios.get(`${apiConfig.ragApiBaseUrl}/health`, {
        timeout: 3000  // 3秒快速检查
      })
      console.log('健康检查通过，调用完整API...')
    } catch (healthError) {
      console.log('健康检查失败，降级到测试模式:', healthError.message)
      const testAnswer = generateTestAnswer(question.trim())
      testAnswer.fallback_reason = '后端服务连接超时，使用本地智能回答'
      return {
        success: true,
        message: '查询成功（智能降级模式）',
        data: testAnswer,
        openid: wxContext.OPENID,
        timestamp: new Date().toISOString()
      }
    }

    // 调用RAG AI后端接口（带超时处理）
    let response
    try {
      console.log('开始调用RAG AI查询接口...')
      response = await axios.post(`${apiConfig.ragApiBaseUrl}/wechat/query`, requestData, {
        timeout: apiConfig.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      })
      console.log('RAG AI查询成功')
    } catch (queryError) {
      console.log('RAG AI查询失败，使用降级模式:', queryError.message)

      // 如果是超时或网络错误，使用智能降级
      if (queryError.code === 'ECONNABORTED' || queryError.code === 'ETIMEDOUT') {
        const testAnswer = generateTestAnswer(question.trim())
        testAnswer.fallback_reason = 'RAG AI服务响应超时，使用本地智能回答'
        return {
          success: true,
          message: '查询成功（降级模式）',
          data: testAnswer,
          openid: wxContext.OPENID,
          timestamp: new Date().toISOString()
        }
      }

      // 其他错误继续抛出
      throw queryError
    }

    console.log('RAG AI响应:', response.data)

    // 返回成功结果
    return {
      success: response.data.success,
      message: response.data.message,
      data: response.data.data,
      openid: wxContext.OPENID,
      timestamp: new Date().toISOString()
    }

  } catch (error) {
    console.error('云函数执行失败:', error)

    // 如果是网络错误，提供降级回答
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      return {
        success: false,
        message: 'RAG AI服务暂时不可用，请稍后重试',
        data: {
          answer: `🤖 **AI旅游助手**

抱歉，智能问答服务暂时不可用。

您问的是："${event.question || '未知问题'}"

请稍后重试，或者您可以：
📱 查看其他功能模块
🔄 刷新页面重新尝试
📞 联系客服获取帮助

我们正在努力恢复服务，感谢您的耐心等待！`,
          sources: ['系统提示'],
          confidence: 0.1,
          enhanced_with_ai: false,
          fallback_mode: true
        },
        error: error.message,
        openid: wxContext.OPENID,
        timestamp: new Date().toISOString()
      }
    }

    // 其他错误
    return {
      success: false,
      message: '服务暂时不可用，请稍后重试',
      error: error.message,
      openid: wxContext.OPENID,
      timestamp: new Date().toISOString()
    }
  }
}

// 测试模式智能回答生成函数
function generateTestAnswer(question) {
  const questionLower = question.toLowerCase()

  // 北京相关问题
  if (questionLower.includes('北京') || questionLower.includes('beijing')) {
    if (questionLower.includes('景点') || questionLower.includes('旅游') || questionLower.includes('推荐')) {
      return {
        answer: `🏛️ **北京必去景点推荐**

**历史文化类：**
• 故宫博物院 - 明清皇宫，世界文化遗产
• 天坛公园 - 明清皇帝祭天的场所
• 颐和园 - 中国古典园林艺术的杰作
• 圆明园 - 历史遗迹，铭记历史

**现代地标：**
• 天安门广场 - 世界最大的城市广场
• 鸟巢、水立方 - 奥运场馆建筑群
• 央视大楼 - 现代建筑奇观

**特色街区：**
• 南锣鼓巷 - 胡同文化体验
• 王府井大街 - 购物美食天堂
• 三里屯 - 时尚潮流聚集地

💡 **游览建议：** 建议提前预约故宫门票，避开节假日高峰期。可以安排2-3天游览，第一天故宫+天安门，第二天颐和园+圆明园，第三天现代景点。`,
        sources: ['旅游攻略知识库', 'AI智能推荐'],
        confidence: 0.9,
        enhanced_with_ai: false,
        test_mode: true
      }
    }

    if (questionLower.includes('美食') || questionLower.includes('吃')) {
      return {
        answer: `🍜 **北京特色美食推荐**

**传统小吃：**
• 北京烤鸭 - 全聚德、便宜坊等老字号
• 炸酱面 - 老北京传统面食
• 豆汁焦圈 - 地道北京早餐
• 驴打滚 - 传统甜点小食

**胡同美食：**
• 卤煮火烧 - 北京特色小吃
• 爆肚 - 传统清真小吃
• 糖葫芦 - 街头经典零食
• 艾窝窝 - 传统糕点

**现代餐厅：**
• 海底捞 - 知名火锅连锁
• 西贝莜面村 - 西北风味
• 眉州东坡 - 川菜名店

🍽️ **美食街推荐：** 王府井小吃街、簋街、前门大街都是品尝北京美食的好去处！`,
        sources: ['美食攻略知识库', 'AI智能推荐'],
        confidence: 0.9,
        enhanced_with_ai: false,
        test_mode: true
      }
    }
  }

  // 三亚相关问题
  if (questionLower.includes('三亚') || questionLower.includes('海南')) {
    if (questionLower.includes('景点') || questionLower.includes('旅游') || questionLower.includes('推荐')) {
      return {
        answer: `🌴 **三亚热门景点推荐**

**海滩度假：**
• 亚龙湾 - 天下第一湾，水清沙白
• 大东海 - 市区海滩，交通便利
• 海棠湾 - 高端度假区，免税购物
• 蜈支洲岛 - 潜水胜地，海上运动

**自然风光：**
• 天涯海角 - 浪漫地标，必打卡
• 南山文化旅游区 - 佛教文化圣地
• 呀诺达雨林 - 热带雨林体验
• 分界洲岛 - 海洋生态保护区

**特色体验：**
• 千古情演出 - 大型实景演出
• 免税店购物 - 海棠湾免税城
• 温泉度假 - 南田温泉、珠江南田

🏖️ **最佳时间：** 11月-次年4月是三亚旅游最佳季节，避开台风季节。`,
        sources: ['旅游攻略知识库', 'AI智能推荐'],
        confidence: 0.9,
        enhanced_with_ai: false,
        test_mode: true
      }
    }

    if (questionLower.includes('美食') || questionLower.includes('吃')) {
      return {
        answer: `🦀 **三亚特色美食推荐**

**海鲜类：**
• 清蒸石斑鱼 - 肉质鲜美，营养丰富
• 白切文昌鸡 - 海南四大名菜之首
• 椰子蟹 - 三亚特色海鲜
• 和乐蟹 - 海南名蟹，肉质鲜甜

**热带水果：**
• 椰子 - 新鲜椰汁，清热解暑
• 芒果 - 香甜多汁，品种丰富
• 火龙果 - 营养价值高
• 莲雾 - 清脆甘甜

**特色小吃：**
• 海南粉 - 当地传统米粉
• 椰子饭 - 香糯可口
• 清补凉 - 消暑甜品
• 抱罗粉 - 海南特色粉条

🍽️ **推荐地点：** 第一市场、春园海鲜广场、亚龙湾美食街都是品尝海鲜的好地方！`,
        sources: ['美食攻略知识库', 'AI智能推荐'],
        confidence: 0.9,
        enhanced_with_ai: false,
        test_mode: true
      }
    }
  }

  // 交通相关问题
  if (questionLower.includes('交通') || questionLower.includes('怎么去') || questionLower.includes('路线')) {
    return {
      answer: `🚄 **出行交通指南**

**高铁出行（推荐）：**
• 速度快，准点率高
• 覆盖全国主要城市
• 可通过12306官网/APP预订
• 建议提前15-30天购票

**飞机出行：**
• 长距离首选，节省时间
• 各大航空公司官网预订
• 关注特价机票信息
• 提前2小时到达机场

**自驾出行：**
• 自由度高，适合家庭游
• 提前规划路线和住宿
• 注意高速路况和天气
• 准备好相关证件

**市内交通：**
• 地铁：快速便捷，避免拥堵
• 公交：经济实惠，覆盖面广
• 出租车/网约车：门到门服务
• 共享单车：短距离出行

🗺️ **出行建议：** 根据距离和预算选择合适的交通方式，长途优选高铁/飞机，市内推荐地铁+步行。`,
      sources: ['交通指南知识库', 'AI智能推荐'],
      confidence: 0.85,
      enhanced_with_ai: false,
      test_mode: true
    }
  }

  // 默认回答
  return {
    answer: `🤖 **AI旅游助手为您服务**

感谢您的咨询！我是专业的旅游助手，可以为您提供：

📍 **景点推荐** - 热门景点、小众秘境
🏨 **住宿建议** - 酒店民宿、性价比推荐
🍜 **美食攻略** - 当地特色、网红餐厅
🚗 **交通指南** - 路线规划、出行方式
💰 **预算规划** - 费用估算、省钱攻略

您问的是："${question}"

请告诉我您想了解哪个城市或具体需求，我会为您提供详细的旅游建议！

💡 **热门问题示例：**
• "推荐一些北京的必去景点"
• "三亚有什么好吃的美食"
• "上海到杭州怎么去最方便"

🔄 **当前为测试模式**，正在为您提供智能回答服务。`,
    sources: ['AI智能助手', '旅游知识库'],
    confidence: 0.8,
    enhanced_with_ai: false,
    test_mode: true
  }
}