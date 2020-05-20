//index.js
//获取应用实例
const app = getApp()

Page({
  data: {
    motto: 'Hello World',
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    newlist: [],
    data11:[],
    hao11:[]
  },
  //事件处理函数
  // bindViewTap: function() {
  //   wx.navigateTo({
  //     url: '../logs/logs'
  //   })
  // },
  gotoEventPage:function(e){
    let index=e.currentTarget.dataset.index;
    let item=e.currentTarget.dataset.item;
    let id = e.currentTarget.dataset.id;
    let hao = e.currentTarget.dataset.hao;



    var index1 = parseInt(index) + 1 ;
    var that = this;

  



    wx.request({
      url: 'http://47.108.65.135:5100/keshe/api/v1/event/data',//请求地址
      data: {
        event_index:index1  
      },
      header: {
        "Content-Type": "applciation/x-www-form-urlencoded"
      },
      method: 'GET',
      success: function (res) {

        console.log(res)


        // that.setData({
        //   feature_data: JSON.parse(res.data.featureset).data,
        //   feature_index: JSON.parse(res.data.featureset).index,
        // })


        var data_11 = [];
        var data_22 = [];
        var data_33 = [];
        var data_44 = [];
        for (var i = 0; i < JSON.parse(res.data.dataset).index.length; i++) {
          data_11.push(
            [
              i,
              JSON.parse(res.data.dataset).data[i][0],

            ]
          );

          data_22.push(
            [
              i,
              JSON.parse(res.data.dataset).data[i][1],

            ]
          );

          data_33.push(
            [
              i,
              JSON.parse(res.data.dataset).data[i][2],

            ]
          );

          data_44.push(
            [
              i,
              JSON.parse(res.data.dataset).data[i][3],

            ]
          );



        }



        // var datamin = 1000000000;
        // var datamax = 0;
        // for (var i = 0; i < 100; i++) {
        //   if (JSON.parse(res.data.featureset).data[i] > datamax) {
        //     datamax = JSON.parse(res.data.featureset).data[i]
        //   }
        //   if (JSON.parse(res.data.featureset).data[i] < datamin) {
        //     datamin = JSON.parse(res.data.featureset).data[i]
        //   }

        // }
        // // console.log(datamax)
        // that.setData({

        //   featuremin: datamin,
        //   featuremax: datamax
        // })


        // console.log(data_11);
        // that.setData({

        //   data_1: data_11,
        // })

        app.globalData.data_1 = data_11;
        app.globalData.data_2 = data_22;
        app.globalData.data_3 = data_33;
        // app.globalData.data_4 = data_44;

        //  console.log(this.data.data_1);
      },

      fail: function (res) {

      },
      complete: function () { }
    })

    setTimeout(function(){
      wx.navigateTo({
        url: '../Event/Event?index=' + index + "&time=" + item + "&type=" + id + "&hao=" + hao,
        success: function (res) {

        },
        fail: function (res) {

        },
        complete: function (res) {

        },
      })


    },1000)
    // wx.navigateTo({
    //   url: '../Event/Event?index=' + index + "&time=" + item + "&type=" + id+"&hao=" + hao,
    //   success: function (res) {

    //   },
    //   fail: function (res) {

    //   },
    //   complete: function (res) {

    //   },
    // })

  },
  onLoad: function () {
    var that = this;

  



    wx.request({
      url: 'http://47.108.65.135:5100/keshe/api/v1/main/event',//获取数据
      data: {
        event_index: '1'
      },
      header: {
        "Content-Type": "applciation/x-www-form-urlencoded"
      },
      method: 'GET',
      success: function (res) {
        // console.log(JSON.parse(res.data.data).data[0][2]);
        that.setData({
          newlist: JSON.parse(res.data.data).index,
          data11: JSON.parse(res.data.data).data
        })
        // app.globalData.data_1 = [[5, 8], [6, 10], [7, 7]];

      },

      fail: function (res) {

      },
      complete: function () { }
    })



    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      })
    } else if (this.data.canIUse){
      // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
      // 所以此处加入 callback 以防止这种情况
      app.userInfoReadyCallback = res => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
      }
    } else {
      // 在没有 open-type=getUserInfo 版本的兼容处理
      wx.getUserInfo({
        success: res => {
          app.globalData.userInfo = res.userInfo
          this.setData({
            userInfo: res.userInfo,
            hasUserInfo: true
          })
        }
      })
    }
  },
  getUserInfo: function(e) {
    console.log(e)
    app.globalData.userInfo = e.detail.userInfo
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
  }
})
