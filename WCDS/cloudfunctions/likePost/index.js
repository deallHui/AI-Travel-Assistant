// 云函数入口文件
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

// 云函数入口函数
exports.main = async (event, context) => {
  console.log('=== likePost云函数开始执行 ===')
  console.log('接收到的参数：', event)
  
  const db = cloud.database()
  const wxContext = cloud.getWXContext()
  const openid = wxContext.OPENID
  const { postId, action } = event // action: 'like' 或 'unlike'
  
  try {
    // 获取当前帖子数据
    const postRes = await db.collection('qa_posts').doc(postId).get()
    
    if (!postRes.data) {
      return {
        success: false,
        error: '帖子不存在'
      }
    }
    
    const post = postRes.data
    const currentLikes = post.likes && Array.isArray(post.likes) ? post.likes : []
    const isCurrentlyLiked = currentLikes.includes(openid)
    
    console.log('当前帖子likes：', currentLikes)
    console.log('用户openid：', openid)
    console.log('当前是否已点赞：', isCurrentlyLiked)
    console.log('请求操作：', action)
    
    let newLikes
    let resultAction
    
    if (action === 'like' && !isCurrentlyLiked) {
      // 添加点赞
      newLikes = [...currentLikes, openid]
      resultAction = 'liked'
    } else if (action === 'unlike' && isCurrentlyLiked) {
      // 取消点赞
      newLikes = currentLikes.filter(uid => uid !== openid)
      resultAction = 'unliked'
    } else if (action === 'toggle') {
      // 切换点赞状态
      if (isCurrentlyLiked) {
        newLikes = currentLikes.filter(uid => uid !== openid)
        resultAction = 'unliked'
      } else {
        newLikes = [...currentLikes, openid]
        resultAction = 'liked'
      }
    } else {
      // 无需操作
      return {
        success: true,
        action: 'no_change',
        isLiked: isCurrentlyLiked,
        likesCount: currentLikes.length,
        message: '状态无变化'
      }
    }
    
    console.log('新的likes数组：', newLikes)
    
    // 更新数据库
    const updateRes = await db.collection('qa_posts').doc(postId).update({
      data: {
        likes: newLikes
      }
    })
    
    console.log('数据库更新结果：', updateRes)
    
    return {
      success: true,
      action: resultAction,
      isLiked: newLikes.includes(openid),
      likesCount: newLikes.length,
      likes: newLikes,
      message: resultAction === 'liked' ? '点赞成功' : '取消点赞成功'
    }
    
  } catch (error) {
    console.error('likePost云函数执行错误：', error)
    return {
      success: false,
      error: error.message || error.toString(),
      message: '操作失败'
    }
  }
}
