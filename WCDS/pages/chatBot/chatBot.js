// pages/chatBot/chatBot.js
Page({
  /**
   * 页面的初始数据
   */
  data: {
    messages: [], // 聊天消息列表
    inputText: '', // 输入框文本
    isLoading: false, // 是否正在加载
    scrollTop: 0, // 滚动位置
    userLocation: null, // 用户位置信息
    systemStatus: {
      connected: false,
      lastCheck: null
    }
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 添加欢迎消息
    this.addMessage({
      type: 'bot',
      content: '🎯 您好！我是您的专属旅游助手，可以为您提供：\n\n📍 景点推荐和攻略\n🏨 住宿和美食建议\n🚗 交通和路线规划\n💡 实用旅游小贴士\n\n请告诉我您想了解什么？',
      timestamp: new Date().toISOString()
    });

    // 检查系统状态
    this.checkSystemHealth();

    // 获取用户位置（可选）
    this.getUserLocation();
  },

  /**
   * 检查系统健康状态
   */
  checkSystemHealth() {
    wx.cloud.callFunction({
      name: 'getQASystem',
      data: {
        question: 'health_check',
        action: 'health'
      }
    }).then(res => {
      console.log('系统健康检查:', res);
      this.setData({
        'systemStatus.connected': res.result.success,
        'systemStatus.lastCheck': new Date().toISOString()
      });
    }).catch(err => {
      console.error('系统健康检查失败:', err);
      this.setData({
        'systemStatus.connected': false,
        'systemStatus.lastCheck': new Date().toISOString()
      });
    });
  },

  /**
   * 获取用户位置
   */
  getUserLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        console.log('获取位置成功:', res);
        this.setData({
          userLocation: {
            latitude: res.latitude,
            longitude: res.longitude
          }
        });

        // 可选：获取城市信息
        this.getCityFromLocation(res.latitude, res.longitude);
      },
      fail: (err) => {
        console.log('获取位置失败:', err);
        // 位置获取失败不影响正常使用
      }
    });
  },

  /**
   * 根据坐标获取城市信息
   */
  getCityFromLocation(latitude, longitude) {
    // 这里可以调用地图API获取城市信息
    // 暂时使用模拟数据
    const mockCity = '当前城市';
    this.setData({
      'userLocation.city': mockCity
    });
  },

  /**
   * 添加消息到聊天列表
   */
  addMessage(message) {
    const messages = this.data.messages;

    // 处理置信度百分比显示
    if (message.confidence) {
      message.confidencePercent = Math.round(message.confidence * 100);
    }

    messages.push({
      id: Date.now(),
      ...message
    });

    this.setData({
      messages: messages
    });

    // 滚动到底部
    this.scrollToBottom();
  },

  /**
   * 滚动到底部
   */
  scrollToBottom() {
    this.setData({
      scrollTop: this.data.messages.length * 1000
    });
  },

  /**
   * 输入框内容变化
   */
  onInputChange(e) {
    this.setData({
      inputText: e.detail.value
    });
  },

  /**
   * 发送消息
   */
  sendMessage(e) {
    let inputText = this.data.inputText.trim();

    if (!inputText) {
      wx.showToast({
        title: '请输入问题',
        icon: 'none'
      });
      return;
    }

    this.sendMessageWithText(inputText);
  },

  /**
   * 发送快捷问题
   */
  sendQuickMessage(e) {
    const text = e.currentTarget.dataset.text;
    if (text) {
      this.sendMessageWithText(text);
    }
  },

  /**
   * 发送消息的通用方法
   */
  sendMessageWithText(inputText) {
    if (this.data.isLoading) {
      wx.showToast({
        title: '请等待回复',
        icon: 'none'
      });
      return;
    }

    // 添加用户消息
    this.addMessage({
      type: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    });

    // 清空输入框
    this.setData({
      inputText: '',
      isLoading: true
    });

    // 调用云函数查询
    this.queryRAGSystem(inputText);
  },

  /**
   * 查询RAG系统
   */
  queryRAGSystem(question) {
    const requestData = {
      question: question,
      location: this.data.userLocation
    };

    console.log('发送查询请求:', requestData);

    wx.cloud.callFunction({
      name: 'getQASystem',
      data: requestData
    }).then(res => {
      console.log('RAG查询结果:', res);

      this.setData({
        isLoading: false
      });

      if (res.result.success) {
        // 添加AI回复
        this.addMessage({
          type: 'bot',
          content: res.result.data.answer,
          sources: res.result.data.sources,
          confidence: res.result.data.confidence,
          enhanced_with_ai: res.result.data.enhanced_with_ai,
          timestamp: res.result.timestamp
        });
      } else {
        // 添加错误消息
        this.addMessage({
          type: 'bot',
          content: `❌ ${res.result.message}\n\n请稍后重试，或检查网络连接。`,
          timestamp: new Date().toISOString(),
          isError: true
        });
      }
    }).catch(err => {
      console.error('云函数调用失败:', err);

      this.setData({
        isLoading: false
      });

      this.addMessage({
        type: 'bot',
        content: '❌ 网络连接失败，请检查网络后重试。',
        timestamp: new Date().toISOString(),
        isError: true
      });
    });
  },

  /**
   * 重新发送消息
   */
  resendMessage(e) {
    const index = e.currentTarget.dataset.index;
    const message = this.data.messages[index];

    if (message && message.type === 'user') {
      this.queryRAGSystem(message.content);
    }
  },

  /**
   * 清空聊天记录
   */
  clearChat() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有聊天记录吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            messages: []
          });

          // 重新添加欢迎消息
          this.addMessage({
            type: 'bot',
            content: '🎯 聊天记录已清空！我是您的专属旅游助手，请告诉我您想了解什么？',
            timestamp: new Date().toISOString()
          });
        }
      }
    });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {},

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {},

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {},

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {},

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    // 检查系统状态
    this.checkSystemHealth();
    wx.stopPullDownRefresh();
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {},

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: '智能旅游助手',
      desc: '专业的旅游攻略问答系统',
      path: '/pages/chatBot/chatBot'
    };
  }
});
