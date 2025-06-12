// 云函数入口文件
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

// 云函数入口函数
exports.main = async (event, context) => {
  console.log('login云函数被调用')
  
  const wxContext = cloud.getWXContext()
  
  console.log('用户openid：', wxContext.OPENID)
  console.log('用户appid：', wxContext.APPID)
  console.log('用户unionid：', wxContext.UNIONID)
  
  return {
    success: true,
    openid: wxContext.OPENID,
    appid: wxContext.APPID,
    unionid: wxContext.UNIONID,
    message: '获取用户信息成功'
  }
}
