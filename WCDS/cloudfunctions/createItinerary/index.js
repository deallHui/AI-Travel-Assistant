// 云函数入口文件
const cloud = require('wx-server-sdk')
const db = cloud.database()

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV }) // 使用当前云环境

// 云函数入口函数
exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext()
  const { from, to, startDate, endDate } = event
  try {
    await db.collection('itineraries').add({
      data: {
        userId: wxContext.OPENID,
        from,
        destinationId: to,
        startDate,
        endDate,
        schedule: [],
        reminders: []
      }
    })
    return { success: true }
  } catch (e) {
    return { success: false, error: e }
  }
}