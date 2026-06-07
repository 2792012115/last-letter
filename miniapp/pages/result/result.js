const app = getApp();

Page({
  data: {
    letter: '',
    keywords: [],
  },

  onLoad() {
    this.setData({
      letter: app.globalData.letter || '',
      keywords: app.globalData.keywords || [],
    });
  },

  goHome() {
    wx.navigateBack({ delta: 2 });
  },

  shareLetter() {
    const letter = this.data.letter;
    const watermark = '\n\n— 来自「如果明天不在了」';
    wx.setClipboardData({
      data: letter + watermark,
      success() {
        wx.showToast({ title: '已复制！去分享吧 💌', icon: 'none', duration: 2000 });
      },
      fail() {
        wx.showToast({ title: '复制失败，请手动选择', icon: 'none' });
      }
    });
  },

  // 转发给好友
  onShareAppMessage() {
    return {
      title: '一封来自「如果明天不在了」的信 💌',
      path: '/pages/index/index',
      imageUrl: '', // 可以放分享图
    };
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: '如果明天不在了，你想对谁说些什么？',
    };
  },
});
