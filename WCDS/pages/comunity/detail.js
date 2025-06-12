Page({
  data: {
    post: {},
    commentValue: ''
  },
  onLoad(options) {
    this.postId = options.id;
    this.loadPost();
  },

  loadPost() {
    this.getUserOpenid().then(openid => {
      console.log('详情页当前用户openid：', openid)

      wx.cloud.database().collection('qa_posts').doc(this.postId).get().then(res => {
        console.log('详情页从数据库获取的原始数据：', res.data)

        const isLiked = res.data.likes && Array.isArray(res.data.likes) && res.data.likes.includes(openid)
        const likesCount = (res.data.likes && Array.isArray(res.data.likes) && res.data.likes.length) || 0

        const post = {
          ...res.data,
          isLiked: isLiked,
          likesCount: likesCount
        };

        console.log('详情页处理后的帖子数据：', post);
        this.setData({ post });
      }).catch(err => {
        console.error('加载帖子详情失败：', err);
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        });
      });
    })
  },

  // 获取用户openid（与列表页保持一致）
  getUserOpenid() {
    return new Promise((resolve) => {
      // 先尝试从缓存获取
      let openid = wx.getStorageSync('openid')
      if (openid) {
        console.log('详情页从缓存获取openid：', openid)
        resolve(openid)
        return
      }

      // 如果缓存没有，调用云函数获取
      wx.cloud.callFunction({
        name: 'login'
      }).then(res => {
        openid = res.result.openid
        console.log('详情页从云函数获取openid：', openid)
        wx.setStorageSync('openid', openid)
        resolve(openid)
      }).catch(err => {
        console.error('详情页获取openid失败：', err)
        // 使用临时ID作为备用
        openid = 'temp_user_' + Date.now()
        console.log('详情页使用临时openid：', openid)
        wx.setStorageSync('openid', openid)
        resolve(openid)
      })
    })
  },
  likePost() {
    console.log('=== 详情页点赞操作开始（使用云函数）===');
    console.log('帖子ID：', this.data.post._id);

    // 使用云函数进行点赞操作
    wx.cloud.callFunction({
      name: 'likePost',
      data: {
        postId: this.data.post._id,
        action: 'toggle' // 切换点赞状态
      }
    }).then(res => {
      console.log('详情页点赞云函数返回：', res.result)

      if (res.result.success) {
        // 更新本地状态
        let post = { ...this.data.post };
        post.likes = res.result.likes || [];
        post.isLiked = res.result.isLiked;
        post.likesCount = res.result.likesCount;

        console.log('详情页更新后的状态：', post);
        this.setData({ post });

        wx.showToast({
          title: res.result.message,
          icon: 'success',
          duration: 1000
        });
      } else {
        console.error('详情页点赞操作失败：', res.result.error)
        wx.showToast({
          title: res.result.message || '操作失败',
          icon: 'none'
        });
      }
    }).catch(err => {
      console.error('详情页调用点赞云函数失败：', err)
      wx.showToast({
        title: '网络错误，请重试',
        icon: 'none'
      });
    })
  },
  onCommentInput(e) {
    this.setData({ commentValue: e.detail.value });
  },
  submitComment() {
    const openid = wx.getStorageSync('openid') || 'test_openid';
    const comment = {
      userId: openid,
      content: this.data.commentValue,
      createTime: new Date().toLocaleString()
    };
    wx.cloud.database().collection('qa_posts').doc(this.data.post._id).update({
      data: { comments: wx.cloud.database().command.push([comment]) }
    }).then(() => {
      let post = this.data.post;
      post.comments = post.comments || [];
      post.comments.push(comment);
      this.setData({ post, commentValue: '' });
      wx.showToast({ title: '评论成功' });
    });
  }
});