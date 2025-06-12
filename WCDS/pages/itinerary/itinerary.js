Page({
  data: {
    itineraries: []
  },
  onLoad() {
    this.getItineraries()
  },
  // 获取用户行程
  getItineraries() {
    wx.cloud.callFunction({
      name: 'getItineraries',
      data: {}
    }).then(res => {
      this.setData({ itineraries: res.result.data })
    })
  },
  // 提交新行程
  onSubmit(e) {
    const { from, to, startDate, endDate } = e.detail.value
    wx.cloud.callFunction({
      name: 'createItinerary',
      data: {
        from, to, startDate, endDate
      }
    }).then(res => {
      wx.showToast({ title: '行程已保存' })
      this.getItineraries()
    })
  },
  setReminder(e) {
    wx.showModal({
      title: '设置提醒',
      content: '此处可集成订阅消息或本地提醒功能',
      showCancel: false
    })
  }
}) 