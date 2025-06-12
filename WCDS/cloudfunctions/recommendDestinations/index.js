// 云函数入口文件
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV }) // 使用当前云环境

// 云函数入口函数
exports.main = async (event, context) => {
  console.log('=== recommendDestinations 云函数开始执行 ===')
  console.log('接收到的参数：', JSON.stringify(event, null, 2))

  const db = cloud.database()
  const { filters = {} } = event
  const { budget, time, preference } = filters

  try {
    // 构建查询条件
    let query = {}
    if (budget) query.budget = budget
    if (time) query.recommendedTime = time
    if (preference) query.preferences = preference

    console.log('构建的查询条件：', JSON.stringify(query, null, 2))

    // 从数据库获取目的地数据
    const destinations = await db.collection('destinations')
      .where(query)
      .limit(20)
      .get()

    console.log('数据库查询成功')
    console.log('查询到的数据条数：', destinations.data.length)
    console.log('第一条数据示例：', destinations.data[0] ? JSON.stringify(destinations.data[0], null, 2) : '无数据')

    const result = {
      success: true,
      data: destinations.data,
      count: destinations.data.length,
      message: '查询成功'
    }

    console.log('准备返回的结果：', JSON.stringify(result, null, 2))
    console.log('=== recommendDestinations 云函数执行完成 ===')

    return result
  } catch (err) {
    console.error('=== recommendDestinations 云函数执行出错 ===')
    console.error('错误详情：', err)

    const errorResult = {
      success: false,
      error: err.message || err.toString(),
      data: [],
      message: '查询失败'
    }

    console.log('返回的错误结果：', JSON.stringify(errorResult, null, 2))
    return errorResult
  }
}