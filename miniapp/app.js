App({
  globalData: {
    // API 后端地址
    apiBase: 'https://web-production-71583a.up.railway.app',
    relationships: {},
    selectedRel: null,
    recipientName: '',
    questions: [],
    answers: [],
  },

  onLaunch() {
    // 加载关系预设
    this.loadRelationships();
  },

  loadRelationships() {
    const that = this;
    wx.request({
      url: this.globalData.apiBase + '/api/relationships',
      success(res) {
        if (res.data) {
          that.globalData.relationships = res.data;
        }
      },
      fail() {
        // 离线兜底
        that.globalData.relationships = {
          "妈妈": {"icon":"👩","label":"给妈妈"},
          "爸爸": {"icon":"👨","label":"给爸爸"},
          "前任": {"icon":"💔","label":"给前任"},
          "最好的朋友": {"icon":"🤝","label":"给最好的朋友"},
          "18岁的自己": {"icon":"🕰️","label":"给18岁的自己"},
          "自定义": {"icon":"✉️","label":"给想说话的人"}
        };
      }
    });
  }
});
