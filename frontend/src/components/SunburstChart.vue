<template>
  <div class="chart-wrapper">
    <div class="palette-selector">
      <select v-model="selectedPalette" @change="handlePaletteChange">
        <option v-for="name in paletteNames" :key="name" :value="name">
          {{ name }}
        </option>
      </select>
    </div>
    <div ref="chartContainer" style="width: 100%; height: calc(100% - 40px);"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { PALETTES } from '@/palettes';

export default {
  props: {
    chartData: {
      type: Object,
      required: true,
    },
    paletteName: {
      type: String,
      default: 'ocean'
    }
  },
  data() {
    return {
      chart: null,
      currentData: null,
      selectedPalette: this.paletteName,
      colors: PALETTES[this.paletteName] || PALETTES.ocean
    };
  },
  computed: {
    paletteNames() {
      return Object.keys(PALETTES);
    }
  },
  watch: {
    chartData: {
      handler: 'updateChart',
      deep: true,
    },
    paletteName: {
      immediate: true,
      handler(newPalette) {
        this.selectedPalette = newPalette;
        this.colors = PALETTES[newPalette] || PALETTES.ocean;
        if (this.chart) {
          this.updateChart();
        }
      }
    }
  },
  mounted() {
    this.currentData = this.chartData;
    this.renderChart();
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose();
    }
  },
  methods: {
    handlePaletteChange() {
      this.colors = PALETTES[this.selectedPalette];
      this.$emit('update:paletteName', this.selectedPalette);
      this.updateChart();
    },
    renderChart() {
      const chartDom = this.$refs.chartContainer;
      this.chart = echarts.init(chartDom);

      const getChildrenColors = (data, index) => {
        if (!data || !data.children) {
          return [];
        }

        return data.children.map((child, childIndex) => {
          const newIndex = (index + childIndex) % this.colors.length;
          return {
            ...child,
            itemStyle: { color: this.colors[newIndex] },
            children: getChildrenColors(child, newIndex)
          }
        })
      }

      const applyColorsToData = (data) => {
        if (data) {
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
          center: ['50%', '50%'],
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
      if (this.chart) {
        this.currentData = this.chartData;
        this.renderChart();
      }
    },
    handleChartClick(params) {
      if (params.data && params.data.children) {
        this.currentData = params.data;
        this.renderChart();
      }
    },
  },
};
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.palette-selector {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
}

.palette-selector select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
  background: white;
  font-size: 14px;
}
</style>