const cloud = require('wx-server-sdk')
const axios = require('axios')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

exports.main = async (event, context) => {
  const { location } = event
  const key = '7f5e46fd4619424db520b34d23f8061b'
  // 用专属API Host替换原有域名
  const apiHost = 'n45egjxap5.re.qweatherapi.com'
  // 1. 查询数据库获取城市ID
  const db = cloud.database()
  const cityRes = await db.collection('city').where({ name: location }).get()
  if (!cityRes.data.length) {
    return { code: 404, msg: '未找到该城市' }
  }
  const cityId = cityRes.data[0].id

  // 2. 用城市ID请求天气
  const url = `https://${apiHost}/v7/weather/now?location=${cityId}&key=${key}`
  console.log('请求url:', url)
  const res = await axios.get(url)
  return res.data
}