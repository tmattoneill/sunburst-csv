<template>
  <div ref="chartContainer" style="width: 800px; height: 600px"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  data() {
    return {
      chart: null,
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const response = await fetch('http://127.0.0.1:5001/data'); // Fetch data from Flask API
        if (!response.ok) {
          const message = `An error has occurred: ${response.status} from backend`;
          throw new Error(message)
        }
        const data = await response.json();
        this.renderChart(data)
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
    renderChart(data) {
      const chartDom = this.$refs.chartContainer;
      this.chart = echarts.init(chartDom);

      const option = {
        series: {
          type: 'sunburst',
          data: [data],
          radius: [0, '100%'],
          label: {
            rotate: 'tangential',
            overflow: 'truncate',
            ellipsis: '...',
            fontSize: '12',
          },
        },
      };

      this.chart.setOption(option);
    },
  },
  beforeUnmount() {
    if(this.chart) {
      this.chart.dispose()
    }
  }
};
</script>