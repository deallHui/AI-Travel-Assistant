Page({
  data: {
    chatMode: "bot", // bot 表示使用agent，model 表示使用大模型
    showBotAvatar: true,
    agentConfig: {
      botId: "bot-048e77d6", // 你的agent id
      allowWebSearch: true,
      allowUploadFile: true,
      allowPullRefresh: true,
      allowUploadImage: true,
      showToolCallDetail: true,
      allowMultiConversation: true,
      allowVoice: true
    },
    modelConfig: {
      modelProvider: "deepseek",
      quickResponseModel: "deepseek-v3",
      logo: "",
      welcomeMsg: "欢迎语"
    },
    envShareConfig: {}
  },
  onLoad() {
    // 初始化AI对话相关逻辑
  }
}) 