// 测试RAG AI后端连接的脚本
// 可以在Node.js环境中运行此脚本来测试连接

const axios = require('axios');

// 配置 - 使用cpolar公网地址
const RAG_API_BASE_URL = 'http://6dc100db.r38.cpolar.top';
const TEST_TIMEOUT = 15000; // 15秒超时（公网可能较慢）

// 测试数据
const testQuestions = [
  '北京有什么好玩的景点？',
  '上海到杭州怎么去？',
  '三亚有什么特色美食？'
];

// 颜色输出函数
const colors = {
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`
};

// 测试健康检查
async function testHealthCheck() {
  console.log(colors.blue('\n🔍 测试健康检查接口...'));
  
  try {
    const response = await axios.get(`${RAG_API_BASE_URL}/health`, {
      timeout: TEST_TIMEOUT
    });
    
    console.log(colors.green('✅ 健康检查通过'));
    console.log('响应数据:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    console.log(colors.red('❌ 健康检查失败'));
    console.log('错误信息:', error.message);
    return false;
  }
}

// 测试微信专用健康检查
async function testWechatHealthCheck() {
  console.log(colors.blue('\n🔍 测试微信专用健康检查接口...'));
  
  try {
    const response = await axios.get(`${RAG_API_BASE_URL}/wechat/health`, {
      timeout: TEST_TIMEOUT
    });
    
    console.log(colors.green('✅ 微信健康检查通过'));
    console.log('响应数据:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    console.log(colors.red('❌ 微信健康检查失败'));
    console.log('错误信息:', error.message);
    return false;
  }
}

// 测试查询接口
async function testQuery(question) {
  console.log(colors.blue(`\n🔍 测试查询: "${question}"`));
  
  try {
    const requestData = {
      question: question,
      openid: 'test_openid_123',
      location: {
        latitude: 39.9042,
        longitude: 116.4074,
        city: '北京'
      },
      top_k: 3
    };
    
    const response = await axios.post(`${RAG_API_BASE_URL}/wechat/query`, requestData, {
      timeout: TEST_TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log(colors.green('✅ 查询成功'));
    console.log('回答:', colors.cyan(response.data.data.answer.substring(0, 200) + '...'));
    console.log('来源:', response.data.data.sources);
    console.log('置信度:', response.data.data.confidence);
    console.log('AI增强:', response.data.data.enhanced_with_ai);
    
    return true;
  } catch (error) {
    console.log(colors.red('❌ 查询失败'));
    console.log('错误信息:', error.message);
    if (error.response) {
      console.log('响应状态:', error.response.status);
      console.log('响应数据:', error.response.data);
    }
    return false;
  }
}

// 测试向量数据库信息
async function testVectorstoreInfo() {
  console.log(colors.blue('\n🔍 测试向量数据库信息接口...'));
  
  try {
    const response = await axios.get(`${RAG_API_BASE_URL}/vectorstore/info`, {
      timeout: TEST_TIMEOUT
    });
    
    console.log(colors.green('✅ 向量数据库信息获取成功'));
    console.log('文档数量:', response.data.document_count);
    console.log('嵌入模型:', response.data.embedding_model);
    console.log('LLM模型:', response.data.llm_model);
    return true;
  } catch (error) {
    console.log(colors.red('❌ 向量数据库信息获取失败'));
    console.log('错误信息:', error.message);
    return false;
  }
}

// 主测试函数
async function runTests() {
  console.log(colors.yellow('🚀 开始测试RAG AI后端连接...'));
  console.log(colors.yellow(`📍 测试地址: ${RAG_API_BASE_URL}`));
  
  let passedTests = 0;
  let totalTests = 0;
  
  // 测试健康检查
  totalTests++;
  if (await testHealthCheck()) {
    passedTests++;
  }
  
  // 测试微信健康检查
  totalTests++;
  if (await testWechatHealthCheck()) {
    passedTests++;
  }
  
  // 测试向量数据库信息
  totalTests++;
  if (await testVectorstoreInfo()) {
    passedTests++;
  }
  
  // 测试查询接口
  for (const question of testQuestions) {
    totalTests++;
    if (await testQuery(question)) {
      passedTests++;
    }
    
    // 等待一秒避免请求过快
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  // 输出测试结果
  console.log(colors.yellow('\n📊 测试结果汇总:'));
  console.log(`总测试数: ${totalTests}`);
  console.log(`通过测试: ${colors.green(passedTests)}`);
  console.log(`失败测试: ${colors.red(totalTests - passedTests)}`);
  
  if (passedTests === totalTests) {
    console.log(colors.green('\n🎉 所有测试通过！RAG AI后端工作正常。'));
  } else {
    console.log(colors.red('\n⚠️ 部分测试失败，请检查RAG AI后端服务。'));
  }
  
  return passedTests === totalTests;
}

// 运行测试
if (require.main === module) {
  runTests().then(success => {
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error(colors.red('测试运行出错:'), error);
    process.exit(1);
  });
}

module.exports = {
  runTests,
  testHealthCheck,
  testWechatHealthCheck,
  testQuery,
  testVectorstoreInfo
};
