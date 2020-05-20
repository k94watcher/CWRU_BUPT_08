// pages/test/test.js
import * as echarts from '../../ec-canvas/echarts';
var wxCharts = require('../../utils/wxcharts.js');
var app = getApp();
var daylineChart = null;
var yuelineChart1 = null;
var yuelineChart2 = null;

// function initChart(canvas, width, height, dpr) {
//   const chart = echarts.init(canvas, null, {
//     width: width,
//     height: height,
//     devicePixelRatio: dpr // new
//   });
//   canvas.setChart(chart);

//   var data = app.globalData.data_1;
//   var data2 = app.globalData.data_2;
//   var data3 = app.globalData.data_3;
//   var data4 = app.globalData.data_4;

//   // for (var i = 0; i < 10; i++) {
//   //   data.push(
//   //     [
//   //       Math.round(Math.random() * 100),
//   //       Math.round(Math.random() * 100),
//   //       Math.round(Math.random() * 40)
//   //     ]
//   //   );
//   //   data2.push(
//   //     [
//   //       Math.round(Math.random() * 100),
//   //       Math.round(Math.random() * 100),
//   //       Math.round(Math.random() * 100)
//   //     ]
//   //   );
//   // }

//   var axisCommon = {
//     axisLabel: {
//       textStyle: {
//         color: '#C8C8C8'
//       }
//     },
//     axisTick: {
//       lineStyle: {
//         color: '#fff'
//       }
//     },
//     axisLine: {
//       lineStyle: {
//         color: '#C8C8C8'
//       }
//     },
//     splitLine: {
//       lineStyle: {
//         color: '#C8C8C8',
//         type: 'solid'
//       }
//     }
//   };


//   var option = {

//     color: ["#FF7070", "#60B6E3","#ff6100","#C28F5C"],
//     backgroundColor: '#eee',
//     xAxis: axisCommon,
//     yAxis: axisCommon,
//     tooltip: {
//       trigger: 'axis',
//       axisPointer: {
//         show: true,
//         type: 'cross',
//         snap: true
//       }

//     },

//     legend: {
//       data: ['DE_time', 'FE_time', 'BA_time','RPM']
//     },
//     visualMap: {
//       show: false,
//       max: 100,
//       inRange: {
//         symbolSize: 5
//       }
//     },
//     series: [{
//       type: 'scatter',
//       name: 'DE_time',
//       data: data
//     },
//     {
//       name: 'FE_time',
//       type: 'scatter',
//       data: data2
//     },
//     {
//       name: 'BA_time',
//         type: 'scatter',
//         data: data3
//     },
//     {
//       name: 'RPM',
//         type: 'scatter',
//         data: data4
//     },
//     ],
//     animationDelay: function (idx) {
//       return idx * 50;
//     },
//     animationEasing: 'elasticOut'
//   };
//   chart.setOption(option);
//   return chart;
// }



