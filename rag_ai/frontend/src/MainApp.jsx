import React, { useState } from 'react'
import { 
  Layout, 
  Menu, 
  Typography, 
  Space,
  Breadcrumb,
  Button,
  Dropdown
} from 'antd'
import {
  MessageOutlined,
  DatabaseOutlined,
  HomeOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  CompassOutlined,
  EnvironmentOutlined
} from '@ant-design/icons'
import App from './App'
import KnowledgeManager from './components/KnowledgeManager'
import './index.css'

const { Header, Content, Sider } = Layout
const { Title } = Typography

const MainApp = () => {
  const [selectedKey, setSelectedKey] = useState('chat')
  const [collapsed, setCollapsed] = useState(false)

  // 菜单项配置
  const menuItems = [
    {
      key: 'chat',
      icon: <CompassOutlined />,
      label: '旅游问答',
      component: <App />
    },
    {
      key: 'knowledge',
      icon: <EnvironmentOutlined />,
      label: '攻略管理',
      component: <KnowledgeManager />
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
      component: (
        <div style={{ padding: '24px', textAlign: 'center' }}>
          <Title level={3}>系统设置</Title>
          <p>系统设置功能开发中...</p>
        </div>
      )
    }
  ]

  // 获取当前选中的组件
  const getCurrentComponent = () => {
    const currentItem = menuItems.find(item => item.key === selectedKey)
    return currentItem ? currentItem.component : <App />
  }

  // 获取当前页面标题
  const getCurrentTitle = () => {
    const currentItem = menuItems.find(item => item.key === selectedKey)
    return currentItem ? currentItem.label : '智能问答'
  }

  // 用户菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录'
    }
  ]

  const handleUserMenuClick = ({ key }) => {
    if (key === 'logout') {
      // 处理退出登录
      console.log('退出登录')
    } else if (key === 'profile') {
      // 处理个人资料
      console.log('个人资料')
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          background: '#fff',
          boxShadow: '2px 0 8px rgba(0,0,0,0.1)'
        }}
      >
        {/* Logo区域 */}
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0'
        }}>
          {collapsed ? (
            <CompassOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
          ) : (
            <Space>
              <CompassOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
              <Title level={4} style={{ margin: 0, color: '#52c41a' }}>
                智游助手
              </Title>
            </Space>
          )}
        </div>

        {/* 导航菜单 */}
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          style={{ borderRight: 0, marginTop: '16px' }}
          onClick={({ key }) => setSelectedKey(key)}
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label
          }))}
        />
      </Sider>

      {/* 主内容区域 */}
      <Layout>
        {/* 顶部导航栏 */}
        <Header style={{ 
          background: '#fff', 
          padding: '0 24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Space>
            {/* 折叠按钮 */}
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: '16px' }}
            />

            {/* 面包屑导航 */}
            <Breadcrumb
              items={[
                {
                  href: '',
                  title: <HomeOutlined />
                },
                {
                  title: getCurrentTitle()
                }
              ]}
            />
          </Space>

          {/* 用户信息 */}
          <Space>
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleUserMenuClick
              }}
              placement="bottomRight"
            >
              <Button type="text" style={{ height: 'auto' }}>
                <Space>
                  <UserOutlined />
                  <span>管理员</span>
                </Space>
              </Button>
            </Dropdown>
          </Space>
        </Header>

        {/* 内容区域 */}
        <Content style={{ 
          margin: 0,
          background: '#f5f5f5',
          overflow: 'auto'
        }}>
          {getCurrentComponent()}
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainApp
