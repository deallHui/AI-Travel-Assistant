import React from 'react'
import { Card, Button, Space, Typography, Row, Col, Tag } from 'antd'
import {
  EnvironmentOutlined,
  CarOutlined,
  ShopOutlined,
  CameraOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  TeamOutlined,
  CalendarOutlined
} from '@ant-design/icons'

const { Title, Text } = Typography

const TravelQuestions = ({ onQuestionClick }) => {
  // 旅游问题分类
  const questionCategories = [
    {
      title: '🏛️ 景点推荐',
      icon: <EnvironmentOutlined />,
      color: '#52c41a',
      questions: [
        '北京有哪些必去的景点？',
        '上海外滩附近有什么好玩的？',
        '西安的历史文化景点推荐',
        '三亚有哪些海滩值得去？',
        '成都周边的自然风光景点'
      ]
    },
    {
      title: '🍜 美食攻略',
      icon: <ShopOutlined />,
      color: '#fa8c16',
      questions: [
        '北京烤鸭哪家最正宗？',
        '上海小笼包推荐店铺',
        '西安有哪些特色小吃？',
        '广州早茶去哪里吃？',
        '重庆火锅店推荐'
      ]
    },
    {
      title: '🚗 交通出行',
      icon: <CarOutlined />,
      color: '#1890ff',
      questions: [
        '从机场到市区怎么走最方便？',
        '北京地铁一日游路线规划',
        '上海公交卡怎么办理？',
        '杭州西湖周边交通攻略',
        '自驾游需要注意什么？'
      ]
    },
    {
      title: '🏨 住宿建议',
      icon: <TeamOutlined />,
      color: '#722ed1',
      questions: [
        '北京住哪个区域比较方便？',
        '上海性价比高的酒店推荐',
        '青年旅社和民宿怎么选？',
        '旅游旺季如何订到好酒店？',
        '亲子游住宿有什么要求？'
      ]
    },
    {
      title: '💰 预算规划',
      icon: <DollarOutlined />,
      color: '#eb2f96',
      questions: [
        '北京三日游大概需要多少钱？',
        '学生党穷游攻略推荐',
        '蜜月旅行预算怎么规划？',
        '带老人旅游费用预算',
        '如何在旅游中省钱？'
      ]
    },
    {
      title: '📅 行程安排',
      icon: <CalendarOutlined />,
      color: '#13c2c2',
      questions: [
        '北京五日游经典路线',
        '上海周末两日游安排',
        '西安三日游最佳行程',
        '云南十日游路线规划',
        '春节期间适合去哪里？'
      ]
    }
  ]

  return (
    <div style={{ padding: '16px' }}>
      <Title level={4} style={{ textAlign: 'center', marginBottom: '24px' }}>
        🌟 热门旅游问题推荐
      </Title>
      
      <Row gutter={[16, 16]}>
        {questionCategories.map((category, index) => (
          <Col span={12} key={index}>
            <Card
              size="small"
              title={
                <Space>
                  <span style={{ color: category.color }}>{category.icon}</span>
                  <Text strong>{category.title}</Text>
                </Space>
              }
              style={{ height: '280px' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                {category.questions.map((question, qIndex) => (
                  <Button
                    key={qIndex}
                    type="text"
                    size="small"
                    style={{ 
                      textAlign: 'left', 
                      height: 'auto',
                      padding: '4px 8px',
                      whiteSpace: 'normal',
                      wordBreak: 'break-all'
                    }}
                    onClick={() => onQuestionClick(question)}
                  >
                    <Text style={{ fontSize: '12px' }}>
                      {question}
                    </Text>
                  </Button>
                ))}
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Card style={{ marginTop: '16px', textAlign: 'center' }}>
        <Space wrap>
          <Tag color="blue" icon={<ClockCircleOutlined />}>
            实时更新
          </Tag>
          <Tag color="green" icon={<CameraOutlined />}>
            图文并茂
          </Tag>
          <Tag color="orange" icon={<TeamOutlined />}>
            用户推荐
          </Tag>
          <Tag color="purple" icon={<DollarOutlined />}>
            省钱攻略
          </Tag>
        </Space>
        <div style={{ marginTop: '8px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            💡 点击上方问题快速开始对话，或直接输入您的旅游问题
          </Text>
        </div>
      </Card>
    </div>
  )
}

export default TravelQuestions