Page({
  data: {
    
    featuremin:[],
    featuremax: [],
    feature_index: [],
    feature_data:[],
    hao11:[],
    index11: 1,
    type11:[],
    time11:[],
    data_1: [],
    data_2: [],
    data_3: [],
    data_4: [],
    logs: [],
    ec: {
      lazyload : true,
      onInit: initChart,

    },
  
  },



  textPaste1(){
    wx.showToast({
      title: '复制成功 到浏览器打开链接即可下载',
    })
    wx.setClipboardData({
      data: 'http://47.108.65.135:5100/keshe/api/v1/event/history/origin_data?event_index='+this.data.hao11,
      success: function (res) {
        wx.getClipboardData({    
          success: function (res) {
            console.log(res.data) // data
          }
        })
      }
    })
  },


  textPaste2(){
    wx.showToast({
      title: '复制成功 到浏览器打开链接即可下载',
    })
    wx.setClipboardData({
      data: 'http://47.108.65.135:5100/keshe/api/v1/event/history/feature_data?event_index=' + this.data.hao11,
      success: function (res) {
        wx.getClipboardData({    
          success: function (res) {
            console.log(res.data) // data
          }
        })
      }
    })
  },


  onShareAppMessage: function (res) {
    return {
      title: 'ECharts 可以在微信小程序中使用啦！',
      path: '/pages/logs/logs',
      success: function () { },
      fail: function () { }
    }
  },


  // getMothElectro: function () {
  //   var windowWidth = 320;
  //   try {
  //     var res = wx.getSystemInfoSync();
  //     windowWidth = res.windowWidth;
  //   } catch (e) {
  //     console.error('getSystemInfoSync failed!');
  //   }
  //   // yuelineChart1 = new wxCharts({ //当月用电折线图配置
  //   //   canvasId: 'yueEle',
  //   //   type: 'line',
  //   //   categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'], //categories X轴
  //   //   animation: true,
  //   //   // background: '#f5f5f5',
  //   //   series: [
  //   //   {
  //   //     name: '光伏供电量',
  //   //     data: [6, 4, 9, 7, 1, 4, 5, 1, 1, 8, 8, 6, 6, 2, 2, 2, 0, 5, 5, 8, 8, 8, 8, 9, 0, 4, 6, 9, 2, 1, 6],
  //   //     format: function (val, name) {
  //   //       return val.toFixed(2) + 'kWh';
  //   //     }
  //   //   },
  //   //   {
  //   //     name: '市电供电量',
  //   //     data: [0, 4, 3, 3, 1, 7, 7, 7, 9, 9, 3, 3, 0, 0, 5, 6, 0, 4, 1, 2, 0, 1, 3, 9, 2, 5, 1, 8, 3, 4, 2],
  //   //     format: function (val, name) {
  //   //       return val.toFixed(2) + 'kWh';
  //   //     }
  //   //   }],
  //   //   xAxis: {
  //   //     disableGrid: true
  //   //   },
  //   //   yAxis: {
  //   //     title: '当月用电(kWh)',
  //   //     format: function (val) {
  //   //       return val.toFixed(2);
  //   //     },
  //   //     max: 20,
  //   //     min: 0
  //   //   },
  //   //   width: windowWidth,
  //   //   height: 200,
  //   //   dataLabel: false,
  //   //   dataPointShape: true,
  //   //   extra: {
  //   //     lineStyle: 'straight'
  //   //   }
  //   // });
  //   yuelineChart2 = new wxCharts({ //当月用电折线图配置
  //     canvasId: 'yueEle2',
  //     type: 'line',
  //     categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'], //categories X轴
  //     animation: true,
  //     // background: '#f5f5f5',
  //     series: [{
  //       name: '总用电量',
  //       //data: yuesimulationData.data,
  //       data: [1, 6, 9, 1, 0, 2, 9, 2, 8, 6, 0, 9, 8, 0, 3, 7, 3, 9, 3, 8, 9, 5, 4, 1, 5, 8, 2, 4, 9, 8, 7],
  //       format: function (val, name) {
  //         return val.toFixed(2) + 'kWh';
  //       }
  //     }],
  //     xAxis: {
  //       disableGrid: true
  //     },
  //     yAxis: {
  //       title: '当月用电(kWh)',
  //       format: function (val) {
  //         return val.toFixed(2);
  //       },
  //       max: 20,
  //       min: 0
  //     },
  //     width: windowWidth,
  //     height: 200,
  //     dataLabel: false,
  //     dataPointShape: true,
  //     extra: {
  //       lineStyle: 'straight'
  //     }
  //   });
  // },
  // // yueTouchHandler1: function (e) { //当月用电触摸显示
  // //   console.log(yuelineChart1.getCurrentDataIndex(e));
  // //   yuelineChart1.showToolTip(e, { //showToolTip图表中展示数据详细内容
  // //     background: '#7cb5ec',
  // //     format: function (item, category) {
  // //       return category + '日 ' + item.name + ':' + item.data
  // //     }
  // //   });
  // // },
  // yueTouchHandler2: function (e) { //当月用电触摸显示
  //   console.log(yuelineChart2.getCurrentDataIndex(e));
  //   yuelineChart2.showToolTip(e, { //showToolTip图表中展示数据详细内容
  //     background: '#7cb5ec',
  //     format: function (item, category) {
  //       return category + '日 ' + item.name + ':' + item.data
  //     }
  //   });
  // },


  /**
   * 页面的初始数据
   */

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    


    console.log(options)
    let index=options.index;
    let time=options.time;
    let type = options.type;
    let hao=options.hao;
    // console.log(typeof index)
    this.setData({
      // detailData:list_data[index],
      index11:parseInt(index)+1,
      time11:time,
      type11:type,
      hao11:hao,
    });
    
    
    var that = this;
    wx.request({
      url: 'http://47.108.65.135:5100/keshe/api/v1/event/data',//请求地址
      data: {
        event_index: hao
      },
      header: {
        "Content-Type": "applciation/x-www-form-urlencoded"
      },
      method: 'GET',
      success: function (res) {
        
        console.log(JSON.parse(res.data.dataset).index.length)
       

        that.setData({
          feature_data: JSON.parse(res.data.featureset).data,
          feature_index: JSON.parse(res.data.featureset).index,
        })
       

        // var data_11 = [];
        // var data_22 = [];
        // var data_33 = [];
        // var data_44 = [];
        // for (var i = 0; i < 100; i++) {
        //   data_11.push(
        //     [
        //       i,
        //       JSON.parse(res.data.dataset).data[i][0],
              
        //     ]
        //   );

        //   data_22.push(
        //     [
        //       i,
        //       JSON.parse(res.data.dataset).data[i][1],

        //     ]
        //   );

        //   data_33.push(
        //     [
        //       i,
        //       JSON.parse(res.data.dataset).data[i][2],

        //     ]
        //   );

        //   data_44.push(
        //     [
        //       i,
        //       JSON.parse(res.data.dataset).data[i][3],

        //     ]
        //   );
          
          
          
        //   }


        
          var datamin =1000000000;
          var datamax=0;
        for (var i = 0; i < 100; i++){
          if (JSON.parse(res.data.featureset).data[i]>datamax)
          {
            datamax = JSON.parse(res.data.featureset).data[i]
          }
          if (JSON.parse(res.data.featureset).data[i] < datamin) {
            datamin = JSON.parse(res.data.featureset).data[i]
          }

        }
        // console.log(datamax)
        that.setData({

          featuremin:datamin,
          featuremax:datamax
        })
        
          
          // console.log(data_11);
        // that.setData({
          
        //   data_1: data_11,
        // })
          
        // app.globalData.data_1 = data_11;
        // app.globalData.data_2 = data_22;
        // app.globalData.data_3 = data_33;
        // app.globalData.data_4 = data_44;

      //  console.log(this.data.data_1);
      },

      fail: function (res) {

      },
      complete: function () { }
    })
    
    
    // this.getMothElectro();
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () { 

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },




  // getMothElectro: function () {
  //   console.log("app.globalData.feature_data")
  //   var windowWidth = 320;
  //   try {
  //     var res = wx.getSystemInfoSync();
  //     windowWidth = res.windowWidth;
  //   } catch (e) {
  //     console.error('getSystemInfoSync failed!');
  //   }



  //   // yuelineChart1 = new wxCharts({ //当月用电折线图配置
  //   //   canvasId: 'yueEle',
  //   //   type: 'line',
  //   //   categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'], //categories X轴
  //   //   animation: true,
  //   //   // background: '#f5f5f5',
  //   //   series: [
  //   //   {
  //   //     name: '光伏供电量',
  //   //     data: [6, 4, 9, 7, 1, 4, 5, 1, 1, 8, 8, 6, 6, 2, 2, 2, 0, 5, 5, 8, 8, 8, 8, 9, 0, 4, 6, 9, 2, 1, 6],
  //   //     format: function (val, name) {
  //   //       return val.toFixed(2) + 'kWh';
  //   //     }
  //   //   },
  //   //   {
  //   //     name: '市电供电量',
  //   //     data: [0, 4, 3, 3, 1, 7, 7, 7, 9, 9, 3, 3, 0, 0, 5, 6, 0, 4, 1, 2, 0, 1, 3, 9, 2, 5, 1, 8, 3, 4, 2],
  //   //     format: function (val, name) {
  //   //       return val.toFixed(2) + 'kWh';
  //   //     }
  //   //   }],
  //   //   xAxis: {
  //   //     disableGrid: true
  //   //   },
  //   //   yAxis: {
  //   //     title: '当月用电(kWh)',
  //   //     format: function (val) {
  //   //       return val.toFixed(2);
  //   //     },
  //   //     max: 20,
  //   //     min: 0
  //   //   },
  //   //   width: windowWidth,
  //   //   height: 200,
  //   //   dataLabel: false,
  //   //   dataPointShape: true,
  //   //   extra: {
  //   //     lineStyle: 'straight'
  //   //   }
  //   // });




  //   yuelineChart2 = new wxCharts({ //当月用电折线图配置
  //     canvasId: 'yueEle2',
  //     type: 'line',




  //     // categories:this.data.feature_index, //categories X轴
  //     // categories: ["DE_time_time_std", "DE_time_freq_iqr", "DE_time_freq_f5", "DE_time_freq_f7", "DE_time_freq_f8", "DE_time_ratio_cD3", "FE_time_time_std", "FE_time_freq_iqr", "FE_time_freq_f5", "FE_time_freq_f7", "FE_time_freq_f8", "FE_time_ratio_cD3", "BA_time_time_std", "BA_time_freq_iqr", "BA_time_freq_f5", "BA_time_freq_f7", "BA_time_freq_f8", "BA_time_ratio_cD3", "RPM_time_std", "RPM_freq_iqr", "RPM_freq_f5", "RPM_freq_f7", "RPM_freq_f8", "RPM_ratio_cD3"], 
     
     
     
     
  //     categories: app.globalData.feature_index,
  //     animation: true,
  //     // background: '#f5f5f5',
  //     series: [{
  //       name: '总用电量',
  //       //data: yuesimulationData.data,
  //       // data: that.data.feature_data,
  //       // data: app.globalData.feature_index,
  //       data: [6, 4, 9, 7, 1, 4, 5, 1, 1, 8, 8, 6, 6, 2, 2, 2, 0, 5, 5, 8, 8, 8, 8, 9, 0, 4, 6, 9, 2, 1],
  //       format: function (val, name) {
  //         return val.toFixed(2) + 'kWh';
  //       }
  //     }],
  //     xAxis: {
  //       disableGrid: true
  //     },
  //     yAxis: {
  //       title: '当月用电(kWh)',
  //       format: function (val) {
  //         return val.toFixed(2);
  //       },
  //       max: 20,
  //       min: 0
  //     },
  //     width: windowWidth,
  //     height: 200,
  //     dataLabel: false,
  //     dataPointShape: true,
  //     extra: {
  //       lineStyle: 'straight'
  //     }
  //   });
  // },





  // // yueTouchHandler1: function (e) { //当月用电触摸显示
  // //   console.log(yuelineChart1.getCurrentDataIndex(e));
  // //   yuelineChart1.showToolTip(e, { //showToolTip图表中展示数据详细内容
  // //     background: '#7cb5ec',
  // //     format: function (item, category) {
  // //       return category + '日 ' + item.name + ':' + item.data
  // //     }
  // //   });
  // // },





  // yueTouchHandler2: function (e) { //当月用电触摸显示
  //   console.log(yuelineChart2.getCurrentDataIndex(e));
  //   yuelineChart2.showToolTip(e, { //showToolTip图表中展示数据详细内容
  //     background: '#7cb5ec',
  //     format: function (item, category) {
  //       return category + '日 ' + item.name + ':' + item.data
  //     }
  //   });
  // },



})


