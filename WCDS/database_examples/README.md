# 云开发数据库数据导入指南

## 概述
为了让index页面正常显示内容，您需要在微信小程序云开发控制台中创建以下数据库集合并导入相应的数据。

## 需要创建的集合

### 1. destinations（目的地集合）
**用途**: index页面显示的推荐目的地列表
**文件**: `destinations_collection.json`
**字段说明**:
- `id`: 目的地唯一标识
- `name`: 目的地名称
- `description`: 目的地描述
- `imageUrl`: 目的地图片URL（需要替换为实际图片地址）
- `tags`: 标签数组
- `budget`: 预算类型（economic/comfort/luxury）
- `recommendedTime`: 推荐游玩时间（1-3/4-7/7+）
- `preferences`: 偏好类型（nature/culture/food/leisure）
- `attractions`: 景点列表
- `weather`: 天气信息
- `traffic`: 交通信息

### 2. city（城市集合）
**用途**: 天气查询功能使用的城市数据
**文件**: `city_collection.json`
**字段说明**:
- `name`: 城市名称
- `id`: 和风天气API使用的城市ID
- `province`: 省份
- `country`: 国家

### 3. travel_articles（旅游文章集合）
**用途**: 文章页面显示的旅游攻略文章
**文件**: `travel_articles_collection.json`
**字段说明**:
- `title`: 文章标题
- `content`: 文章内容
- `author`: 作者
- `category`: 分类（攻略/摄影/游记/美食/度假/文化）
- `destination`: 目的地
- `publishDate`: 发布日期
- `views`: 浏览量
- `likes`: 点赞数
- `tags`: 标签数组

### 4. itineraries（行程集合）
**用途**: 用户创建的旅行行程数据
**文件**: `itineraries_collection.json`
**字段说明**:
- `userId`: 用户ID（微信openid）
- `from`: 出发地
- `destinationId`: 目的地ID
- `startDate`: 开始日期
- `endDate`: 结束日期
- `schedule`: 行程安排数组
- `reminders`: 提醒事项数组
- `createTime`: 创建时间
- `status`: 状态

## 导入步骤

### 方法一：通过云开发控制台导入

1. 打开微信开发者工具
2. 进入云开发控制台
3. 选择"数据库"
4. 点击"创建集合"，创建上述4个集合
5. 进入每个集合，点击"导入"
6. 选择对应的JSON文件进行导入

### 方法二：通过代码批量导入

您也可以创建一个云函数来批量导入数据：

```javascript
// 云函数：initDatabase
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event, context) => {
  try {
    // 导入destinations数据
    const destinations = [/* 复制destinations_collection.json的内容 */]
    await db.collection('destinations').add({
      data: destinations
    })
    
    // 导入其他集合数据...
    
    return { success: true, message: '数据导入成功' }
  } catch (error) {
    return { success: false, error: error.message }
  }
}
```

## 注意事项

1. **图片URL**: 示例数据中的图片URL需要替换为实际可访问的图片地址
2. **用户ID**: itineraries集合中的userId需要替换为实际的微信用户openid
3. **城市ID**: city集合中的id字段是和风天气API使用的城市编码，如需使用其他天气API请相应调整
4. **索引**: 建议为常用查询字段创建索引以提高查询性能

## 数据量说明

- destinations: 6条示例数据（北京、上海、杭州、成都、三亚、西安）
- city: 15条城市数据（主要旅游城市）
- travel_articles: 6篇示例文章
- itineraries: 2条示例行程

## 扩展建议

1. 可以根据实际需求添加更多目的地数据
2. 补充更多城市的天气查询数据
3. 增加更多旅游文章内容
4. 根据用户反馈优化数据结构

导入这些数据后，您的index页面就能正常显示推荐目的地列表，用户可以进行筛选和查看详情了。
