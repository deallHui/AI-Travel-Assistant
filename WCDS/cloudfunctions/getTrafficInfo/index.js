const cloud = require('wx-server-sdk')
const axios = require('axios')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

exports.main = async (event, context) => {
  try {
    const { road, city } = event // 前端传入 road（道路名）、city（城市名）

    // 检查必要参数
    if (!city || !road) {
      return {
        success: false,
        summary: '请输入完整的城市名和道路名'
      }
    }

    const key = 'db8dd86087d25a0e06770f57c9c599f6' // 修复了API密钥前的制表符
    // 高德交通态势API
    const url = `https://restapi.amap.com/v3/traffic/status/road?key=${key}&name=${encodeURIComponent(road)}&city=${encodeURIComponent(city)}`

    console.log('请求URL:', url)
    const res = await axios.get(url)
    console.log('高德API返回:', res.data)

    // 处理高德API返回的数据
    if (res.data && res.data.status === '1' && res.data.trafficinfo) {
      const trafficInfo = res.data.trafficinfo
      let summary = ''

      // 构建交通信息摘要
      if (trafficInfo.description) {
        summary = trafficInfo.description
      } else if (trafficInfo.evaluation) {
        const eval = trafficInfo.evaluation
        summary = `道路状态：${eval.description || '未知'}，畅通率：${eval.expedite || '0%'}，拥堵率：${eval.congested || '0%'}，严重拥堵率：${eval.blocked || '0%'}`
      } else {
        summary = '该道路交通状态正常'
      }

      return {
        success: true,
        summary: summary,
        rawData: res.data // 保留原始数据用于调试
      }
    } else {
      // API调用失败或无数据
      const errorMsg = res.data?.info || '获取交通信息失败'
      console.log('高德API错误:', errorMsg, res.data)

      return {
        success: false,
        summary: `暂无该道路的详细交通信息（${errorMsg}）`
      }
    }
  } catch (error) {
    console.error('交通信息查询错误:', error)
    return {
      success: false,
      summary: '交通信息查询服务暂时不可用，请稍后重试'
    }
  }
}