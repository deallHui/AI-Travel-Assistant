import React, { useState, useRef, useEffect } from 'react'
import { 
  Layout, 
  Input, 
  Button, 
  Card, 
  Typography, 
  Space, 
  Spin, 
  Alert,
  Tag,
  Divider,
  Row,
  Col,
  Statistic
} from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  CompassOutlined,
  QuestionCircleOutlined,
  EnvironmentOutlined,
  CarOutlined,
  CameraOutlined
} from '@ant-design/icons'
import axios from 'axios'
import TravelQuestions from './components/TravelQuestions'
import './index.css'

const { Header, Content } = Layout
const { TextArea } = Input
const { Title, Paragraph, Text } = Typography

// API配置
const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [systemInfo, setSystemInfo] = useState(null)
  const messagesEndRef = useRef(null)

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 获取系统信息
  useEffect(() => {
    fetchSystemInfo()
  }, [])

  const fetchSystemInfo = async () => {
    try {
      const [healthResponse, vectorstoreResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/health`),
        axios.get(`${API_BASE_URL}/vectorstore/info`)
      ])
      
      setSystemInfo({
        health: healthResponse.data,
        vectorstore: vectorstoreResponse.data
      })
    } catch (error) {
      console.error('获取系统信息失败:', error)
    }
  }

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        question: inputValue,
        top_k: 3
      })

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        confidence: response.data.confidence,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('查询失败:', error)

      let errorContent = '抱歉，查询失败。'

      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        errorContent = '❌ 网络连接失败，请检查后端服务是否启动 (http://localhost:8000)'
      } else if (error.response) {
        // 服务器返回错误
        errorContent = `❌ 服务器错误 (${error.response.status}): ${error.response.data?.detail || '未知错误'}`
      } else if (error.request) {
        // 请求发出但没有收到响应
        errorContent = '❌ 无法连接到后端服务，请确认后端是否在 http://localhost:8000 运行'
      } else {
        // 其他错误
        errorContent = `❌ 请求失败: ${error.message}`
      }

      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: errorContent,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  // 处理回车发送
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 清空对话
  const handleClearMessages = () => {
    setMessages([])
  }

  // 处理推荐问题点击
  const handleQuestionClick = (question) => {
    setInputValue(question)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#fff', 
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <CompassOutlined style={{ fontSize: '24px', color: '#52c41a', marginRight: '12px' }} />
          <Title level={3} style={{ margin: 0, color: '#52c41a' }}>
            智能旅游攻略问答系统
          </Title>
        </div>
        
        {systemInfo && (
          <Space>
            <Statistic
              title="攻略数量"
              value={systemInfo.vectorstore?.document_count || 0}
              prefix={<EnvironmentOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
            <Tag color={systemInfo.health?.status === 'healthy' ? 'green' : 'red'}>
              {systemInfo.health?.status === 'healthy' ? '系统正常' : '系统异常'}
            </Tag>
          </Space>
        )}
      </Header>

      <Content style={{ padding: '24px' }}>
        <div className="chat-container">
          <Row gutter={24}>
            <Col span={18}>
              <Card 
                title={
                  <Space>
                    <CompassOutlined />
                    旅游问答对话
                    <Button size="small" onClick={handleClearMessages}>
                      清空对话
                    </Button>
                  </Space>
                }
                style={{ height: '600px' }}
              >
                <div className="message-list" style={{ height: '480px' }}>
                  {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#999', marginTop: '20px' }}>
                      <CompassOutlined style={{ fontSize: '48px', marginBottom: '16px', color: '#52c41a' }} />
                      <Paragraph>
                        🌟 欢迎使用智能旅游攻略问答系统！<br />
                        🗺️ 我是您的专属旅游助手，可以为您提供：<br />
                        📍 景点推荐 🏨 住宿建议 🍜 美食攻略 🚗 交通指南
                      </Paragraph>
                      <TravelQuestions onQuestionClick={handleQuestionClick} />
                    </div>
                  ) : (
                    messages.map((message) => (
                      <div key={message.id} className="message-item">
                        <Card 
                          size="small"
                          style={{
                            backgroundColor: message.type === 'user' ? '#e6f7ff' : 
                                           message.type === 'error' ? '#fff2f0' : '#f6ffed'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                            {message.type === 'user' ? (
                              <UserOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                            ) : (
                              <RobotOutlined style={{ marginRight: '8px', color: '#52c41a' }} />
                            )}
                            <div style={{ flex: 1 }}>
                              <div className="message-content">
                                <div style={{ whiteSpace: 'pre-wrap' }}>
                                  {message.content}
                                </div>
                              </div>

                              {message.sources && message.sources.length > 0 && (
                                <div className="message-sources">
                                  <Divider style={{ margin: '8px 0' }} />
                                  <Text type="secondary" style={{ fontSize: '12px' }}>
                                    📚 参考来源：
                                  </Text>
                                  <div style={{ marginTop: '4px' }}>
                                    {message.sources.map((source, index) => {
                                      // 根据来源类型设置不同的颜色和图标
                                      let color = 'blue';
                                      let icon = '📄';

                                      if (source.includes('DeepSeek') || source.includes('网络搜索')) {
                                        color = 'green';
                                        icon = '🤖';
                                      } else if (source.includes('知识库')) {
                                        color = 'blue';
                                        icon = '📚';
                                      }

                                      return (
                                        <Tag key={index} color={color} size="small" style={{ marginBottom: '2px' }}>
                                          {icon} {source}
                                        </Tag>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}

                              {message.confidence && (
                                <div style={{ marginTop: '8px' }}>
                                  <Text type="secondary" style={{ fontSize: '11px' }}>
                                    🎯 置信度: {(message.confidence * 100).toFixed(0)}%
                                  </Text>
                                </div>
                              )}
                              
                              <div style={{ textAlign: 'right', marginTop: '8px' }}>
                                <Text type="secondary" style={{ fontSize: '11px' }}>
                                  {message.timestamp.toLocaleTimeString()}
                                </Text>
                              </div>
                            </div>
                          </div>
                        </Card>
                      </div>
                    ))
                  )}
                  
                  {loading && (
                    <div className="loading-indicator">
                      <Spin size="large" />
                      <Paragraph style={{ marginTop: '16px', color: '#666' }}>
                        正在思考中...
                      </Paragraph>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
              </Card>

              <Card style={{ marginTop: '16px' }} title="🗣️ 向旅游助手提问">
                <Space.Compact style={{ width: '100%' }}>
                  <TextArea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="例如：北京有哪些必去景点？上海的美食推荐？三亚旅游攻略..."
                    autoSize={{ minRows: 2, maxRows: 4 }}
                    disabled={loading}
                  />
                  <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={handleSendMessage}
                    loading={loading}
                    disabled={!inputValue.trim()}
                    style={{ height: 'auto' }}
                  >
                    发送
                  </Button>
                </Space.Compact>
              </Card>
            </Col>

            <Col span={6}>
              <Card title="🚀 系统状态" style={{ marginBottom: '16px' }}>
                {systemInfo ? (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Statistic
                      title="系统状态"
                      value={systemInfo.health?.status === 'healthy' ? '正常运行' : '异常'}
                      valueStyle={{
                        color: systemInfo.health?.status === 'healthy' ? '#3f8600' : '#cf1322'
                      }}
                    />
                    <Statistic
                      title="旅游攻略"
                      value={systemInfo.vectorstore?.document_count || 0}
                      suffix="篇"
                    />
                    <Statistic
                      title="攻略库状态"
                      value={systemInfo.health?.vectorstore_initialized ? '已就绪' : '未加载'}
                      valueStyle={{
                        color: systemInfo.health?.vectorstore_initialized ? '#3f8600' : '#cf1322'
                      }}
                    />
                  </Space>
                ) : (
                  <Spin />
                )}
              </Card>

              <Card title="🧭 使用指南">
                <Paragraph style={{ fontSize: '14px' }}>
                  <Text strong>🎯 我能帮您：</Text><br />
                  🏛️ 推荐热门景点和路线<br />
                  🏨 提供住宿和餐饮建议<br />
                  🚗 规划交通和出行方案<br />
                  💰 分享省钱和实用攻略<br />
                  🤖 AI智能搜索补充信息<br />
                  <br />
                  <Text strong>💡 提问技巧：</Text><br />
                  📍 说明具体的城市或地区<br />
                  🗓️ 提及旅行时间和预算<br />
                  👥 告诉我同行人数和偏好<br />
                  🔄 支持多轮深入咨询<br />
                  <br />
                  <Text strong>🚀 智能增强：</Text><br />
                  📚 优先搜索本地知识库<br />
                  🤖 自动启用AI网络搜索<br />
                  🎯 提供置信度参考<br />
                  📊 显示信息来源标识<br />
                </Paragraph>
              </Card>
            </Col>
          </Row>
        </div>
      </Content>
    </Layout>
  )
}

export default App
