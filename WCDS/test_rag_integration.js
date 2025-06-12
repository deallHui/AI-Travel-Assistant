// 微信小程序RAG AI集成测试脚本
// 在微信开发者工具控制台中运行此脚本

console.log('🧪 开始RAG AI集成测试...');

// 测试配置
const testConfig = {
  ragApiUrl: 'https://47c24b5e.r38.cpolar.top',
  testQuestions: [
    '你好',
    '推荐一些北京的景点',
    '三亚有什么好吃的',
    '从上海到杭州怎么去'
  ]
};

// 测试API连接
async function testApiConnection() {
  console.log('📡 测试1: API连接测试');
  
  try {
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${testConfig.ragApiUrl}/health`,
        method: 'GET',
        timeout: 10000,
        success: resolve,
        fail: reject
      });
    });
    
    console.log('✅ API连接成功:', response.data);
    return true;
  } catch (error) {
    console.error('❌ API连接失败:', error);
    return false;
  }
}

// 测试微信小程序专用接口
async function testWechatApi() {
  console.log('📱 测试2: 微信小程序API测试');
  
  const testData = {
    openid: 'test_user_' + Date.now(),
    question: '推荐一些北京的景点',
    location: {
      city: '北京',
      latitude: 39.9042,
      longitude: 116.4074
    }
  };
  
  try {
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${testConfig.ragApiUrl}/wechat/query`,
        method: 'POST',
        data: testData,
        header: {
          'Content-Type': 'application/json'
        },
        timeout: 30000,
        success: resolve,
        fail: reject
      });
    });
    
    console.log('✅ 微信API测试成功:', response.data);
    return true;
  } catch (error) {
    console.error('❌ 微信API测试失败:', error);
    return false;
  }
}

// 测试云函数
async function testCloudFunction() {
  console.log('☁️ 测试3: 云函数测试');
  
  try {
    const response = await wx.cloud.callFunction({
      name: 'getQASystem',
      data: {
        question: '你好，测试云函数',
        location: null
      }
    });
    
    console.log('✅ 云函数测试成功:', response.result);
    return true;
  } catch (error) {
    console.error('❌ 云函数测试失败:', error);
    return false;
  }
}

// 批量测试问题
async function testMultipleQuestions() {
  console.log('🔄 测试4: 批量问题测试');
  
  const results = [];
  
  for (let i = 0; i < testConfig.testQuestions.length; i++) {
    const question = testConfig.testQuestions[i];
    console.log(`📝 测试问题 ${i + 1}: ${question}`);
    
    try {
      const response = await wx.cloud.callFunction({
        name: 'getQASystem',
        data: {
          question: question,
          location: null
        }
      });
      
      results.push({
        question: question,
        success: response.result.success,
        answer: response.result.data?.answer?.substring(0, 100) + '...',
        confidence: response.result.data?.confidence
      });
      
      console.log(`✅ 问题 ${i + 1} 测试成功`);
    } catch (error) {
      console.error(`❌ 问题 ${i + 1} 测试失败:`, error);
      results.push({
        question: question,
        success: false,
        error: error.message
      });
    }
    
    // 避免请求过快
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('📊 批量测试结果:', results);
  return results;
}

// 性能测试
async function testPerformance() {
  console.log('⚡ 测试5: 性能测试');
  
  const startTime = Date.now();
  
  try {
    const response = await wx.cloud.callFunction({
      name: 'getQASystem',
      data: {
        question: '性能测试问题',
        location: null
      }
    });
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    console.log(`✅ 性能测试完成: ${duration}ms`);
    
    if (duration < 5000) {
      console.log('🚀 响应速度: 优秀');
    } else if (duration < 10000) {
      console.log('👍 响应速度: 良好');
    } else {
      console.log('⚠️ 响应速度: 需要优化');
    }
    
    return duration;
  } catch (error) {
    console.error('❌ 性能测试失败:', error);
    return -1;
  }
}

// 主测试函数
async function runAllTests() {
  console.log('🎯 开始完整测试流程...');
  console.log('=====================================');
  
  const testResults = {
    apiConnection: false,
    wechatApi: false,
    cloudFunction: false,
    multipleQuestions: [],
    performance: -1,
    timestamp: new Date().toISOString()
  };
  
  // 执行所有测试
  testResults.apiConnection = await testApiConnection();
  testResults.wechatApi = await testWechatApi();
  testResults.cloudFunction = await testCloudFunction();
  testResults.multipleQuestions = await testMultipleQuestions();
  testResults.performance = await testPerformance();
  
  // 生成测试报告
  console.log('📋 测试报告');
  console.log('=====================================');
  console.log('API连接:', testResults.apiConnection ? '✅ 通过' : '❌ 失败');
  console.log('微信API:', testResults.wechatApi ? '✅ 通过' : '❌ 失败');
  console.log('云函数:', testResults.cloudFunction ? '✅ 通过' : '❌ 失败');
  console.log('批量测试:', `${testResults.multipleQuestions.filter(r => r.success).length}/${testResults.multipleQuestions.length} 通过`);
  console.log('性能测试:', testResults.performance > 0 ? `${testResults.performance}ms` : '失败');
  
  const overallSuccess = testResults.apiConnection && 
                        testResults.cloudFunction && 
                        testResults.multipleQuestions.some(r => r.success);
  
  console.log('=====================================');
  console.log('🎉 总体结果:', overallSuccess ? '✅ 集成成功' : '❌ 需要修复');
  
  if (!overallSuccess) {
    console.log('🔧 建议检查:');
    console.log('1. cpolar隧道是否正常运行');
    console.log('2. Docker容器是否健康');
    console.log('3. 云函数是否正确部署');
    console.log('4. 网络连接是否稳定');
  }
  
  return testResults;
}

// 导出测试函数
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    runAllTests,
    testApiConnection,
    testWechatApi,
    testCloudFunction,
    testMultipleQuestions,
    testPerformance
  };
}

// 如果在控制台中直接运行
if (typeof wx !== 'undefined') {
  console.log('💡 使用方法:');
  console.log('1. 在微信开发者工具控制台中运行: runAllTests()');
  console.log('2. 或单独测试: testApiConnection(), testCloudFunction() 等');
  console.log('3. 查看详细日志和测试结果');
}
