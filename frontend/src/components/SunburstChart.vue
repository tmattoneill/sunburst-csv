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

// Path tracking
const nodeMap = ref(new Map())
const pathMap = ref(new Map())
let nextId = 1

// Helper to generate unique IDs
const generateNodeId = () => `node_${nextId++}`

// Helper to build node maps and paths
const buildNodeMaps = (node, parentPath = []) => {
  const nodeId = generateNodeId()

  // Store node with its ID
  nodeMap.value.set(nodeId, {
    id: nodeId,
    name: node.name,
    data: node
  })

  // Store complete path to this node
  const currentPath = [...parentPath, { id: nodeId, name: node.name }]
  pathMap.value.set(nodeId, currentPath)

  // Process children recursively
  if (node.children) {
    node.children.forEach(child => {
      const childInfo = buildNodeMaps(child, currentPath)
      // Add nodeId to the original data for reference
      child.nodeId = childInfo.nodeId
    })
  }

  // Add nodeId to the original data for reference
  node.nodeId = nodeId
  return { nodeId, path: currentPath }
}

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

const handleChartClick = (params) => {
  if (params.data && params.data.nodeId) {
    emit('node-click', params.data);

    // Get complete path from pathMap
    const path = pathMap.value.get(params.data.nodeId);
    console.log('Complete path for node:', path);

    emit('path-change', path);

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
  // Reset and rebuild maps
  nodeMap.value = new Map();
  pathMap.value = new Map();
  nextId = 1;

  const { path } = buildNodeMaps(props.chartData);

  currentData.value = props.chartData;
  updateChart();
  emit('path-change', path);
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
  // Initialize maps
  nodeMap.value = new Map();
  pathMap.value = new Map();
  nextId = 1;

  // Build initial maps from root data
  const { path } = buildNodeMaps(props.chartData);

  currentData.value = props.chartData;
  renderChart();
  emit('path-change', path);
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