function initChart(canvas, width, height, dpr) {
  const chart = echarts.init(canvas, null, {
    width: width,
    height: height,
    devicePixelRatio: dpr // new
  });
  canvas.setChart(chart);

  var data = app.globalData.data_1;
  var data2 = app.globalData.data_2;
  var data3 = app.globalData.data_3;
  // var data4 = app.globalData.data_4;

  // for (var i = 0; i < 10; i++) {
  //   data.push(
  //     [
  //       Math.round(Math.random() * 100),
  //       Math.round(Math.random() * 100),
  //       Math.round(Math.random() * 40)
  //     ]
  //   );
  //   data2.push(
  //     [
  //       Math.round(Math.random() * 100),
  //       Math.round(Math.random() * 100),
  //       Math.round(Math.random() * 100)
  //     ]
  //   );
  // }

  var axisCommon = {
    axisLabel: {
      textStyle: {
        color: '#C8C8C8'
      }
    },
    axisTick: {
      lineStyle: {
        color: '#fff'
      }
    },
    axisLine: {
      lineStyle: {
        color: '#C8C8C8'
      }
    },
    splitLine: {
      lineStyle: {
        color: '#C8C8C8',
        type: 'solid'
      }
    }
  };


  var option = {

    color: ["#FF7070", "#60B6E3", "#ff6100"],//, "#C28F5C"
    backgroundColor: '#eee',
    xAxis: axisCommon,
    yAxis: axisCommon,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        show: true,
        type: 'cross',
        snap: true
      }

    },

    legend: {
      data: ['DE_time', 'FE_time',  'RPM']
    },
    visualMap: {
      show: false,
      max: 100,
      inRange: {
        symbolSize: 5
      }
    },
    series: [{
      type: 'scatter',
      name: 'DE_time',
      data: data
    },
    {
      name: 'FE_time',
      type: 'scatter',
      data: data2
    },
    {
      name: 'RPM',
      type: 'scatter',
      data: data3
    },
    // {
    //   name: 'RPM',
    //   type: 'scatter',
    //   data: data4
    // },
    ],
    animationDelay: function (idx) {
      return idx * 50;
    },
    animationEasing: 'elasticOut'
  };
  chart.setOption(option);
  return chart;
}