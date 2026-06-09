const app = getApp();

Page({
  data: {
    icon: '',
    label: '',
    recipientName: '',
    questions: [],
    answers: [],
    submitting: false,
  },

  onLoad() {
    const rel = app.globalData.selectedRel;
    const rels = app.globalData.relationships;
    const preset = rels[rel] || { icon: '✉️', label: rel };

    this.setData({
      icon: preset.icon,
      label: preset.label,
      recipientName: app.globalData.recipientName,
    });

    // 从后端加载问题
    wx.request({
      url: app.globalData.apiBase + '/api/questions',
      method: 'POST',
      data: { relationship: rel },
      success: (res) => {
        if (res.data && res.data.questions) {
          this.setData({ questions: res.data.questions });
        }
      },
      fail: () => {
        // 离线兜底
        const defaults = {
          "妈妈": ["你記憶中，媽媽為你做過最讓你鼻子一酸的小事是什麼？","如果只能讓她記住你的一句話，那會是什麼？","你覺得她這輩子最大的遺憾是什麼——和你有關嗎？","你現在做著什麼事的時候，會突然想起她？"],
          "爸爸": ["你有沒有一直想問他、但從來沒敢開口的一件事？","他教會你的最重要的一個道理是什麼？","你覺得他年輕時候的夢想是什麼，實現了嗎？","如果明天不在了，你最想替他做完哪件事？"],
          "前任": ["分開後你才終於明白的一件事是什麼？","你們之間最好的一天，那天發生了什麼？","如果重來一次，你會在什麼時候做出不同的選擇？","你現在還留著TA的什麼東西？為什麼留著？"],
          "最好的朋友": ["TA幫你扛過的最大的事是什麼？","你們之間只屬於彼此的那個梗是什麼？","如果TA明天不在了，你最遺憾沒一起做的事是什麼？","你想替TA對TA的另一半/家人說一句什麼？"],
          "18岁的自己": ["18歲的你最害怕的事情是什麼？現在想告訴TA：別怕。為什麼？","當年你以為天塌下來的那件事，現在還記得嗎？","你最想讓18歲的自己提前知道的道理是什麼？","現在的你有沒有活成18歲時期待的樣子？"],
          "自定义": ["這個人和你之間最難忘的一個畫面是什麼？","有什麼話你攢了很久但從來沒說出口？","如果這是最後一次對話，你最想讓TA明白什麼？","你希望TA讀完這封信之後，第一反應是什麼？"],
        };
        this.setData({ questions: defaults[rel] || defaults["自定义"] });
      }
    });
  },

  onAnswerInput(e) {
    const idx = e.currentTarget.dataset.index;
    const val = e.detail.value;
    const answers = [...this.data.answers];
    answers[idx] = val;
    this.setData({ answers });
  },

  submitAnswers() {
    // 补全空回答
    const answers = this.data.questions.map((_, i) =>
      this.data.answers[i] || '（这个问题我暂时不知道怎么回答）'
    );

    this.setData({ submitting: true });

    app.globalData.questions = this.data.questions;
    app.globalData.answers = answers;

    wx.request({
      url: app.globalData.apiBase + '/api/generate',
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: {
        relationship: app.globalData.selectedRel,
        recipient_name: app.globalData.recipientName,
        questions: this.data.questions,
        answers: answers,
      },
      success: (res) => {
        this.setData({ submitting: false });
        if (res.data && res.data.letter) {
          app.globalData.letter = res.data.letter;
          app.globalData.keywords = res.data.keywords || [];
          wx.navigateTo({ url: '/pages/result/result' });
        } else {
          wx.showToast({ title: '生成失败，请重试', icon: 'none' });
        }
      },
      fail: (err) => {
        this.setData({ submitting: false });
        wx.showToast({ title: '网络错误：' + (err.errMsg || ''), icon: 'none' });
      }
    });
  },
});
