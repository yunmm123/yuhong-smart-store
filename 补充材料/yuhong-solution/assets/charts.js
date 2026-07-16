(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- Chart 1: Before vs After Comparison (including planned features) ---
  var chart1 = echarts.init(document.getElementById('chart-compare'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    legend: {
      data: ['方案落地前', '一期已实现', '二期规划目标'],
      top: 10,
      textStyle: { color: muted, fontSize: 13 }
    },
    grid: { left: '12%', right: '8%', top: 60, bottom: 40 },
    xAxis: {
      type: 'category',
      data: ['巡检效率', '问题闭环率', '客户转化率', '客户复购率', '紧急履约率', '决策响应周期'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11, interval: 0, rotate: 20 }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 12, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    series: [
      {
        name: '方案落地前',
        type: 'bar',
        data: [20, 30, 20, 15, 55, 15],
        itemStyle: { color: accent2 + '60', borderRadius: [4, 4, 0, 0] },
        barWidth: 22
      },
      {
        name: '一期已实现',
        type: 'bar',
        data: [95, 95, 65, 50, 55, 90],
        itemStyle: { color: accent, borderRadius: [4, 4, 0, 0] },
        barWidth: 22,
        label: {
          show: true,
          position: 'top',
          color: accent,
          fontSize: 10,
          formatter: '{c}%'
        }
      },
      {
        name: '二期规划目标',
        type: 'bar',
        data: [95, 95, 65, 50, 86, 95],
        itemStyle: { color: accent + '50', borderRadius: [4, 4, 0, 0], borderType: 'dashed' },
        barWidth: 22,
        label: {
          show: true,
          position: 'top',
          color: accent,
          fontSize: 10,
          formatter: function(params) {
            return params.value > 55 ? params.value + '%' : '';
          }
        }
      }
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart 2: Radar Chart - Capability Improvement ---
  var chart2 = echarts.init(document.getElementById('chart-radar'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: { appendToBody: true },
    legend: {
      data: ['传统模式', '一期已实现', '二期规划目标'],
      top: 10,
      textStyle: { color: muted, fontSize: 13 }
    },
    radar: {
      indicator: [
        { name: '巡检效率', max: 100 },
        { name: 'AI辅助能力', max: 100 },
        { name: '数据可见性', max: 100 },
        { name: '客户沉淀', max: 100 },
        { name: '流程自动化', max: 100 },
        { name: '渠道管控力', max: 100 }
      ],
      axisName: { color: ink, fontSize: 13 },
      splitArea: {
        areaStyle: { color: [bg2, '#fff'] }
      },
      splitLine: { lineStyle: { color: rule } },
      axisLine: { lineStyle: { color: rule } }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [20, 5, 15, 10, 5, 15],
          name: '传统模式',
          itemStyle: { color: accent2 },
          areaStyle: { color: accent2 + '30' },
          lineStyle: { color: accent2, width: 2 }
        },
        {
          value: [95, 90, 90, 85, 90, 60],
          name: '一期已实现',
          itemStyle: { color: accent },
          areaStyle: { color: accent + '30' },
          lineStyle: { color: accent, width: 2 }
        },
        {
          value: [95, 90, 95, 85, 95, 90],
          name: '二期规划目标',
          itemStyle: { color: accent + '80', type: 'dashed' },
          areaStyle: { color: accent + '10' },
          lineStyle: { color: accent + '80', width: 2, type: 'dashed' }
        }
      ]
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });
})();
