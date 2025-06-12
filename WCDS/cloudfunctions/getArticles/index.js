// 云函数入口文件
const cloud = require('wx-server-sdk')
const db = cloud.database()

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV }) // 使用当前云环境

// 云函数入口函数
exports.main = async (event, context) => {
  const { category, limit = 10 } = event
  
  try {
    // 构建查询条件
    let query = {}
    if (category) query.category = category
    
    // 从数据库获取文章数据
    const articles = await db.collection('travel_articles')
      .where(query)
      .limit(limit)
      .orderBy('publishDate', 'desc')
      .get()
    
    return {
      success: true,
      data: articles.data
    }
  } catch (err) {
    console.error(err)
    return {
      success: false,
      error: err
    }
  }
}