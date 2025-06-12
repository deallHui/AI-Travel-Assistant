// 测试新的云函数RAG AI集成
const axios = require('axios');

// 模拟云函数环境
const mockEvent = {
  question: "推荐一些北京的必去景点",
  location: {
    latitude: 39.9042,
    longitude: 116.4074,
    city: "北京"
  }
};

const mockContext = {};

// 模拟微信云函数SDK
const mockCloud = {
  init: () => {},
  getWXContext: () => ({
    OPENID: 'test_openid_123'
  })
};

// 配置
const config = {
  development: {
    ragApiBaseUrl: 'http://localhost:8000',
    timeout: 30000
  }
};

const apiConfig = config.development;

async function testCloudFunction() {
  console.log('🧪 测试新的云函数RAG AI集成...\n');

  try {
    // 1. 测试健康检查
    console.log('1️⃣ 测试健康检查...');
    const healthResponse = await axios.get(`${apiConfig.ragApiBaseUrl}/wechat/health`, {
      timeout: 10000
    });
    console.log('✅ 健康检查通过:', healthResponse.data);
    console.log('');

    // 2. 测试RAG查询
    console.log('2️⃣ 测试RAG查询...');
    const requestData = {
      question: mockEvent.question,
      openid: 'test_openid_123',
      location: mockEvent.location,
      top_k: 3
    };

    console.log('发送请求:', requestData);
    
    const response = await axios.post(`${apiConfig.ragApiBaseUrl}/wechat/query`, requestData, {
      timeout: apiConfig.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('✅ RAG查询成功!');
    console.log('响应数据:', JSON.stringify(response.data, null, 2));

    // 3. 模拟云函数返回格式
    const cloudFunctionResult = {
      success: response.data.success,
      message: response.data.message,
      data: response.data.data,
      openid: 'test_openid_123',
      timestamp: new Date().toISOString()
    };

    console.log('\n📱 云函数返回格式:');
    console.log(JSON.stringify(cloudFunctionResult, null, 2));

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 解决方案:');
      console.log('1. 确保RAG AI后端服务正在运行');
      console.log('2. 检查服务地址: http://localhost:8000');
      console.log('3. 运行命令: cd rag_ai && python start_backend.py');
    }
  }
}

// 运行测试
testCloudFunction();
