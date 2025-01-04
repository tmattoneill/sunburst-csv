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
      currentData: null,
    };
  },
  watch: {
    chartData: {
      handler: 'updateChart',
      deep: true,
    },
  },
  mounted() {
    this.currentData = this.chartData;
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

      const colors = [
        '#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#023e8a',
        '#0096c7', '#48cae4', '#ade8f4', '#caf0f8', '#014f86'
      ];
      const getChildrenColors = (data, index) => {
        if (!data || !data.children) {
          return [];
        }

        return data.children.map((child, childIndex) => {
              const newIndex = (index + childIndex)% colors.length;
              return {
                ...child,
                itemStyle: {color: colors[newIndex]},
                children: getChildrenColors(child, newIndex)
              }

            }
        )
      }

      const applyColorsToData = (data) => {
        if(data) {
          return {
            ...data,
            children: getChildrenColors(data, 0)
          }
        }

        return data
      }


      const option = {
        series: {
          type: 'sunburst',
          data: [applyColorsToData(this.currentData)],
          radius: ['10%', '100%'],
          center:['50%', '50%'],
          label: {
            show: false,
            rotate: 'tangential',
            overflow: 'truncate',
            ellipsis: '...',
            fontSize: '11',
            formatter: (params) => {
              return params.data.name + (params.data.value ? `: ${params.data.value}` : "");
            }
          },
          emphasis: {
            focus: 'ancestor',
            label: {
              show: true,
            }
          }
        },
      };
      this.chart.setOption(option);

      this.chart.on('click', (params) => {
        this.handleChartClick(params);
      });
    },
    updateChart() {
      if(this.chart) {
        this.currentData = this.chartData;
        this.renderChart();
      }
    },
    handleChartClick(params) {
      if (params.data && params.data.children) {
        this.currentData = params.data;
        this.renderChart()
      }
    },
  },
};
</script>