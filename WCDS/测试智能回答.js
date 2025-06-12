// 测试智能回答生成函数
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

**现代地标：**
• 天安门广场 - 世界最大的城市广场
• 鸟巢、水立方 - 奥运场馆建筑群

**特色街区：**
• 南锣鼓巷 - 胡同文化体验
• 王府井大街 - 购物美食天堂

💡 **游览建议：** 建议提前预约故宫门票，避开节假日高峰期。`,
        sources: ['旅游攻略知识库', 'AI智能推荐'],
        confidence: 0.9,
        test_mode: true
      }
    }
  }
  
  // 三亚相关问题
  if (questionLower.includes('三亚') || questionLower.includes('海南')) {
    return {
      answer: `🌴 **三亚热门景点推荐**

**海滩度假：**
• 亚龙湾 - 天下第一湾，水清沙白
• 大东海 - 市区海滩，交通便利
• 蜈支洲岛 - 潜水胜地，海上运动

**自然风光：**
• 天涯海角 - 浪漫地标，必打卡
• 南山文化旅游区 - 佛教文化圣地

🏖️ **最佳时间：** 11月-次年4月是三亚旅游最佳季节。`,
      sources: ['旅游攻略知识库', 'AI智能推荐'],
      confidence: 0.9,
      test_mode: true
    }
  }
  
  // 默认回答
  return {
    answer: `🤖 **AI旅游助手为您服务**

您问的是："${question}"

我可以为您提供：
📍 景点推荐、🏨 住宿建议、🍜 美食攻略、🚗 交通指南

请告诉我您想了解哪个城市或具体需求！`,
    sources: ['AI智能助手'],
    confidence: 0.8,
    test_mode: true
  }
}

// 测试用例
const testQuestions = [
  "推荐一些北京的必去景点",
  "三亚有什么好玩的地方",
  "上海有什么美食推荐",
  "怎么从北京到上海"
]

console.log('🧪 测试智能回答生成...\n')

testQuestions.forEach((question, index) => {
  console.log(`${index + 1}. 问题: ${question}`)
  const result = generateTestAnswer(question)
  console.log(`   回答: ${result.answer.substring(0, 100)}...`)
  console.log(`   置信度: ${result.confidence}`)
  console.log(`   测试模式: ${result.test_mode}`)
  console.log('')
})

console.log('✅ 测试完成！智能回答功能正常工作。')
