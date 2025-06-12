// pages/comunity/comunity.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    qaList: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.loadQA()
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 页面显示时重新加载数据，确保点赞状态正确
    this.loadQA()
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  loadQA() {
    // 先获取用户openid
    this.getUserOpenid().then(openid => {
      console.log('当前用户openid：', openid)

      wx.cloud.database().collection('qa_posts').orderBy('createTime', 'desc').get().then(res => {
        console.log('从数据库获取的原始数据：', res.data)

        // 为每个帖子添加用户点赞状态
        const qaList = res.data.map(item => {
          const isLiked = item.likes && Array.isArray(item.likes) && item.likes.includes(openid)
          const likesCount = (item.likes && Array.isArray(item.likes) && item.likes.length) || 0

          console.log(`帖子 ${item.title} - likes:`, item.likes, 'isLiked:', isLiked, 'count:', likesCount)

          return {
            ...item,
            isLiked: isLiked,
            likesCount: likesCount
          }
        })

        console.log('处理后的QA数据：', qaList)
        this.setData({ qaList })
      }).catch(err => {
        console.error('加载QA数据失败：', err)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      })
    })
  },

  // 获取用户openid
  getUserOpenid() {
    return new Promise((resolve) => {
      // 先尝试从缓存获取
      let openid = wx.getStorageSync('openid')
      if (openid) {
        console.log('从缓存获取openid：', openid)
        resolve(openid)
        return
      }

      // 如果缓存没有，调用云函数获取
      wx.cloud.callFunction({
        name: 'login'
      }).then(res => {
        openid = res.result.openid
        console.log('从云函数获取openid：', openid)
        wx.setStorageSync('openid', openid)
        resolve(openid)
      }).catch(err => {
        console.error('获取openid失败：', err)
        // 使用临时ID作为备用
        openid = 'temp_user_' + Date.now()
        console.log('使用临时openid：', openid)
        wx.setStorageSync('openid', openid)
        resolve(openid)
      })
    })
  },

  goToAsk() {
    wx.navigateTo({ url: '/pages/share/edit' })
  },

  // 测试数据库写入权限
  testDatabaseWrite() {
    console.log('=== 开始测试数据库写入权限 ===')

    this.getUserOpenid().then(openid => {
      console.log('测试用户ID：', openid)

      // 获取第一个帖子进行测试
      if (this.data.qaList.length === 0) {
        wx.showToast({ title: '没有帖子可测试', icon: 'none' })
        return
      }

      const testPost = this.data.qaList[0]
      const testId = testPost._id
      const testData = {
        testField: 'test_' + Date.now(),
        testUser: openid
      }

      console.log('测试帖子ID：', testId)
      console.log('测试数据：', testData)

      // 测试简单字段更新
      wx.cloud.database().collection('qa_posts').doc(testId).update({
        data: testData
      }).then(res => {
        console.log('简单字段更新成功：', res)

        // 测试数组操作 - 使用直接设置数组的方法
        const likesData = {
          likes: [openid, 'test_user_2', 'test_user_3'] // 添加多个测试用户
        }

        console.log('测试数组操作，数据：', likesData)

        return wx.cloud.database().collection('qa_posts').doc(testId).update({
          data: likesData
        })
      }).then(res => {
        console.log('数组操作成功：', res)

        // 验证结果
        return wx.cloud.database().collection('qa_posts').doc(testId).get()
      }).then(res => {
        console.log('验证结果：', res.data)
        console.log('likes字段：', res.data.likes)

        wx.showToast({
          title: '数据库测试成功',
          icon: 'success'
        })

        // 重新加载数据
        this.loadQA()
      }).catch(err => {
        console.error('数据库测试失败：', err)
        console.error('错误详情：', JSON.stringify(err, null, 2))

        wx.showToast({
          title: '数据库测试失败：' + (err.message || err.errMsg),
          icon: 'none',
          duration: 3000
        })
      })
    })
  },

  likePost(e) {
    e.stopPropagation && e.stopPropagation();
    const { id, index } = e.currentTarget.dataset;

    console.log('=== 点赞操作开始（使用云函数）===')
    console.log('帖子ID：', id)

    // 使用云函数进行点赞操作
    wx.cloud.callFunction({
      name: 'likePost',
      data: {
        postId: id,
        action: 'toggle' // 切换点赞状态
      }
    }).then(res => {
      console.log('点赞云函数返回：', res.result)

      if (res.result.success) {
        // 更新本地状态
        let qaList = [...this.data.qaList];
        qaList[index].likes = res.result.likes || [];
        qaList[index].isLiked = res.result.isLiked;
        qaList[index].likesCount = res.result.likesCount;

        console.log('更新后的本地状态：', qaList[index])
        this.setData({ qaList });

        wx.showToast({
          title: res.result.message,
          icon: 'success',
          duration: 1000
        });
      } else {
        console.error('点赞操作失败：', res.result.error)
        wx.showToast({
          title: res.result.message || '操作失败',
          icon: 'none'
        });
      }
    }).catch(err => {
      console.error('调用点赞云函数失败：', err)
      wx.showToast({
        title: '网络错误，请重试',
        icon: 'none'
      });
    })
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/comunity/detail?id=${id}` });
  }
})