// 云函数入口文件 - 测试版本
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV }) // 使用当前云环境

// 云函数入口函数 - 测试版本，返回模拟数据
exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext()
  
  try {
    const { question, location } = event
    
    console.log('收到测试请求:', { question, location, openid: wxContext.OPENID })
    
    // 参数验证
    if (!question || typeof question !== 'string' || question.trim().length === 0) {
      return {
        success: false,
        message: '请输入有效的问题',
        timestamp: new Date().toISOString()
      }
    }

    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 根据问题返回不同的模拟回答
    let mockAnswer = '';
    const questionLower = question.toLowerCase();
    
    if (questionLower.includes('北京') || questionLower.includes('景点')) {
      mockAnswer = `🏛️ **北京必去景点推荐**

**历史文化类：**
• 故宫博物院 - 明清皇宫，世界文化遗产
• 天坛公园 - 明清皇帝祭天的场所
• 颐和园 - 中国古典园林艺术的杰作

**现代地标：**
• 天安门广场 - 世界最大的城市广场
• 鸟巢、水立方 - 奥运场馆建筑群

**特色街区：**
• 南锣鼓巷 - 胡同文化体验
• 王府井大街 - 购物美食天堂

💡 **小贴士：** 建议提前预约故宫门票，避开节假日高峰期。`;
    } else if (questionLower.includes('三亚') || questionLower.includes('美食')) {
      mockAnswer = `🌴 **三亚特色美食推荐**

**海鲜类：**
• 清蒸石斑鱼 - 肉质鲜美，营养丰富
• 白切文昌鸡 - 海南四大名菜之首
• 椰子蟹 - 三亚特色海鲜

**热带水果：**
• 椰子 - 新鲜椰汁，清热解暑
• 芒果 - 香甜多汁，品种丰富
• 火龙果 - 营养价值高

**特色小吃：**
• 海南粉 - 当地传统米粉
• 椰子饭 - 香糯可口
• 清补凉 - 消暑甜品

🍽️ **推荐地点：** 第一市场、春园海鲜广场、亚龙湾美食街`;
    } else if (questionLower.includes('上海') || questionLower.includes('杭州') || questionLower.includes('交通')) {
      mockAnswer = `🚄 **上海到杭州交通指南**

**高铁（推荐）：**
• 车程：约1小时
• 班次：每15-30分钟一班
• 票价：二等座约73元
• 车站：上海虹桥站 → 杭州东站

**汽车：**
• 车程：约2-3小时
• 班次：每30分钟一班
• 票价：约60-80元
• 车站：上海南站 → 杭州汽车客运中心

**自驾：**
• 路程：约180公里
• 时间：约2.5小时
• 路线：沪杭高速G60
• 过路费：约80元

🎫 **购票建议：** 提前在12306或携程购买高铁票，节假日需提前预订。`;
    } else {
      mockAnswer = `🤖 **AI旅游助手为您服务**

感谢您的咨询！我是专业的旅游助手，可以为您提供：

📍 **景点推荐** - 热门景点、小众秘境
🏨 **住宿建议** - 酒店民宿、性价比推荐  
🍜 **美食攻略** - 当地特色、网红餐厅
🚗 **交通指南** - 路线规划、出行方式
💰 **预算规划** - 费用估算、省钱攻略

请告诉我您想了解哪个城市或具体需求，我会为您提供详细的旅游建议！

💡 **热门问题：**
• "推荐一些北京的必去景点"
• "三亚有什么好吃的美食"  
• "上海到杭州怎么去最方便"`;
    }

    // 返回成功结果
    return {
      success: true,
      message: '查询成功',
      data: {
        answer: mockAnswer,
        sources: ['旅游攻略知识库', 'AI智能推荐'],
        confidence: 0.85,
        enhanced_with_ai: false,
        has_location: !!location,
        test_mode: true
      },
      openid: wxContext.OPENID,
      timestamp: new Date().toISOString()
    }

  } catch (error) {
    console.error('测试云函数执行失败:', error)

    return {
      success: false,
      message: '服务暂时不可用，请稍后重试',
      error: error.message,
      openid: wxContext.OPENID,
      timestamp: new Date().toISOString()
    }
  }
}
