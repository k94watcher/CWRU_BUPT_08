// pages/机组/jizu.js
const app = getApp()
Page({
  data: {
    newlist:[],
    data11:[],

  },
  //事件处理函数
  // bindViewTap: function() {
  //   wx.navigateTo({
  //     url: '../logs/logs'
  //   })
  // },
  gotoEventPage: function (e) {
    let index = e.currentTarget.dataset.index;
    let id = e.currentTarget.dataset.id;
    let hao = e.currentTarget.dataset.hao;
    // console.log(hao)


    var index1 = parseInt(index) + 1;
    console.log(typeof index)
    wx.request({
      url: 'http://47.108.65.135:5100/keshe/api/v1/machine/data',//请求地址
      data: {
        machine_seq: hao
      },
      header: {
        "Content-Type": "applciation/x-www-form-urlencoded"
      },
      method: 'GET',
      success: function (res) {

        

        var data_11 = [];
        var data_22 = [];
        var data_33 = [];
        var data_44 = [];
        for (var i = 0; i < JSON.parse(res.data.data_monitor).index.length; i++) {
          data_11.push(
            [
              i,
              JSON.parse(res.data.data_monitor).data[i][0],

            ]
          );

          data_22.push(
            [
              i,
              JSON.parse(res.data.data_monitor).data[i][1],

            ]
          );

          data_33.push(
            [
              i,
              JSON.parse(res.data.data_monitor).data[i][2],

            ]
          );

         



        }

       

        app.globalData.data1_1 = data_11;
        app.globalData.data1_2 = data_22;
        app.globalData.data1_3 = data_33;
        app.globalData.data1_4 = data_44;

        //  console.log(app.globalData.data1_4);
      },

      fail: function (res) {

      },
      complete: function () { }
    })


    setTimeout(function(){
      wx.navigateTo({
        url: '../logs/logs?index=' + index + "&type=" + id + "&hao=" + hao,
        success: function (res) {

        },
        fail: function (res) {

        },
        complete: function (res) {

        },
      })
     },1000)


    // console.log(e.currentTarget.dataset.id);
    // wx.navigateTo({
    //   url: '../logs/logs?index=' + index + "&type=" + id,
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
      url: 'http://47.108.65.135:5100/keshe/api/v1/main/machine',//请求地址
      // data: {
      //   event_index: '1'
      // },
      header: {
        "Content-Type": "applciation/x-www-form-urlencoded"
      },
      method: 'GET',
      success: function (res) {
        console.log(JSON.parse(res.data.data).data);
        // console.log(JSON.parse(res.data.data).data);
        that.setData({
          newlist: JSON.parse(res.data.data).data,
          data11: JSON.parse(res.data.data).data
        })
        // console.log(JSON.parse(res.data.data).data[0][0])


      },

      fail: function (res) {

      },
      complete: function () { }
    })




    // wx.request({
    //   url: 'http://47.108.65.135:5100/keshe/api/v1/main/machine',//请求地址
    //   // data: {
    //   //   event_index: '1'
    //   // },
    //   header: {
    //     "Content-Type": "applciation/x-www-form-urlencoded"
    //   },
    //   method: 'GET',
    //   success: function (res) {
    //     // console.log(JSON.parse(res.data));
    //     // console.log(JSON.parse(res.data.data).data);
    //     that.setData({
    //       newlist: JSON.parse(res.data.data).index,
    //       data11: JSON.parse(res.data.data).data
    //     })
    //     // console.log(typeof that.data.data11[1][1])
        

    //   },

    //   fail: function (res) {

    //   },
    //   complete: function () { }
    // })





    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      })
    } else if (this.data.canIUse) {
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

})