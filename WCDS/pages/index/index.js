const app = getApp()

Page({
  data: {
    destinations: [],
    searchValue: '',
    filters: {
      budget: '',
      time: '',
      preference: ''
    }
  },

  onLoad: function() {
    console.log('index页面加载')
    // 先测试云开发连接
    this.testCloudConnection()
    this.loadDestinations()
  },

  // 测试云开发连接
  testCloudConnection: function() {
    console.log('测试云开发连接...')

    // 直接查询数据库
    const db = wx.cloud.database()
    db.collection('destinations').get().then(res => {
      console.log('直接查询数据库成功：', res)
      console.log('数据库中的记录数：', res.data.length)
      if (res.data.length > 0) {
        console.log('第一条记录：', res.data[0])
      }
    }).catch(err => {
      console.error('直接查询数据库失败：', err)
    })
  },

  // 加载目的地数据
  loadDestinations: function() {
    console.log('开始加载目的地数据，当前筛选条件：', this.data.filters)

    wx.showLoading({
      title: '加载中...'
    })

    wx.cloud.callFunction({
      name: 'recommendDestinations',
      data: {
        filters: this.data.filters
      }
    }).then(res => {
      wx.hideLoading()
      console.log('云函数返回结果：', res)
      console.log('res.result类型：', typeof res.result)
      console.log('res.result内容：', JSON.stringify(res.result, null, 2))

      // 检查返回结果的格式
      if (res.result && res.result.success) {
        console.log('获取到目的地数据：', res.result.data)
        this.setData({
          destinations: res.result.data || []
        })

        if (res.result.data && res.result.data.length === 0) {
          wx.showToast({
            title: '暂无匹配的目的地',
            icon: 'none'
          })
        }
      } else {
        console.error('云函数返回格式异常，尝试使用直接数据库查询')
        console.error('异常的返回结果：', res.result)

        // 如果云函数有问题，使用直接数据库查询作为备用方案
        this.loadDestinationsDirectly()
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('调用云函数失败：', err)
      console.log('使用直接数据库查询作为备用方案')
      this.loadDestinationsDirectly()
    })
  },

  // 直接数据库查询备用方案
  loadDestinationsDirectly: function() {
    console.log('使用直接数据库查询，筛选条件：', this.data.filters)

    const db = wx.cloud.database()
    const { budget, time, preference } = this.data.filters

    // 构建查询条件
    let query = {}
    if (budget) query.budget = budget
    if (time) query.recommendedTime = time
    if (preference) query.preferences = preference

    console.log('直接查询条件：', query)

    db.collection('destinations')
      .where(query)
      .limit(20)
      .get()
      .then(res => {
        console.log('直接数据库查询成功：', res)
        this.setData({
          destinations: res.data || []
        })

        if (res.data.length === 0) {
          wx.showToast({
            title: '暂无匹配的目的地',
            icon: 'none'
          })
        } else {
          wx.showToast({
            title: `找到${res.data.length}个目的地`,
            icon: 'success',
            duration: 1500
          })
        }
      })
      .catch(err => {
        console.error('直接数据库查询失败：', err)
        wx.showToast({
          title: '数据加载失败',
          icon: 'none'
        })
      })
  },

  // 搜索输入处理
  onSearchInput: function(e) {
    this.setData({
      searchValue: e.detail.value
    })
    // 实现搜索逻辑
  },

  // 显示预算筛选
  showBudgetFilter: function() {
    wx.showActionSheet({
      itemList: ['不限', '经济型', '舒适型', '豪华型'],
      success: (res) => {
        const budgets = ['', 'economic', 'comfort', 'luxury']
        this.setData({
          'filters.budget': budgets[res.tapIndex]
        })
        console.log('预算筛选更新：', budgets[res.tapIndex])
        this.loadDestinationsDirectly()
      }
    })
  },

  // 显示时间筛选
  showTimeFilter: function() {
    wx.showActionSheet({
      itemList: ['不限', '1-3天', '4-7天', '7天以上'],
      success: (res) => {
        const times = ['', '1-3', '4-7', '7+']
        this.setData({
          'filters.time': times[res.tapIndex]
        })
        console.log('时间筛选更新：', times[res.tapIndex])
        this.loadDestinationsDirectly()
      }
    })
  },

  // 显示偏好筛选
  showPreferenceFilter: function() {
    wx.showActionSheet({
      itemList: ['不限', '自然风光', '人文历史', '美食购物', '休闲度假'],
      success: (res) => {
        const preferences = ['', 'nature', 'culture', 'food', 'leisure']
        this.setData({
          'filters.preference': preferences[res.tapIndex]
        })
        console.log('偏好筛选更新：', preferences[res.tapIndex])
        this.loadDestinationsDirectly()
      }
    })
  },

  // 跳转到目的地详情
  navigateToDetail: function(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/destination/detail?id=${id}`
    })
  },

  // 跳转到AI助手
  goToAIAssistant() {
    wx.switchTab({
      url: '/pages/chatBot/chatBot'
    })
  }
})