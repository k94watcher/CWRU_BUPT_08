//logs.js
var wxCharts = require('../../utils/wxcharts.js');
import * as echarts from '../../ec-canvas/echarts';
const app = getApp();
var daylineChart = null;
var yuelineChart1 = null;
var yuelineChart2 = null;
var yuelineChart3 = null;


// function initChart(canvas, width, height, dpr) {
//   const chart = echarts.init(canvas, null, {
//     width: width,
//     height: height,
//     devicePixelRatio: dpr // new
//   });
//   canvas.setChart(chart);

//   var data = app.globalData.data1_1;
//   var data2 = app.globalData.data1_2;
//   var data3 = app.globalData.data1_3;
//   // var data4 = app.globalData.data1_4;

//   // for (var i = 0; i < 100; i++) {
//   //   data.push(
//   //     [
//   //       Math.round(Math.random() * 100),
//   //       Math.round(Math.random() * 100),
//   //       1
//   //     ]
//   //   );
//   //   data2.push(
//   //     [
//   //       Math.round(Math.random() * 100),
//   //       Math.round(Math.random() * 100),
//   //       1
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

//     color: ["#FF7070", "#60B6E3", "#ff6100"],   //, "#C28F5C"
//     backgroundColor: '#eee',
//     xAxis: axisCommon,
//     yAxis: axisCommon,
//     tooltip: {
//       trigger:'axis',
//       axisPointer: {
//         show: true,
//         type: 'cross',
//         snap: true
//       }
      
//     },

