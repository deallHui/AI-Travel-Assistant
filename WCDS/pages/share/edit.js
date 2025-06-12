Page({
  data: {
    title: '',
    content: ''
  },
  onTitleInput(e) {
    this.setData({ title: e.detail.value })
  },
  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },
  onSubmit() {
    const { title, content } = this.data
    if (!title || !content) {
      wx.showToast({ title: '请填写完整', icon: 'none' })
      return
    }
    wx.cloud.database().collection('qa_posts').add({
      data: {
        title,
        content,
        createTime: new Date(),
        answers: [],
        tags: []
      }
    }).then(() => {
      wx.showToast({ title: '发布成功' })
      wx.navigateBack()
    })
  }
}) 