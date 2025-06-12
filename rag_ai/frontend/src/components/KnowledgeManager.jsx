import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  Modal,
  Form,
  Upload,
  message,
  Statistic,
  Row,
  Col,
  Typography,
  Divider,
  Spin
} from 'antd'
import {
  SearchOutlined,
  UploadOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  ReloadOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  EnvironmentOutlined,
  CompassOutlined,
  CarOutlined,
  CameraOutlined
} from '@ant-design/icons'
import axios from 'axios'

const { Search } = Input
const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

const API_BASE_URL = 'http://localhost:8000'

const KnowledgeManager = () => {
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)
  const [systemInfo, setSystemInfo] = useState(null)
  const [modelsInfo, setModelsInfo] = useState(null)
  const [uploadModalVisible, setUploadModalVisible] = useState(false)
  const [searchModalVisible, setSearchModalVisible] = useState(false)
  const [form] = Form.useForm()

  // 获取系统信息
  const fetchSystemInfo = async () => {
    setLoading(true)
    try {
      const [healthResponse, vectorstoreResponse, modelsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/health`),
        axios.get(`${API_BASE_URL}/vectorstore/info`),
        axios.get(`${API_BASE_URL}/models/info`)
      ])
      
      setSystemInfo({
        health: healthResponse.data,
        vectorstore: vectorstoreResponse.data
      })
      setModelsInfo(modelsResponse.data)
    } catch (error) {
      console.error('获取系统信息失败:', error)
      message.error('获取系统信息失败')
    } finally {
      setLoading(false)
    }
  }

  // 搜索知识库
  const handleSearch = async (query) => {
    if (!query.trim()) return
    
    setSearchLoading(true)
    try {
      const response = await axios.post(`${API_BASE_URL}/vectorstore/search`, {
        question: query,
        top_k: 10
      })
      
      setSearchResults(response.data.results)
      setSearchModalVisible(true)
    } catch (error) {
      console.error('搜索失败:', error)
      message.error('搜索失败')
    } finally {
      setSearchLoading(false)
    }
  }

  // 文件上传处理
  const handleUpload = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      // 这里需要后端支持文件上传API
      message.info('文件上传功能需要后端API支持')
      return false // 阻止默认上传行为
    } catch (error) {
      console.error('上传失败:', error)
      message.error('上传失败')
      return false
    }
  }

  useEffect(() => {
    fetchSystemInfo()
  }, [])

  // 搜索结果表格列定义
  const searchColumns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      render: (rank) => <Tag color="blue">#{rank}</Tag>
    },
    {
      title: '内容预览',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content) => (
        <div style={{ maxHeight: '100px', overflow: 'hidden' }}>
          <Text>{content.substring(0, 200)}...</Text>
        </div>
      )
    },
    {
      title: '相似度',
      dataIndex: 'similarity_score',
      key: 'similarity_score',
      width: 100,
      render: (score) => (
        <Tag color={score > 0.7 ? 'green' : score > 0.5 ? 'orange' : 'red'}>
          {(score * 100).toFixed(1)}%
        </Tag>
      )
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <EnvironmentOutlined /> 旅游攻略管理
      </Title>
      
      {/* 系统状态概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="攻略总数"
              value={systemInfo?.vectorstore?.document_count || 0}
              prefix={<EnvironmentOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="系统状态"
              value={systemInfo?.health?.status === 'healthy' ? '正常' : '异常'}
              valueStyle={{ 
                color: systemInfo?.health?.status === 'healthy' ? '#3f8600' : '#cf1322' 
              }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="嵌入模型"
              value={systemInfo?.vectorstore?.embedding_model || 'N/A'}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="LLM模型"
              value={systemInfo?.vectorstore?.llm_model || 'N/A'}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={12}>
          <Card title="🔍 攻略搜索" extra={<CompassOutlined />}>
            <Search
              placeholder="搜索景点、美食、住宿、交通等攻略内容..."
              enterButton="搜索攻略"
              size="large"
              loading={searchLoading}
              onSearch={handleSearch}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="📋 快速操作" extra={<CarOutlined />}>
            <Space wrap>
              <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={() => setUploadModalVisible(true)}
              >
                上传攻略
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchSystemInfo}
                loading={loading}
              >
                刷新状态
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => message.info('导出功能开发中...')}
              >
                导出攻略
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 模型信息 */}
      {modelsInfo && (
        <Card title="模型配置信息" style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Card size="small" title="LLM模型">
                <Paragraph>
                  <Text strong>名称:</Text> {modelsInfo.llm?.name}<br />
                  <Text strong>提供商:</Text> {modelsInfo.llm?.provider}<br />
                  <Text strong>模型ID:</Text> {modelsInfo.llm?.model_id}<br />
                  <Text strong>状态:</Text> 
                  <Tag color={modelsInfo.llm?.status === 'active' ? 'green' : 'red'}>
                    {modelsInfo.llm?.status}
                  </Tag>
                </Paragraph>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="🤖 嵌入模型">
                <Paragraph>
                  <Text strong>名称:</Text> {modelsInfo.embedding?.name}<br />
                  <Text strong>提供商:</Text> {modelsInfo.embedding?.provider}<br />
                  <Text strong>模型ID:</Text> {modelsInfo.embedding?.model_id}<br />
                  <Text strong>状态:</Text>
                  <Tag color={modelsInfo.embedding?.status === 'active' ? 'green' : 'red'}>
                    {modelsInfo.embedding?.status}
                  </Tag>
                </Paragraph>
                <div style={{ marginTop: '8px' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    💡 如需切换模型提升速度，请运行：<br />
                    <code>python switch_embedding.py quick</code>
                  </Text>
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="向量数据库">
                <Paragraph>
                  <Text strong>名称:</Text> {modelsInfo.vectorstore?.name}<br />
                  <Text strong>类型:</Text> {modelsInfo.vectorstore?.type}<br />
                  <Text strong>状态:</Text> 
                  <Tag color={modelsInfo.vectorstore?.status === 'active' ? 'green' : 'red'}>
                    {modelsInfo.vectorstore?.status}
                  </Tag>
                </Paragraph>
              </Card>
            </Col>
          </Row>
        </Card>
      )}

      {/* 上传文档模态框 */}
      <Modal
        title="上传文档到知识库"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="file"
            label="选择文档文件"
            rules={[{ required: true, message: '请选择要上传的文件' }]}
          >
            <Upload
              beforeUpload={handleUpload}
              maxCount={1}
              accept=".txt,.md,.pdf,.doc,.docx"
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
          </Form.Item>
          
          <Form.Item name="title" label="文档标题">
            <Input placeholder="输入文档标题（可选）" />
          </Form.Item>
          
          <Form.Item name="category" label="文档分类">
            <Input placeholder="输入文档分类（可选）" />
          </Form.Item>
          
          <Form.Item name="description" label="文档描述">
            <TextArea 
              rows={3} 
              placeholder="输入文档描述（可选）" 
            />
          </Form.Item>
        </Form>
        
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <Space>
            <Button onClick={() => setUploadModalVisible(false)}>
              取消
            </Button>
            <Button type="primary" onClick={() => message.info('上传功能开发中...')}>
              上传
            </Button>
          </Space>
        </div>
      </Modal>

      {/* 搜索结果模态框 */}
      <Modal
        title={`搜索结果 (共 ${searchResults.length} 条)`}
        open={searchModalVisible}
        onCancel={() => setSearchModalVisible(false)}
        width={800}
        footer={null}
      >
        <Table
          columns={searchColumns}
          dataSource={searchResults}
          rowKey="rank"
          pagination={{ pageSize: 5 }}
          size="small"
        />
      </Modal>
    </div>
  )
}

export default KnowledgeManager
