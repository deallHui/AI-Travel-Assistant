Page({
  data: {
    city: '',
    road: '',
    weather: null,
    traffic: null
  },
  onCityInput(e) {
    this.setData({ city: e.detail.value });
  },
  onRoadInput(e) {
    this.setData({ road: e.detail.value });
  },
  onSearch() {
    const city = this.data.city.trim();
    const road = this.data.road.trim();
    if (!city) {
      wx.showToast({ title: '请输入城市', icon: 'none' });
      return;
    }
    if (!road) {
      wx.showToast({ title: '请输入道路名', icon: 'none' });
      return;
    }
    // 查询天气
    wx.cloud.callFunction({
      name: 'getWeatherInfo',
      data: { location: city }
    }).then(res => {
      const result = res.result;
      if (result && result.code === "200" && result.now) {
        this.setData({
          weather: {
            temp: result.now.temp,
            text: result.now.text,
            wind: result.now.windScale,
            precip: result.now.precip
          }
        });
      } else {
        wx.showToast({ title: '天气信息获取失败', icon: 'none' });
        this.setData({ weather: null });
        console.log('天气云函数返回：', res.result);
      }
    });
    // 查询交通
    wx.cloud.callFunction({
      name: 'getTrafficInfo',
      data: { city, road }
    }).then(res => {
      console.log('交通信息云函数返回：', res.result);
      if (res.result && res.result.summary) {
        this.setData({
          traffic: {
            summary: res.result.summary
          }
        });
      } else {
        this.setData({
          traffic: {
            summary: '暂无详细交通信息'
          }
        });
      }
    }).catch(err => {
      console.error('交通信息查询失败：', err);
      this.setData({
        traffic: {
          summary: '交通信息查询失败，请稍后重试'
        }
      });
    });
  }
});