//     legend: {
//       data: ['DE_time', 'FE_time',  'RPM']
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
//       name: 'RPM',
//       type: 'scatter',
//       data: data3
//     },
//     // {
//     //   name: 'RPM',
//     //   type: 'scatter',
//     //   data: data4
//     // },
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



  textPaste1(){
    wx.showToast({
      title: '复制成功 到浏览器打开链接即可下载',
    })
    wx.setClipboardData({
      data: 'http://47.108.65.135:5100/keshe/api/v1/machine/history/origin_data?machine_seq='+this.data.hao,
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
      data: 'http://47.108.65.135:5100/keshe/api/v1/machine/history/feature_data?machine_seq=' + this.data.hao,
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
  data: {
    featuremin: [],
    featuremax: [],
    feature_columns:[],
    feature_data:[],
    hao:[],
    index111:[],
    type111:[],
    logs: [],
     ec: {
      onInit: initChart
    }
  },

  onLoad: function (e) {
    let that =this
    let index=e.index
    let type=e.type
    let hao1=e.hao
    // console.log(JSON.parse(e.index))
    // console.log(type111)
    // console.log(hao)

    that.setData({
      // detailData:list_data[index],
      index111: parseInt(index) + 1,
      
      type111: type,

      hao:hao1
      
    });


  // console.log(type)


    
    wx.request({
      url: 'http://47.108.65.135:5100/keshe/api/v1/machine/data',//请求地址
      data: {
        machine_seq:that.data.hao
      },
      header: {
        "Content-Type": "applciation/x-www-form-urlencoded"
      },
      method: 'GET',
      success: function (res) {

        // console.log(res);
        
        // console.log(JSON.parse(res.data.data_monitor).index.length);


        that.setData({
          feature_columns: JSON.parse(res.data.data_feature).columns,
          feature_data: JSON.parse(res.data.data_feature).data,
        })
       

        // that.setData({
        //   feature_data: JSON.parse(res.data.featureset).data,
        //   feature_index: JSON.parse(res.data.featureset).index,
        // })
        // console.log(that.data.feature_index)
        // app.globalData.feature_data = JSON.parse(res.data.featureset).data;
        // app.globalData.feature_index = JSON.parse(res.data.featureset).index;


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

          data_44.push(
            [
              i,
              JSON.parse(res.data.data_monitor).data[i][3],

            ]
          );



        }
        
        var datamin = 1000000000;
        var datamax = 0;
        for (var i = 0; i < 96; i++) {
          if (JSON.parse(res.data.data_feature).data[0][i] > datamax) {
            datamax = JSON.parse(res.data.data_feature).data[0][i]
          }
          if (JSON.parse(res.data.data_feature).data[0][i] < datamin) {
            datamin = JSON.parse(res.data.data_feature).data[0][i]
          }

        }
        // console.log(datamin)
        that.setData({

          featuremin: datamin,
          featuremax: datamax
        })


        // console.log(data_44);
        // that.setData({

        //   data_1: data_11,
        // })

        // app.globalData.data1_1 = data_11;
        // app.globalData.data1_2 = data_22;
        // app.globalData.data1_3 = data_33;
        // app.globalData.data1_4 = data_44;

        //  console.log(app.globalData.data1_4);
      },

      fail: function (res) {

      },
      complete: function () { }
    })


  

    // this.getMothElectro();//加载当月用电
  },

  onReady() {
  },

  getMothElectro: function () {
    var windowWidth = 320;
    try {
      var res = wx.getSystemInfoSync();
      windowWidth = res.windowWidth;
    } catch (e) {
      console.error('getSystemInfoSync failed!');
    }
    // yuelineChart1 = new wxCharts({ //当月用电折线图配置
    //   canvasId: 'yueEle',
    //   type: 'line',
    //   categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'], //categories X轴
    //   animation: true,
    //   // background: '#f5f5f5',
    //   series: [{
    //     name: '总用电量',
    //     //data: yuesimulationData.data,
    //     data: [1, 6, 9, 1, 0, 2, 9, 2, 8, 6, 0, 9, 8, 0, 3, 7, 3, 9, 3, 8, 9, 5, 4, 1, 5, 8, 2, 4, 9, 8, 7],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   }, {
    //     name: '电池供电量',
    //     data: [0, 6, 2, 2, 7, 6, 2, 5, 8, 1, 8, 4, 0, 9, 7, 2, 5, 2, 8, 2, 5, 2, 9, 4, 4, 9, 8, 5, 5, 5, 6],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   },
    //   {
    //     name: '光伏供电量',
    //     data: [6, 4, 9, 7, 1, 4, 5, 1, 1, 8, 8, 6, 6, 2, 2, 2, 0, 5, 5, 8, 8, 8, 8, 9, 0, 4, 6, 9, 2, 1, 6],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   },
    //   {
    //     name: '市电供电量',
    //     data: [0, 4, 3, 3, 1, 7, 7, 7, 9, 9, 3, 3, 0, 0, 5, 6, 0, 4, 1, 2, 0, 1, 3, 9, 2, 5, 1, 8, 3, 4, 2],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   }],
    //   xAxis: {
    //     disableGrid: true
    //   },
    //   yAxis: {
    //     title: '当月用电(kWh)',
    //     format: function (val) {
    //       return val.toFixed(2);
    //     },
    //     max: 20,
    //     min: 0
    //   },
    //   width: windowWidth,
    //   height: 200,
    //   dataLabel: false,
    //   dataPointShape: true,
    //   extra: {
    //     lineStyle: 'straight'
    //   }
    // });

    // yuelineChart2 = new wxCharts({ //当月用电折线图配置
    //   canvasId: 'yueEle2',
    //   type: 'line',
    //   categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'], //categories X轴
    //   animation: true,
    //   // background: '#f5f5f5',
    //   series: [{
    //     name: '总用电量',
    //     //data: yuesimulationData.data,
    //     data: [1, 6, 9, 1, 0, 2, 9, 2, 8, 6, 0, 9, 8, 0, 3, 7, 3, 9, 3, 8, 9, 5, 4, 1, 5, 8, 2, 4, 9, 8, 7],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   }, {
    //     name: '电池供电量',
    //     data: [0, 6, 2, 2, 7, 6, 2, 5, 8, 1, 8, 4, 0, 9, 7, 2, 5, 2, 8, 2, 5, 2, 9, 4, 4, 9, 8, 5, 5, 5, 6],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   },
    //   {
    //     name: '光伏供电量',
    //     data: [6, 4, 9, 7, 1, 4, 5, 1, 1, 8, 8, 6, 6, 2, 2, 2, 0, 5, 5, 8, 8, 8, 8, 9, 0, 4, 6, 9, 2, 1, 6],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   },
    //   {
    //     name: '市电供电量',
    //     data: [0, 4, 3, 3, 1, 7, 7, 7, 9, 9, 3, 3, 0, 0, 5, 6, 0, 4, 1, 2, 0, 1, 3, 9, 2, 5, 1, 8, 3, 4, 2],
    //     format: function (val, name) {
    //       return val.toFixed(2) + 'kWh';
    //     }
    //   }],
    //   xAxis: {
    //     disableGrid: true
    //   },
    //   yAxis: {
    //     title: '当月用电(kWh)',
    //     format: function (val) {
    //       return val.toFixed(2);
    //     },
    //     max: 20,
    //     min: 0
    //   },
    //   width: windowWidth,
    //   height: 200,
    //   dataLabel: false,
    //   dataPointShape: true,
    //   extra: {
    //     lineStyle: 'straight'
    //   }
    // });

  //   yuelineChart3 = new wxCharts({ //当月用电折线图配置
  //     canvasId: 'yueEle3',
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
  //     }, {
  //       name: '电池供电量',
  //       data: [0, 6, 2, 2, 7, 6, 2, 5, 8, 1, 8, 4, 0, 9, 7, 2, 5, 2, 8, 2, 5, 2, 9, 4, 4, 9, 8, 5, 5, 5, 6],
  //       format: function (val, name) {
  //         return val.toFixed(2) + 'kWh';
  //       }
  //     },
  //     {
  //       name: '光伏供电量',
  //       data: [6, 4, 9, 7, 1, 4, 5, 1, 1, 8, 8, 6, 6, 2, 2, 2, 0, 5, 5, 8, 8, 8, 8, 9, 0, 4, 6, 9, 2, 1, 6],
  //       format: function (val, name) {
  //         return val.toFixed(2) + 'kWh';
  //       }
  //     },
  //     {
  //       name: '市电供电量',
  //       data: [0, 4, 3, 3, 1, 7, 7, 7, 9, 9, 3, 3, 0, 0, 5, 6, 0, 4, 1, 2, 0, 1, 3, 9, 2, 5, 1, 8, 3, 4, 2],
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


  // yueTouchHandler1: function (e) { //当月用电触摸显示
  //   console.log(yuelineChart1.getCurrentDataIndex(e));
   
  //   yuelineChart1.showToolTip(e, { //showToolTip图表中展示数据详细内容
  //     background: '#7cb5ec',
  //     format: function (item, category) {
  //       return category + '日 ' + item.name + ':' + item.data
  //     }
  //   });
  // },

  // // yueTouchHandler2: function (e) { //当月用电触摸显示
  // //   console.log(yuelineChart2.getCurrentDataIndex(e));
  // //   yuelineChart2.showToolTip(e, { //showToolTip图表中展示数据详细内容
  // //     background: '#7cb5ec',
  // //     format: function (item, category) {
  // //       return category + '日 ' + item.name + ':' + item.data
  // //     }
  // //   });
  // // }, 
  
  // yueTouchHandler3: function (e) { //当月用电触摸显示
  //   console.log(yuelineChart3.getCurrentDataIndex(e));
  //   yuelineChart3.showToolTip(e, { //showToolTip图表中展示数据详细内容
  //     background: '#7cb5ec',
  //     format: function (item, category) {
  //       return category + '日 ' + item.name + ':' + item.data
  //     }
  //   });
  },



  // onLoad: function (e) {


  //   this.getMothElectro();//加载当月用电
  // },
  onReady() {
  }

});



function initChart(canvas, width, height, dpr) {
  const chart = echarts.init(canvas, null, {
    width: width,
    height: height,
    devicePixelRatio: dpr // new
  });
  canvas.setChart(chart);

  var data = app.globalData.data1_1;
  var data2 = app.globalData.data1_2;
  var data3 = app.globalData.data1_3;
  // var data4 = app.globalData.data1_4;

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

    color: ["#FF7070", "#60B6E3", "#ff6100"],   //, "#C28F5C"
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
      data: ['DE_time', 'FE_time', 'RPM']
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


