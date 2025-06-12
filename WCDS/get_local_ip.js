// 获取本机IP地址的脚本
const os = require('os');

function getLocalIPAddress() {
    const interfaces = os.networkInterfaces();
    const addresses = [];
    
    for (const name of Object.keys(interfaces)) {
        for (const interface of interfaces[name]) {
            // 跳过内部地址和IPv6地址
            if (interface.family === 'IPv4' && !interface.internal) {
                addresses.push({
                    name: name,
                    address: interface.address
                });
            }
        }
    }
    
    return addresses;
}

console.log('🔍 检测到的本机IP地址:');
const addresses = getLocalIPAddress();

if (addresses.length === 0) {
    console.log('❌ 未找到可用的IP地址');
    console.log('💡 建议使用 localhost:8000 或检查网络连接');
} else {
    addresses.forEach((addr, index) => {
        console.log(`${index + 1}. ${addr.name}: ${addr.address}`);
        console.log(`   测试地址: http://${addr.address}:8000`);
    });
    
    console.log('\n📋 推荐配置:');
    console.log(`ragApiBaseUrl: 'http://${addresses[0].address}:8000'`);
}

console.log('\n🔧 如何更新云函数配置:');
console.log('1. 复制上面推荐的IP地址');
console.log('2. 编辑 cloudfunctions/getQASystem/index.js');
console.log('3. 更新 ragApiBaseUrl 配置');
console.log('4. 重新部署云函数');
