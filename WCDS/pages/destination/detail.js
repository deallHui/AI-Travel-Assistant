Page({
  data: {
    destination: {}
  },
  onLoad(options) {
    const id = options.id
    wx.cloud.database().collection('destinations').where({ id }).get().then(res => {
      this.setData({ destination: res.data[0] })
    })
  }
}) 