<!-- SunburstChart.vue -->
<script setup>
import { ref, watch, onMounted, onBeforeUnmount, defineProps, defineEmits } from 'vue'
import * as echarts from 'echarts'
import { PALETTES } from '@/palettes'

// Props
const props = defineProps({
  chartData: {
    type: Object,
    required: true,
  },
  paletteName: {
    type: String,
    default: 'ocean'
  }
})

// Emits
const emit = defineEmits(['update:paletteName', 'node-click', 'node-hover', 'path-change'])

// Refs
const chart = ref(null)
const currentData = ref(null)
const selectedPalette = ref(props.paletteName)
const chartContainer = ref(null)
const colors = ref(PALETTES[props.paletteName] || PALETTES.Ocean)

watch(() => props.paletteName, (newPalette) => {
  colors.value = PALETTES[newPalette] || PALETTES.Ocean;
  if (chart.value) {
    updateChart();
  }
}, { immediate: true });

const handleChartHover = (params) => {
  if (params.data) {
    emit('node-hover', params.data)
  }
}

const handleChartMouseOut = () => {
  emit('node-hover', null);
}

const getChildrenColors = (data, index) => {
  if (!data || !data.children) {
    return []
  }

  return data.children.map((child, childIndex) => {
    const newIndex = (index + childIndex) % colors.value.length
    return {
      ...child,
      itemStyle: { color: colors.value[newIndex] },
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

// Add fullPath ref to track complete path
const fullPath = ref([{ name: props.chartData.name }]);

const handleChartClick = (params) => {
  if (params.data) {
    emit('node-click', params.data);

    console.log('Click params:', params);
    console.log('Full treePathInfo:', params.treePathInfo);
    console.log('TreePathInfo names:', params.treePathInfo.map(node => node.name));

    // Get new nodes from current click (skip empty names)
    const newNodes = params.treePathInfo
      .filter(node => node.name)
      .map(node => ({
        name: node.name
      }));

    // If clicking deeper in the tree, add to path
    if (newNodes.length > 0) {
      const clickedNodeName = params.data.name;
      // Only add the clicked node if it's not already the last item in our path
      if (fullPath.value[fullPath.value.length - 1]?.name !== clickedNodeName) {
        fullPath.value.push({ name: clickedNodeName });
      }
    }

    console.log('Full path being emitted:', fullPath.value);
    console.log('Path names:', fullPath.value.map(node => node.name));

    emit('path-change', fullPath.value);

    if (params.data.children) {
      currentData.value = params.data;
      renderChart();
    }
  }
}

const renderChart = () => {
  if (!chartContainer.value) return

  if (chart.value) {
    chart.value.dispose();  // Clean up existing chart
  }

  chart.value = echarts.init(chartContainer.value)

  const option = {
    series: {
      type: 'sunburst',
      data: [applyColorsToData(currentData.value)],
      radius: ['0%', '100%'],
      center: ['50%', '50%'],
      levels: [{
        r0: '0%',
        r: '15%',
        itemStyle: {
          color: 'none',
          borderWidth: 0
        },
        label: {
          show: true,
          position: 'center',
          fontSize: 14,
          formatter: (params) => {
            return params.treePathInfo.length === 1 ? params.data.name : ''
          }
        }
      }],
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: false
        }
      }
    },
  }

  chart.value.setOption(option)
  chart.value.on('click', handleChartClick)
  chart.value.on('mouseover', handleChartHover)
  chart.value.on('mouseout', handleChartMouseOut);
}

const updateChart = () => {
  if (chart.value) {
    currentData.value = props.chartData
    renderChart()
  }
}

// Watchers
watch(() => props.chartData, () => {
  currentData.value = props.chartData;
  // Reset path to just root node when chart data changes
  fullPath.value = [{ name: props.chartData.name }];
  updateChart();
  emit('path-change', fullPath.value);
}, { deep: true })

watch(() => props.paletteName, (newPalette) => {
  selectedPalette.value = newPalette
  colors.value = PALETTES[newPalette] || PALETTES.Ocean
  if (chart.value) {
    updateChart()
  }
}, { immediate: true })

// Lifecycle hooks
onMounted(() => {
  currentData.value = props.chartData
  renderChart()
  // Initialize with root path
  emit('path-change', [{ name: props.chartData.name }])
})

onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.dispose()
  }
})
</script>

<template>
  <div class="chart-section">
    <div class="row g-0">
      <div class="col-12">
        <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-section {
  width: 100%;
}

.form-select-sm {
  font-size: 0.875rem;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
</style>