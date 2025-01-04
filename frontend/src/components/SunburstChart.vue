<template>
  <div ref="chartContainer" style="width: 100%; height: 100%;"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  props: {
    chartData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      chart: null,
    };
  },
  watch: {
    chartData: {
      handler: 'updateChart',
      deep: true,
    },
  },
  mounted() {
    this.renderChart();
  },
  beforeUnmount() {
    if(this.chart) {
      this.chart.dispose();
    }
  },
  methods: {
    renderChart() {
      const chartDom = this.$refs.chartContainer;
      this.chart = echarts.init(chartDom);

      const option = {
        series: {
          type: 'sunburst',
          data: [this.chartData],
          radius: [0, '95%'],
          label: {
            rotate: 'tangential',
            overflow: 'truncate',
            ellipsis: '...',
            fontSize: '11',
          },
        },
      };
      this.chart.setOption(option);
    },
    updateChart() {
      if (this.chart) {
        this.renderChart();
      }
    },
  },
};
</script>