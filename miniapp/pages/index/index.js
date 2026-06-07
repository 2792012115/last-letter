Page({
  data: {
    rels: [],
    selectedRel: '',
    recipientName: '',
  },

  onShow() {
    const app = getApp();
    const rels = app.globalData.relationships;
    const arr = Object.entries(rels).map(([key, val]) => ({
      key,
      icon: val.icon,
      label: val.label,
    }));
    this.setData({ rels: arr, selectedRel: '', recipientName: '' });
  },

  selectRel(e) {
    this.setData({ selectedRel: e.currentTarget.dataset.key });
  },

  onNameInput(e) {
    this.setData({ recipientName: e.detail.value });
  },

  goNext() {
    const { selectedRel, recipientName, rels } = this.data;
    if (!selectedRel) {
      // 默认选第一个
      if (rels.length > 0) {
        this.setData({ selectedRel: rels[0].key });
        wx.showToast({ title: '已默认选择', icon: 'none', duration: 1000 });
        setTimeout(() => this.goNext(), 1000);
        return;
      }
      wx.showToast({ title: '请先选择收信对象', icon: 'none' });
      return;
    }

    const app = getApp();
    app.globalData.selectedRel = selectedRel;
    app.globalData.recipientName = recipientName || selectedRel;

    // 跳到提问页
    wx.navigateTo({ url: '/pages/questions/questions' });
  },
});
