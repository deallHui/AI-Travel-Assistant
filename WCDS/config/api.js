// API配置文件
// 根据环境自动选择API地址

const config = {
  // 开发环境配置
  development: {
    // 使用cpolar公网地址 - 当前活跃的隧道
    ragApiBaseUrl: 'https://47c24b5e.r38.cpolar.top',
    // 备用地址
    fallbackUrls: [
      'http://172.18.2.53:8000',  // 本地Docker地址
      'http://localhost:8000'     // 本地开发地址
    ],
    timeout: 30000
  },

  // 生产环境配置
  production: {
    // 生产环境使用cpolar公网地址
    ragApiBaseUrl: 'https://47c24b5e.r38.cpolar.top',
    timeout: 30000
  }
};

// 自动检测环境
function getEnvironment() {
  // 可以根据小程序的版本类型来判断环境
  const accountInfo = wx.getAccountInfoSync();
  
  if (accountInfo.miniProgram.envVersion === 'develop' || 
      accountInfo.miniProgram.envVersion === 'trial') {
    return 'development';
  } else {
    return 'production';
  }
}

// 获取当前环境的配置
function getConfig() {
  const env = getEnvironment();
  return config[env];
}

// 导出配置
module.exports = {
  getConfig,
  getEnvironment,
  
  // 直接导出常用配置
  RAG_API_BASE_URL: getConfig().ragApiBaseUrl,
  TIMEOUT: getConfig().timeout,
  
  // API端点
  endpoints: {
    wechatQuery: '/wechat/query',
    wechatHealth: '/wechat/health',
    query: '/query',
    search: '/search'
  }
};
